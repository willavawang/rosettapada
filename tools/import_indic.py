"""Extract only selected ancient verse texts from a locally saved comparative edition.

Usage: python3 tools/import_indic.py INPUT_DIRECTORY OUTPUT_DIRECTORY
No network calls. Modern commentary and unselected parallel works are not copied.
"""
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json
import re
import sys

CHAPTERS = ["CD-01-Yamaka.htm", "CD-02-Appamada.htm", "CD-03-Citta.htm"]
BASE = "https://ancient-buddhist-texts.net/Buddhist-Texts/C3-Comparative-Dhammapada/"
NAMES = {"pd": ("Patna", "patna.json"), "ga": ("Gāndhārī", "gandhari.json"), "sa": ("Udānavarga", "sanskrit.json")}


class Extractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.verse = None
        self.cell = None
        self.depth = 0
        self.kind = None
        self.active_marks = []
        self.records = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and re.fullmatch(r"CD_\d+", attrs.get("id", "")):
            self.verse = int(attrs["id"].split("_")[1])
        if tag == "div":
            if self.cell is not None:
                self.depth += 1
            elif "cell1" in attrs.get("class", "").split():
                self.cell = {"pali": self.verse, "heading": "", "lines": [""], "annotations": []}
                self.depth = 1
        if self.cell is None:
            return
        if tag == "p":
            heading = "Heading6" in attrs.get("class", "").split()
            if heading and self.cell["heading"] and any(line.strip() for line in self.cell["lines"]):
                # Some cells contain two distinct parallels, each with its own heading.
                self.finish_record()
                self.cell = {"pali": self.verse, "heading": "", "lines": [""], "annotations": []}
            self.kind = "heading" if heading else "body"
        elif tag == "br" and self.kind == "body":
            self.cell["lines"].append("")
        elif tag in {"i", "em", "s", "ins"}:
            self.active_marks.append(tag)

    def handle_data(self, data):
        if self.cell is None:
            return
        if self.kind == "heading":
            self.cell["heading"] += data
        elif self.kind == "body":
            self.cell["lines"][-1] += data
            for mark in self.active_marks:
                if data.strip():
                    self.cell["annotations"].append({"line": len(self.cell["lines"]) - 1, "kind": mark, "text": data.strip()})

    def handle_endtag(self, tag):
        if self.cell is None:
            return
        if tag in self.active_marks:
            self.active_marks.remove(tag)
        if tag == "p":
            if self.kind == "body" and self.cell["lines"][-1].strip():
                self.cell["lines"].append("")
            self.kind = None
        elif tag == "div":
            self.depth -= 1
            if not self.depth:
                self.finish_record()
                self.cell, self.kind, self.active_marks = None, None, []

    def finish_record(self):
        self.cell["heading"] = " ".join(self.cell["heading"].split())
        self.cell["lines"] = [" ".join(line.split()) for line in self.cell["lines"] if line.strip()]
        self.records.append(self.cell)


def main():
    source_dir, output_dir = map(Path, sys.argv[1:3])
    output_dir.mkdir(parents=True, exist_ok=True)
    all_records, sources = [], []
    for name in CHAPTERS:
        raw = (source_dir / name).read_bytes()
        parser = Extractor()
        parser.feed(raw.decode("utf-8"))
        source_id = name.removesuffix(".htm")
        all_records.extend({**record, "source_id": source_id} for record in parser.records)
        sources.append({"id": source_id, "title": "Ānandajoti Bhikkhu, A Comparative Edition of the Dhammapada, fourth revised edition (2020)", "url": BASE + name, "retrieved": "2026-10-23", "html_sha256": hashlib.sha256(raw).hexdigest(), "license": "Ancient verse text; compilation attribution Ānandajoti Bhikkhu. Modern critical editions have separate rights notices; no blanket license is asserted.", "rights_url": "https://ancient-buddhist-texts.net/Miscellaneous/Copyright-Notice.htm"})
    for key, (prefix, filename) in NAMES.items():
        verses = []
        for number in range(1, 44):
            cells = [r for r in all_records if r["pali"] == number and r["heading"].startswith(prefix)]
            readings = [{"reference": r["heading"], "source_id": r["source_id"], "source_url": BASE + r["source_id"] + f'.htm#CD_{number}', "lines": r["lines"], "annotations": r["annotations"]} for r in cells if r["lines"]]
            for reading in readings:
                reading["fragmentary"] = any(re.search(r"\.\s*\.", line) for line in reading["lines"])
                reading["partial_correspondence"] = any(a["kind"] == "s" for a in reading["annotations"])
            partial = any(r["fragmentary"] or r["partial_correspondence"] for r in readings)
            if key == "ga" and number == 27 and len(readings) == 2:
                readings[1]["preferred"] = True
                readings[1]["note"] = "Partial parallel: this reading preserves the concluding happiness line. Both listed Gāndhārī parallels are retained in the source notes."
            verses.append({"pali": number, "status": "partial" if readings and partial else "present" if readings else "not-located", "readings": readings, **({"note": "No parallel is listed in the consulted comparative edition; this is not a claim of absence from the whole tradition."} if not readings else {})})
        result = {"tradition": key, "sources": sources, "verses": verses}
        (output_dir / filename).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(filename, {status: sum(v["status"] == status for v in verses) for status in ["present", "partial", "not-located"]})


if __name__ == "__main__":
    main()

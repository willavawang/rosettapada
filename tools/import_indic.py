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

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_FILES = {
    1: "CD-01-Yamaka.htm", 2: "CD-02-Appamada.htm", 3: "CD-03-Citta.htm",
    8: "CD-08-Sahassa.htm", 12: "CD-12-Atta.htm", 17: "CD-17-Kodha.htm",
    21: "CD-21-Pakinnaka.htm",
}
CHAPTERS = list(CHAPTER_FILES.values())
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


class PatnaVerse(HTMLParser):
    """Read the ancient text only, omitting metre scans and modern tooltip notes."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ignored = []
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.ignored:
            if tag not in {"br", "hr", "img", "meta", "link", "input"}:
                self.ignored.append(tag)
        elif tag == "metre" or tag == "span" and "TT" in attrs.get("class", "").split():
            self.ignored.append(tag)
        elif tag in {"p", "br"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if self.ignored:
            if tag in self.ignored:
                # Some old tooltip HTML omits a closing inline tag. Closing an
                # enclosing ignored span must not swallow the verse's tail.
                index = len(self.ignored) - 1 - self.ignored[::-1].index(tag)
                del self.ignored[index:]
        elif tag == "p":
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.ignored:
            self.parts.append(data)


def main():
    source_dir, output_dir = map(Path, sys.argv[1:3])
    output_dir.mkdir(parents=True, exist_ok=True)
    collection = json.loads((ROOT / "data/chapters.json").read_text())
    chapters = collection["chapters"]
    numbers = [n for chapter in chapters for n in range(chapter["start"], chapter["end"] + 1)]
    assert numbers == sorted(set(numbers)), "Chapter selection must be ordered and non-overlapping."
    all_records, sources = [], []
    for chapter in chapters:
        name = CHAPTER_FILES[chapter["no"]]
        path = source_dir / name
        if not path.exists():
            path = source_dir / f'indic-{chapter["no"]:02d}.html'
        raw = path.read_bytes()
        parser = Extractor()
        parser.feed(raw.decode("utf-8"))
        source_id = name.removesuffix(".htm")
        all_records.extend({**record, "source_id": source_id} for record in parser.records)
        sources.append({"id": source_id, "title": "Ānandajoti Bhikkhu, A Comparative Edition of the Dhammapada, fourth revised edition (2020)", "url": BASE + name, "retrieved": "2026-10-23" if chapter["no"] <= 3 else "2026-10-24", "html_sha256": hashlib.sha256(raw).hexdigest(), "license": "Ancient verse text; compilation attribution Ānandajoti Bhikkhu. Modern critical editions have separate rights notices; no blanket license is asserted.", "rights_url": "https://ancient-buddhist-texts.net/Miscellaneous/Copyright-Notice.htm"})
    selected_dir = output_dir / "sources/indic"
    selected_dir.mkdir(parents=True, exist_ok=True)
    corrections = json.loads((ROOT / "data/witnesses/sources/indic/corrections.json").read_text())
    patna_correction = next(c for c in corrections["corrections"] if c["pali"] == 158)
    primary_source = None
    if 158 in numbers:
        primary_raw = (source_dir / "17-Atta.htm").read_bytes()
        assert hashlib.sha256(primary_raw).hexdigest() == patna_correction["primary_html_sha256"], "Patna primary source changed; review the correction."
        block = re.search(r'<a id="PDhp_317".*?<div class="bold">(.*?)</div>', primary_raw.decode("utf-8"), re.S).group(1)
        parser = PatnaVerse()
        parser.feed(block)
        primary_lines = [" ".join(line.split()) for line in re.split(r"\n|\u2003", "".join(parser.parts)) if line.strip()]
        assert primary_lines == patna_correction["replacement_lines"], "Patna correction differs from the primary text."
        primary_source = {"id": "PDhp-17-Atta", "title": "Margaret Cone, Patna Dharmapada (1989), chapter 17; digital edition with Pāli parallels by Ānandajoti Bhikkhu (2007)", "url": patna_correction["primary_source_url"].split("#")[0], "retrieved": "2026-10-24", "html_sha256": patna_correction["primary_html_sha256"], "license": "Ancient verse text; Margaret Cone's critical edition reproduced with permission of the Pali Text Society. No blanket license is asserted.", "rights_url": "https://ancient-buddhist-texts.net/Buddhist-Texts/C5-Patna/index.htm"}
    retained = []
    for key, (prefix, filename) in NAMES.items():
        verses = []
        for number in numbers:
            # The source occasionally spells the final i of Gāndhārī short.
            cells = [r for r in all_records if r["pali"] == number and r["heading"].startswith("Gāndhār" if key == "ga" else prefix)]
            readings = [{"reference": r["heading"], "source_id": r["source_id"], "source_url": BASE + r["source_id"] + f'.htm#CD_{number}', "lines": r["lines"], "annotations": r["annotations"]} for r in cells if r["lines"]]
            retained.append({"tradition": key, "pali": number, "readings": json.loads(json.dumps(readings))})
            for reading in readings:
                reading["fragmentary"] = any(re.search(r"\.\s*\.|(^|\s)\.(?=\s|$)", line) for line in reading["lines"])
                reading["partial_correspondence"] = any(a["kind"] == "s" for a in reading["annotations"])
            if key == "pd" and number == 158:
                assert readings[0]["lines"] == patna_correction["comparative_lines"], "Comparative source changed; review the Patna correction."
                readings[0].update({"source_id": "PDhp-17-Atta", "source_url": patna_correction["primary_source_url"], "lines": patna_correction["replacement_lines"], "annotations": [], "note": patna_correction["display_note"]})
            if key == "pd":
                for difference in corrections.get("edition_differences", []):
                    if difference["pali"] == number:
                        assert readings[0]["reference"] == difference["reference"]
                        readings[0]["note"] = difference["display_note"]
            partial = any(r["fragmentary"] or r["partial_correspondence"] for r in readings)
            if key == "ga" and number == 27 and len(readings) == 2:
                readings[1]["preferred"] = True
                readings[1]["note"] = "Partial parallel: this reading preserves the concluding happiness line. Both listed Gāndhārī parallels are retained in the source notes."
            if key == "ga" and number == 106 and len(readings) == 2:
                readings[1]["preferred"] = True
                readings[1]["note"] = "The source lists two distinct Gāndhārī stanzas that parallel different portions of Pāli 106. The sheet displays the stanza about honoring a developed person for a moment; the monthly-sacrifice stanza remains separately recorded. They are not combined into an invented verse."
            verses.append({"pali": number, "status": "partial" if readings and partial else "present" if readings else "not-located", "readings": readings, **({"note": "No parallel is listed in the consulted comparative edition; this is not a claim of absence from the whole tradition."} if not readings else {})})
        result = {"tradition": key, "sources": sources + ([primary_source] if key == "pd" and primary_source else []), "verses": verses}
        (output_dir / filename).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(filename, {status: sum(v["status"] == status for v in verses) for status in ["present", "partial", "not-located"]})
    passages = {"scope": "Ancient Indic passages used for the six-chapter pilot and preserved Mind page; no modern commentary or unselected works.", "sources": sources, "verses": retained, "primary_corrections": [patna_correction] if 158 in numbers else []}
    (selected_dir / "selected-source-passages.json").write_text(json.dumps(passages, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()

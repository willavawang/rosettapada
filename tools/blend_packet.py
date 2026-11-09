"""Write the source packet for one chapter of the Rosettapada Blend.

The packet holds only original-language texts and their source metadata, so a
blend reading can be made without seeing any of the site's English.

    python3 tools/blend_packet.py 1 > packet.json
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WITNESS_FILES = {"pd": "patna.json", "ga": "gandhari.json", "sa": "sanskrit.json", "zh": "chinese.json", "bo": "tibetan.json"}
NAMES = {"pi": "Pāli (Mahāsaṅgīti)", "pd": "Patna Dharmapada", "ga": "Gāndhārī Dharmapada", "sa": "Sanskrit Udānavarga",
         "zh": "Chinese Faju jing (T210) or fallback", "bo": "Tibetan Udānavarga (Derge Toh 326)"}


def pali_lines(chapter, number):
    """Verse lines only, as build.py selects them (story titles and summaries excluded)."""
    root = json.loads((ROOT / f"data/pali/{chapter['uid']}_root-pli-ms.json").read_text(encoding="utf-8"))
    markup = json.loads((ROOT / f"data/pali/{chapter['uid']}_html.json").read_text(encoding="utf-8"))
    keys = [k for k, v in markup.items() if "class='verse-line'" in v and re.fullmatch(rf"dhp{number}:\d+", k)]
    if number in {416, 423}:
        keys = keys[:{416: 4, 423: 6}[number]]
    return [root[k].strip() for k in keys]


def packet(chapter_no):
    chapters = json.loads((ROOT / "data/chapters.json").read_text(encoding="utf-8"))
    chapters = chapters["chapters"] if isinstance(chapters, dict) else chapters
    chapter = next(c for c in chapters if c["no"] == chapter_no)
    witnesses = {k: {v["pali"]: v for v in json.loads((ROOT / "data/witnesses" / f).read_text(encoding="utf-8"))["verses"]}
                 for k, f in WITNESS_FILES.items()}
    verses = []
    for number in range(chapter["start"], chapter["end"] + 1):
        entry = {"no": number, "witnesses": {"pi": {"status": "present", "readings": [{"reference": f"Dhp {number}", "lines": pali_lines(chapter, number)}]}}}
        for key, index in witnesses.items():
            record = index[number]
            entry["witnesses"][key] = {
                "status": record["status"],
                "readings": [{k: r.get(k) for k in ("reference", "lines", "annotations", "fragmentary", "partial_correspondence", "pinyin") if r.get(k) not in (None, [], False)}
                             for r in record.get("readings", [])],
            }
        verses.append(entry)
    return {"chapter": {k: chapter[k] for k in ("no", "title", "pali_title", "start", "end")}, "witness_names": NAMES, "verses": verses}


if __name__ == "__main__":
    print(json.dumps(packet(int(sys.argv[1])), ensure_ascii=False, indent=1))

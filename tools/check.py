"""Offline integrity checks, including local navigation and preservation of the v2 sample."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import hashlib
import json
import re
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids, self.links = set(), []
        self.verses, self.lines, self.languages = [], [], set()
        self.poems, self.reading_status = {}, {}
        self.current_verse, self.line_depth = None, 0
        self.language, self.current_line = None, None
        self.adjacent_pages, self.chapter_links = [], []
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id") == "sheet":
            self.adjacent_pages = [attrs.get("data-previous-page", ""), attrs.get("data-next-page", "")]
        if tag == "section" and "data-verse" in attrs:
            self.current_verse = int(attrs["data-verse"])
            self.verses.append(self.current_verse)
        if tag == "section" and "data-language" in attrs:
            self.language = attrs["data-language"]
            self.languages.add(self.language)
            self.reading_status[self.current_verse, self.language] = attrs.get("data-reading-status")
        if tag == "span":
            if "poem-line" in attrs.get("class", "").split():
                self.current_line = [self.language, attrs.get("data-segment"), ""]
                self.line_depth = 1
            elif self.current_line is not None:
                self.line_depth += 1
        if attrs.get("id"):
            assert attrs["id"] not in self.ids, f'Duplicate id: {attrs["id"]}'
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("rel") in {"prev", "next"}:
            self.chapter_links.append(attrs["href"])
        key = "href" if tag == "a" else "src" if tag == "script" else None
        if key and attrs.get(key):
            self.links.append(attrs[key])
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.links.append(attrs["href"])

    def handle_data(self, data):
        if self.current_line is not None:
            self.current_line[2] += data

    def handle_endtag(self, tag):
        if tag == "span" and self.current_line is not None:
            self.line_depth -= 1
            if self.line_depth == 0:
                if self.current_line[1] is not None:
                    self.lines.append(tuple(self.current_line))
                self.poems.setdefault((self.current_verse, self.language), []).append(self.current_line[2])
                self.current_line = None
        if tag == "section":
            self.language = None


collection = json.loads((ROOT / "data/chapters.json").read_text())
page_names = ["sample.html", "pairs.html", "contents.html", "notes.html", *[chapter["page"] for chapter in collection["chapters"]]]
pages = {name: Page(ROOT / name) for name in page_names}
expected_assets = {*page_names, "styles.css", "reader.js", ".nojekyll", "assets"}
assert {p.name for p in (ROOT / "dist").iterdir()} == expected_assets, "Unexpected deployment file; remove temporary QA fixtures."
for name, page in pages.items():
    assert "{{" not in (ROOT / name).read_text(), f"Unexpanded template: {name}"
    for link in page.links + [link for link in page.adjacent_pages if link]:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        target = unquote(url.path) or name
        assert (ROOT / target).is_file(), f"Broken local link in {name}: {link}"
        if url.fragment:
            assert target in pages and unquote(url.fragment) in pages[target].ids, f"Broken fragment in {name}: {link}"
    assert (ROOT / name).read_bytes() == (ROOT / "dist" / name).read_bytes(), f"Stale deployment output: {name}"

data_path = ROOT / "data/sample.json"
provenance = json.loads((ROOT / "data/provenance.json").read_text())
assert hashlib.sha256(data_path.read_bytes()).hexdigest() == provenance["sample_sha256"], "The inherited sample changed; this phase must preserve it."
data = json.loads(data_path.read_text())
pinyin = {verse['no']: verse['lines'] for verse in json.loads((ROOT / 'data/pinyin.json').read_text())['verses']}
assert set(pinyin) == {verse['no'] for verse in data['verses']}, 'Pinyin must cover exactly the existing sample.'
for verse in data["verses"]:
    assert all(len(row) == len(data["sources"]) for row in verse["rows"]), "Ragged sample data"
    assert f'dhp{verse["no"]}' in pages["sample.html"].ids, "Missing sample verse deep link"
    assert len(pinyin[verse['no']]) == len(verse['rows']), 'Pinyin alignment does not match the Chinese sample.'
original_urls = set(Page(ROOT / "docs/archive/notes-v2.html").links)
original_urls = {url for url in original_urls if url.startswith("https://")}
assert original_urls <= set(pages["notes.html"].links), "An inherited source URL was removed."

# Verify the imported reading edition against its frozen sources, including every verse and line.
for source in collection["files"]:
    source_bytes = (ROOT / source["local"]).read_bytes()
    assert hashlib.sha256(source_bytes).hexdigest() == source["sha256"], f'Source snapshot changed: {source["local"]}'
    assert hashlib.sha1(b'blob ' + str(len(source_bytes)).encode() + b'\0' + source_bytes).hexdigest() == source["git_blob"], "Source snapshot differs from its upstream Git blob."
english_edition = json.loads((ROOT / "data/english/pi.json").read_text())
assert english_edition["source_language"] == "pi", "English must identify its base language."
english = english_edition["verses"]
assert list(map(int, english)) == list(range(1, 424)), "English draft must cover every Pāli position."
chapter_numbers = []
for chapter in collection["chapters"]:
    page = pages[chapter["page"]]
    numbers = list(range(chapter["start"], chapter["end"] + 1))
    chapter_numbers.extend(numbers)
    assert page.verses == numbers, f'Missing or reordered verses in {chapter["page"]}'
    assert page.languages == {"en", "pi", "pd", "ga", "sa", "zh", "zh-pinyin", "bo"}, "All chapter pages must retain the six historical traditions and English."
    uid = chapter["uid"]
    root = json.loads((ROOT / f'data/pali/{uid}_root-pli-ms.json').read_text())
    markup = json.loads((ROOT / f'data/pali/{uid}_html.json').read_text())
    verse_segments = [key for key, value in markup.items() if "class='verse-line'" in value]
    expected_lines = []
    for number in numbers:
        keys = [key for key in verse_segments if key.startswith(f'dhp{number}:')]
        assert keys, f'Empty verse {number}'
        if number in {416, 423}:
            keys = [f"dhp{number}:{i}" for i in range(1, {416: 5, 423: 7}[number])]
        expected_lines.extend(("pi", key, root[key].replace("<j>", "").strip()) for key in keys)
        entry = english[str(number)]
        assert entry["lines"] and all(line.strip() for line in entry["lines"]), "Missing English rendering."
        assert page.poems[number, "en"] == entry["lines"], "English rendering differs from the editorial draft."
        if entry.get("note"):
            assert f"english-{number}" in pages["notes.html"].ids, "English reading note is missing."
            assert f"notes.html#english-{number}" not in page.links, "English reading notes belong off the sheet."
    assert page.lines == expected_lines, f'Imported text or line divisions changed in {chapter["page"]}'
    assert f'{chapter["page"]}#chapter{chapter["no"]}' in pages["contents.html"].links, "Missing chapter navigation"
expected_numbers = list(range(1, 424))
assert chapter_numbers == expected_numbers, "Reader pages must cover all 423 positions in sequence."
assert [chapter["no"] for chapter in collection["chapters"]] == list(range(1, 27)), "Pāli chapter order changed."
assert collection["pilot_chapters"] == [1, 2, 8, 12, 17, 21], "The archival pilot selection changed."
assert [link for link in pages["contents.html"].links if "#chapter" in link] == [
    f'{c["page"]}#chapter{c["no"]}' for c in collection["chapters"]
], "Contents must list all 26 chapters in Pāli order."
chapters = collection["chapters"]
for index, chapter in enumerate(chapters):
    previous = f'{chapters[index - 1]["page"]}#dhp{chapters[index - 1]["end"]}' if index else ""
    following = f'{chapters[index + 1]["page"]}#dhp{chapters[index + 1]["start"]}' if index + 1 < len(chapters) else ""
    page = pages[chapter["page"]]
    assert page.adjacent_pages == [previous, following], "Chapter arrows must follow Pāli order."
    assert page.chapter_links == [link for link in (previous, following) if link], "Chapter links are missing."
    # Columns are arranged on the sheet itself; the header's "?" opens the short guide.
    assert {"open-help", "reading-help", "face-switch"} <= page.ids and not {"previous-verse", "next-verse", "open-settings", "zoom-in"} & page.ids
assert pages["index.html"].verses == list(range(1, 21)), "The homepage must open the complete first chapter."
assert (ROOT / "pairs.html").read_bytes() == (ROOT / "index.html").read_bytes(), "The existing Pairs URL must remain available."

# Check each displayed historical reading and pinyin against the bounded source data.
normalization = json.loads((ROOT / "data/witnesses/normalization.json").read_text())
characters = {int(code, 16): record["unicode"] for code, record in normalization["characters"].items()}
def normalize(value):
    return value.replace("<j>", "").translate(characters).strip()

witness_records = {}
for filename in ["patna.json", "gandhari.json", "sanskrit.json", "chinese.json", "tibetan.json"]:
    witness = json.loads((ROOT / "data/witnesses" / filename).read_text())
    language = witness["tradition"]
    witness_records[language] = {v["pali"]: v for v in witness["verses"]}
    assert [v["pali"] for v in witness["verses"]] == expected_numbers, f'Incomplete coverage ledger: {filename}'
    source_ids = {source["id"] for source in witness["sources"]}
    for record in witness["verses"]:
        number = record["pali"]
        assert record["status"] in {"present", "partial", "not-located", "unverified"}, "Unclear coverage status"
        if record["status"] == "not-located":
            assert not record["readings"], "A gap must not contain invented filler text."
        else:
            assert record["readings"], "A populated status must contain a sourced reading."
        for reading in record["readings"]:
            assert reading["source_id"] in source_ids and reading["reference"], "Missing source reference"
            assert reading["lines"] and all(isinstance(line, str) and line.strip() for line in reading["lines"]), "Empty historical verse text"
            if language == "zh":
                assert len(reading["pinyin"]) == len(reading["lines"]) and all(reading["pinyin"]), "Missing pinyin line"
        chosen = next((r for r in record["readings"] if r.get("preferred")), next(iter(record["readings"]), None))
        chapter = next(c for c in collection["chapters"] if c["start"] <= number <= c["end"])
        page = pages[chapter["page"]]
        expected = [normalize(line) for line in chosen["lines"]] if chosen else []
        assert page.poems.get((number, language), []) == expected, f'Reading changed: Pāli {number}, {language}'
        assert page.reading_status[number, language] == record["status"], "Lost uncertainty/coverage status"
        if language == "zh":
            assert page.poems.get((number, "zh-pinyin"), []) == (chosen["pinyin"] if chosen else []), f'Pinyin changed: {number}'

alternates = json.loads((ROOT / "data/english/alternates.json").read_text())
assert set(alternates) == set(witness_records)
for language, readings in alternates.items():
    for number, lines in readings.items():
        assert witness_records[language][int(number)]["readings"], "Alternate English requires a source witness."
        assert lines and all(isinstance(line, str) and line.strip() for line in lines), "Incomplete alternate English."
for chapter in chapters:
    rendered = (ROOT / chapter["page"]).read_text()
    payload = json.loads(re.search(r'<script type="application/json" id="english-editions">(.*?)</script>', rendered).group(1))
    expected = {
        language: {number: lines for number, lines in readings.items() if chapter["start"] <= int(number) <= chapter["end"]}
        for language, readings in {"pi": {number: entry["lines"] for number, entry in english.items()}, **alternates}.items()
    }
    assert payload == {language: lines for language, lines in expected.items() if lines}, "Wrong alternate English for chapter."

coverage = json.loads((ROOT / "data/chapter-coverage.json").read_text())
assert len(coverage) == 26
for chapter in coverage:
    positions = list(range(chapter["start"], chapter["end"] + 1))
    assert chapter["positions"] == len(positions)
    expected = {key: sum(bool(records[n]["readings"]) for n in positions) for key, records in witness_records.items()}
    assert chapter["counts"] == {"pi": len(positions), **expected}
    assert chapter["represented"] == sum(n > 0 for n in chapter["counts"].values())
    assert chapter["six_populated"] == sum(all(records[n]["readings"] for records in witness_records.values()) for n in positions)
    assert chapter["six_present"] == sum(all(records[n]["status"] == "present" for records in witness_records.values()) for n in positions)
    assert chapter["tier"] == (1 if chapter["six_present"] / len(positions) >= .5 else 2 if chapter["represented"] >= 5 else 3)

# Check native text against retained source passages, not just the rendered data.
indic_source = json.loads((ROOT / "data/witnesses/sources/indic/selected-source-passages.json").read_text())
indic_passages = {(entry["tradition"], entry["pali"]): entry["readings"] for entry in indic_source["verses"]}
patna_corrections = {entry["pali"]: entry for entry in indic_source["primary_corrections"]}
indic_corrections = json.loads((ROOT / "data/witnesses/sources/indic/corrections.json").read_text())
line_corrections = {(c["tradition"], c["pali"], c["reference"]): c for c in indic_corrections.get("line_corrections", [])}
corrected_count = 0
for filename in ["patna.json", "gandhari.json", "sanskrit.json"]:
    witness = json.loads((ROOT / "data/witnesses" / filename).read_text())
    for record in witness["verses"]:
        source_readings = indic_passages[witness["tradition"], record["pali"]]
        assert len(record["readings"]) == len(source_readings), "An Indic counterpart was lost from the source selection."
        for reading, source in zip(record["readings"], source_readings):
            assert reading["reference"] == source["reference"], "Indic source reference changed."
            if witness["tradition"] == "pd" and record["pali"] in patna_corrections:
                correction = patna_corrections[record["pali"]]
                assert source["lines"] == correction["comparative_lines"], "Patna correction lost its original source text."
                assert reading["lines"] == correction["replacement_lines"] and reading["source_url"] == correction["primary_source_url"], "Patna correction differs from its separately checked primary edition."
            else:
                expected_lines = list(source["lines"])
                expected_annotations = json.loads(json.dumps(source["annotations"]))
                fix = line_corrections.get((witness["tradition"], record["pali"], reading["reference"]))
                if fix:
                    # Only the recorded characters may differ from the comparative page.
                    assert expected_lines[fix["line"]].count(fix["source_form"]) == 1, "Line correction no longer matches its source."
                    expected_lines[fix["line"]] = expected_lines[fix["line"]].replace(fix["source_form"], fix["corrected_form"])
                    for annotation in expected_annotations:
                        if annotation["line"] == fix["line"]:
                            annotation["text"] = annotation["text"].replace(fix["source_form"], fix["corrected_form"])
                    assert fix["native_evidence"]["url"] and fix["independent_evidence"]["url"], "A line correction needs two cited editions."
                    assert fix["display_note"] in reading.get("note", ""), "A corrected reading must say so in Notes."
                    corrected_count += 1
                assert reading["lines"] == expected_lines and reading["annotations"] == expected_annotations, "Indic reading differs from its retained source passage."

assert corrected_count == len(line_corrections), "Every recorded line correction must apply to exactly one reading."

ns = {"t": "http://www.tei-c.org/ns/1.0"}
chinese_sources = {}
for number in [210, 212, 213]:
    xml = ET.parse(ROOT / f"data/witnesses/sources/chinese/T04n{number:04d}-selected.xml")
    for group in xml.findall(".//t:lg", ns):
        reference = group.get("corresp")
        chinese_sources[reference] = ["".join(line.itertext()).strip() for line in group.findall("t:l", ns)]
chinese = json.loads((ROOT / "data/witnesses/chinese.json").read_text())
for record in chinese["verses"]:
    for reading in record["readings"]:
        assert reading["lines"] == chinese_sources[reading["reference"]], f'Chinese differs from retained CBETA text: {record["pali"]}'

tibetan = json.loads((ROOT / "data/witnesses/tibetan.json").read_text())
excerpts = json.loads((ROOT / "data/witnesses/sources/tibetan/selected-derge-excerpts.json").read_text())
by_number = {entry["pali"]: entry for entry in excerpts["excerpts"]}
for record in tibetan["verses"]:
    if not record["readings"]:
        continue
    excerpt = by_number[record["pali"]]
    native = re.sub(r"\[\d+x?[ab](?:\.\d+)?\]|\{D\d+\}|\r?\n", "", excerpt["raw_source_lines"])
    native = re.sub(r"\{([^,{}]+),[^{}]+\}", r"\1", native)
    reading = record["readings"][0]
    assert reading["lines"] == excerpt["display_lines"], "Tibetan differs from its cited source selection"
    cursor = 0
    for line in reading["lines"]:
        position = native.find(line, cursor)
        assert position >= cursor, f'Tibetan line not found in the cited native passage: {record["pali"]}'
        cursor = position + len(line)
    assert reading["source_line_start"] == excerpt["source_line_start"] and reading["source_line_end"] == excerpt["source_line_end"], "Tibetan citation changed"

# Keep published Tibetan attestations distinct from direct native checks and semantic identity.
audit = json.loads((ROOT / "data/witnesses/sources/tibetan/correspondence-audit.json").read_text())
assert [record["pali"] for record in audit["verses"]] == list(range(1, 424)), "The Tibetan research ledger must cover all 423 Pāli positions."
assert len(audit["chapters"]) == 26, "The Tibetan research summary must cover all 26 Pāli chapters."
tibetan_records = {record["pali"]: record for record in tibetan["verses"]}
for record in audit["verses"]:
    published = any(not ref["tentative"] for ref in record["rockhill_references"])
    native = tibetan_records.get(record["pali"])
    assert record["published_parallel"] == published, "A tentative Tibetan citation entered the secure count."
    assert record["direct_native_status"] == (native["status"] if native else None), "Tibetan audit differs from the reader's native verification status."
    assert record["native_checked"] == bool(native and native["readings"]), "A native text check was claimed without a retained reading."
    assert record["attested_parallel"] == (published or bool(native and native["status"] == "present")), "Tibetan attestation was inferred without the declared evidence."
    if native and native["readings"]:
        assert [(r["source_line_start"], r["source_line_end"]) for r in record["native_references"]] == [(r["source_line_start"], r["source_line_end"]) for r in native["readings"]], "Tibetan research and reading source locators disagree."
for chapter in audit["chapters"]:
    records = [record for record in audit["verses"] if record["pali_chapter"] == chapter["pali_chapter"]]
    assert chapter["positions"] == len(records), "Tibetan chapter denominator changed."
    assert chapter["attested_lower_bound"] == sum(record["attested_parallel"] for record in records), "Tibetan chapter attestation count changed."
    assert chapter["native_checked"] == sum(record["native_checked"] for record in records), "Tibetan chapter native check count changed."
    assert chapter["same_title_chapter_lower_bound"] == sum(record["same_title_parallel"] for record in records), "Tibetan same-theme count changed."
    assert chapter["coverage_lower_bound"] == chapter["attested_lower_bound"] / chapter["positions"], "Tibetan coverage denominator changed."
assert audit["summary"]["attested_lower_bound"] == sum(record["attested_parallel"] for record in audit["verses"]), "Tibetan overall lower bound changed."
assert audit["summary"]["native_checked"] == sum(record["native_checked"] for record in audit["verses"]), "Tibetan overall native count changed."

# Rosettapada Blend workspace: words, principles, questions and drafts keep their provenance shape.
blend_rulings_path = ROOT / "data/blend/rulings.json"
blend_rulings = json.loads(blend_rulings_path.read_text()) if blend_rulings_path.exists() else {"words": [], "principles": []}
word_ids = [w["id"] for w in blend_rulings["words"]]
principle_ids = [p["id"] for p in blend_rulings["principles"]]
assert len(word_ids + principle_ids) == len(set(word_ids + principle_ids)), "Duplicate Blend word or principle id."
for w in blend_rulings["words"]:
    assert w["status"] in {"proposed", "decided"}, f'Bad status on word {w["id"]}'
    assert w["status"] == "proposed" or w.get("decided"), f'Word {w["id"]} is settled without its decision and reason'
question_ids = set()
blend_lines = set()
for path in sorted((ROOT / "data/blend/chapters").glob("*.json")):
    blend_chapter = json.loads(path.read_text())
    span = range(blend_chapter["chapter"]["start"], blend_chapter["chapter"]["end"] + 1)
    assert [v["no"] for v in blend_chapter["verses"]] == list(span), f"{path.name} does not cover its verses in order"
    chapter_questions = {q["id"]: q for q in blend_chapter.get("questions", [])}
    question_ids |= set(chapter_questions)
    slot_ids = set(chapter_questions) | set(word_ids)
    for q in chapter_questions.values():
        assert q.get("options") or q.get("decided"), f"Question {q['id']} has no options"
    for v in blend_chapter["verses"]:
        assert v["lines"] and all(l["tier"] in (1, 2, 3, 4) for l in v["lines"]), f"{path.name} verse {v['no']} has an untiered line"
        assert v["tier"] == max(l["tier"] for l in v["lines"]), f"{path.name} verse {v['no']} tier is not its hardest line"
        assert v.get("owner_tier") in (None, 1, 2, 3, 4), f"{path.name} verse {v['no']} has a bad owner tier"
        assert set(v.get("questions", [])) <= set(chapter_questions), f"{path.name} verse {v['no']} names an unknown question"
        for l in v["lines"]:
            blend_lines.add(f"{v['no']}.{l['line']}")
            known = [t for t in l["tiers"].values() if t]
            assert l["tier"] >= max(known, default=1), f"{path.name} verse {v['no']} line {l['line']} was tiered below a reader"
            assert set(l.get("rules", [])) <= set(word_ids) | set(principle_ids), f"{path.name} verse {v['no']} line {l['line']} cites an unknown word or principle"
        if v.get("draft"):
            assert len(v["draft"]) == len(v["lines"]), f"{path.name} verse {v['no']} draft is not line for line"
            for dl in v["draft"]:
                for seg in dl["segments"]:
                    if not isinstance(seg, str):
                        assert seg["slot"] in slot_ids, f"{path.name} verse {v['no']} draft slot {seg['slot']} is unknown"
        for b in v.get("blend") or []:
            assert b.get("witnesses") and b.get("tier") in (1, 2, 3, 4), f"{path.name} verse {v['no']} Blend line lacks provenance"
findings_path = ROOT / "data/blend/findings.json"
if findings_path.exists():
    findings = json.loads(findings_path.read_text())
    notable_ids = {n["id"] for n in findings["notable"]}
    for n in findings["notable"]:
        assert n["weight"] in {"doctrine", "practice", "imagery", "translation"}, f'{n["id"]} has an unknown weight'
        assert set(n["lines"]) <= blend_lines, f'{n["id"]} cites a line that has not been read'
        assert set(n["refs"]) <= set(word_ids) | set(principle_ids) | question_ids, f'{n["id"]} cites an unknown word, principle or question'
    for p in findings["patterns"]:
        assert p["status"] in {"hypothesis", "supported", "weakened", "dropped"}, f'{p["id"]} has an unknown status'
        assert set(p["evidence"]) | set(p["against"]) <= notable_ids, f'{p["id"]} cites unknown evidence'
frozen = json.loads((ROOT / "data/witnesses/provenance.json").read_text())
for source in frozen["files"]:
    assert hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["sha256"], f'Historical snapshot changed: {source["path"]}'
for source in (ROOT / "assets").rglob("*"):
    if source.is_file():
        target = ROOT / "dist" / source.relative_to(ROOT)
        assert target.read_bytes() == source.read_bytes(), "Font/asset deployment differs from source"
for chapter in collection["chapters"]:
    assert not any('\ue000' <= char <= '\uf8ff' for char in (ROOT / chapter["page"]).read_text()), "An unsupported legacy glyph reached the reader."
print("Passed: 423 verse positions, English draft, historical sources, 26 chapter tiers, navigation, pinyin, sample, links, and assets.")


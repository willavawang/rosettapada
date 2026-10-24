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
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
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
    for link in page.links:
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
chapter_numbers = []
for chapter in collection["chapters"]:
    page = pages[chapter["page"]]
    numbers = list(range(chapter["start"], chapter["end"] + 1))
    chapter_numbers.extend(numbers)
    assert page.verses == numbers, f'Missing or reordered verses in {chapter["page"]}'
    assert page.languages == {"en", "pi", "pd", "ga", "sa", "zh", "zh-pinyin", "bo"}, "All chapter pages must retain the six historical traditions and English."
    uid = chapter["uid"]
    root = json.loads((ROOT / f'data/pali/{uid}_root-pli-ms.json').read_text())
    english = json.loads((ROOT / f'data/pali/{uid}_translation-en-sujato.json').read_text())
    markup = json.loads((ROOT / f'data/pali/{uid}_html.json').read_text())
    verse_segments = [key for key, value in markup.items() if "class='verse-line'" in value]
    expected_lines = []
    for number in numbers:
        keys = [key for key in verse_segments if key.startswith(f'dhp{number}:')]
        assert keys, f'Empty verse {number}'
        for language, text in [("en", english), ("pi", root)]:
            expected_lines.extend((language, key, text[key].replace("<j>", "").strip()) for key in keys)
    assert page.lines == expected_lines, f'Imported text or line divisions changed in {chapter["page"]}'
    assert f'{chapter["page"]}#chapter{chapter["no"]}' in pages["contents.html"].links, "Missing chapter navigation"
assert chapter_numbers == list(range(1, 44)), "The requested selection must contain exactly verses 1–43."
assert len([link for link in pages["contents.html"].links if "#chapter" in link]) == 3, "Contents must list exactly three chapter pages."
assert pages["index.html"].verses == list(range(1, 21)), "The homepage must open the complete first chapter."
assert (ROOT / "pairs.html").read_bytes() == (ROOT / "index.html").read_bytes(), "The existing Pairs URL must remain available."

# Check each displayed historical reading and pinyin against the bounded source data.
normalization = json.loads((ROOT / "data/witnesses/normalization.json").read_text())
characters = {int(code, 16): record["unicode"] for code, record in normalization["characters"].items()}
def normalize(value):
    return value.replace("<j>", "").translate(characters).strip()

for filename in ["patna.json", "gandhari.json", "sanskrit.json", "chinese.json", "tibetan.json"]:
    witness = json.loads((ROOT / "data/witnesses" / filename).read_text())
    language = witness["tradition"]
    assert [v["pali"] for v in witness["verses"]] == list(range(1, 44)), f'Incomplete coverage ledger: {filename}'
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

# Check native text against retained source passages, not just the rendered data.
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

frozen = json.loads((ROOT / "data/witnesses/provenance.json").read_text())
for source in frozen["files"]:
    assert hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["sha256"], f'Historical snapshot changed: {source["path"]}'
for source in (ROOT / "assets").rglob("*"):
    if source.is_file():
        target = ROOT / "dist" / source.relative_to(ROOT)
        assert target.read_bytes() == source.read_bytes(), "Font/asset deployment differs from source"
for chapter in collection["chapters"]:
    assert not any('\ue000' <= char <= '\uf8ff' for char in (ROOT / chapter["page"]).read_text()), "An unsupported legacy glyph reached the reader."
print("Passed: 43 verses across six traditions match the source records; pinyin, coverage gaps, source hashes, sample, links, and assets verified.")


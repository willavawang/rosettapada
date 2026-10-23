"""Offline integrity checks, including local navigation and preservation of the v2 sample."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids, self.links = set(), []
        self.verses, self.lines, self.languages = [], [], set()
        self.language, self.current_line = None, None
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section" and "data-verse" in attrs:
            self.verses.append(int(attrs["data-verse"]))
        if tag == "section" and "data-language" in attrs:
            self.language = attrs["data-language"]
            self.languages.add(self.language)
        if tag == "span" and "data-segment" in attrs:
            self.current_line = [self.language, attrs["data-segment"], ""]
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
            self.lines.append(tuple(self.current_line))
            self.current_line = None
        if tag == "section":
            self.language = None


collection = json.loads((ROOT / "data/chapters.json").read_text())
page_names = ["index.html", "contents.html", "notes.html", *[chapter["page"] for chapter in collection["chapters"]]]
pages = {name: Page(ROOT / name) for name in page_names}
expected_assets = {*page_names, "styles.css", "reader.js", ".nojekyll"}
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
    assert f'dhp{verse["no"]}' in pages["index.html"].ids, "Missing verse deep link"
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
    assert page.languages == {"en", "pi"}, "Chapter pages must not imply unverified historical parallels."
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
print("Passed: all 43 English–Pāli verses match the source snapshot; sample and references preserved; links and deployment pages valid.")


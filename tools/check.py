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
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            assert attrs["id"] not in self.ids, f'Duplicate id: {attrs["id"]}'
            self.ids.add(attrs["id"])
        key = "href" if tag == "a" else "src" if tag == "script" else None
        if key and attrs.get(key):
            self.links.append(attrs[key])
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.links.append(attrs["href"])


pages = {name: Page(ROOT / name) for name in ["index.html", "contents.html", "notes.html"]}
expected_assets = {"index.html", "contents.html", "notes.html", "styles.css", "reader.js", ".nojekyll"}
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
for verse in data["verses"]:
    assert all(len(row) == len(data["sources"]) for row in verse["rows"]), "Ragged sample data"
    assert f'dhp{verse["no"]}' in pages["index.html"].ids, "Missing verse deep link"
original_urls = set(Page(ROOT / "docs/archive/notes-v2.html").links)
original_urls = {url for url in original_urls if url.startswith("https://")}
assert original_urls <= set(pages["notes.html"].links), "An inherited source URL was removed."
print("Passed: sample unchanged; source references retained; local links, verse anchors and deployment pages valid.")


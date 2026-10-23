"""Render the Rosettapada reading study. Standard library only; no network access."""
from html import escape
from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data/sample.json").read_text(encoding="utf-8"))
SOURCES, VERSES = DATA["sources"], DATA["verses"]
LANGS = {"en": "en", "pi": "pi", "pd": "pra", "ga": "pgd", "sa": "sa", "zh": "zh-Hant", "bo": "bo"}


def e(value):
    return escape(str(value), quote=True)


def render(name, **values):
    text = (ROOT / "templates" / name).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    (ROOT / name).write_text(text, encoding="utf-8")


headings = "\n".join(
    f'<div class="column-heading"><span class="column-name">{e(s["language"])}</span>'
    f'<span class="column-reference">{e("Pāli working translation" if s["key"] == "en" else "Not yet verified" if s["key"] == "bo" else s["reference"])}</span></div>'
    for s in SOURCES
)
verses = []
for verse in VERSES:
    poems = []
    for col, source in enumerate(SOURCES):
        key = source["key"]
        lines = [row[col] for row in verse["rows"]]
        poem_id = f'v{verse["no"]}-{key}'
        label = f'{source["language"]}, verse {verse["no"]}'
        if all(line is None for line in lines):
            content = '<p class="unverified" lang="en">Not yet verified.<span>Source and reading pending.</span></p>'
        else:
            content = '<p class="poem">' + "".join(
                '<span class="poem-line">' + (e(line) if line is not None else '<span class="unverified">Not yet verified</span>') + '</span>'
                for line in lines
            ) + '</p>'
        poems.append(f'<section class="witness lang-{key}" lang="{LANGS[key]}" aria-labelledby="{poem_id}"><h3 class="sr-only" id="{poem_id}">{e(label)}</h3>{content}</section>')
    verses.append(
        f'<section class="verse" id="dhp{verse["no"]}" data-verse="{verse["no"]}" aria-labelledby="verse-title-{verse["no"]}">'
        f'<h2 class="verse-marker" id="verse-title-{verse["no"]}"><span class="verse-number">{verse["no"]:02d}</span>'
        f'<span class="verse-title">{e(verse["title"])}</span></h2>'
        f'<div class="verse-grid" style="--line-count:{len(verse["rows"])}">' + "\n".join(poems) + '</div></section>'
    )
render("index.html", COLUMN_HEADINGS=headings, VERSES="\n".join(verses))
links = "\n".join(
    f'<li><a class="verse-link" href="index.html#dhp{v["no"]}"><span class="toc-number">{v["no"]:02d}</span><span>{e(v["title"])}</span><span class="toc-arrow" aria-hidden="true">↗</span></a></li>'
    for v in VERSES
)
render("contents.html", VERSE_LINKS=links)
render("notes.html")
dist = ROOT / "dist"
dist.mkdir(exist_ok=True)
for filename in ["index.html", "contents.html", "notes.html", "styles.css", "reader.js", ".nojekyll"]:
    shutil.copyfile(ROOT / filename, dist / filename)
print(f"Built Rosettapada: {len(VERSES)} sample verses, {len(SOURCES)} reading columns.")


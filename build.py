"""Render the Rosettapada reading study. Standard library only; no network access."""
from html import escape
from pathlib import Path
import json
import shutil
import hashlib

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data/sample.json").read_text(encoding="utf-8"))
PINYIN = json.loads((ROOT / "data/pinyin.json").read_text(encoding="utf-8"))
PINYIN_VERSES = {verse["no"]: verse["lines"] for verse in PINYIN["verses"]}
SOURCES = list(DATA["sources"])
SOURCES.insert(6, {"key": "zh-pinyin", "language": "Chinese pinyin", "reference": "Mandarin reading aid"})
VERSES = DATA["verses"]
SOURCE_INDEX = {source["key"]: index for index, source in enumerate(DATA["sources"])}
LANGS = {"en": "en", "pi": "pi", "pd": "pra", "ga": "pgd", "sa": "sa", "zh": "zh-Hant", "zh-pinyin": "zh-Latn-pinyin", "bo": "bo"}
WIDTHS = {"en": "min(540px, calc(100vw - 56px))", "pi": "320px", "pd": "340px", "ga": "320px", "sa": "345px", "zh": "230px", "zh-pinyin": "300px", "bo": "285px"}


def e(value):
    return escape(str(value), quote=True)


def render(name, **values):
    text = (ROOT / "templates" / name).read_text(encoding="utf-8")
    values = {
        "STYLE_VERSION": hashlib.sha256((ROOT / "styles.css").read_bytes()).hexdigest()[:10],
        "READER_VERSION": hashlib.sha256((ROOT / "reader.js").read_bytes()).hexdigest()[:10],
        **values,
    }
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    (ROOT / name).write_text(text, encoding="utf-8")


headings, settings = [], []
for source in SOURCES:
    key = source["key"]
    hidden = " hidden" if key == "zh-pinyin" else ""
    checked = "" if key == "zh-pinyin" else " checked"
    reference = "Pāli working translation" if key == "en" else "Not yet verified" if key == "bo" else source["reference"]
    headings.append(
        f'<div class="column-heading" data-language="{key}" data-width="{WIDTHS[key]}"{hidden}>'
        f'<span class="column-name">{e(source["language"])}</span><span class="column-reference">{e(reference)}</span></div>'
    )
    settings.append(
        f'<li class="language-option" data-language="{key}"><label for="show-{key}">'
        f'<input id="show-{key}" type="checkbox" data-language="{key}"{checked}>'
        f'<span>{e(source["language"])}</span></label>'
        f'<button class="drag-handle" type="button" data-language="{key}" '
        f'aria-label="Reorder {e(source["language"])}" aria-describedby="reorder-help" '
        f'title="Drag to reorder; use the up and down arrow keys with the keyboard"><span aria-hidden="true">⠿</span></button></li>'
    )
verses = []
for verse in VERSES:
    poems = []
    for source in SOURCES:
        key = source["key"]
        lines = PINYIN_VERSES[verse["no"]] if key == "zh-pinyin" else [row[SOURCE_INDEX[key]] for row in verse["rows"]]
        hidden = " hidden" if key == "zh-pinyin" else ""
        poem_id = f'v{verse["no"]}-{key}'
        label = f'{source["language"]}, verse {verse["no"]}'
        if all(line is None for line in lines):
            content = '<p class="unverified" lang="en">Not yet verified.<span>Source and reading pending.</span></p>'
        else:
            content = '<p class="poem">' + "".join(
                '<span class="poem-line">' + (e(line) if line is not None else '<span class="unverified">Not yet verified</span>') + '</span>'
                for line in lines
            ) + '</p>'
        poems.append(f'<section class="witness lang-{key}" data-language="{key}" lang="{LANGS[key]}" aria-labelledby="{poem_id}"{hidden}><h3 class="sr-only" id="{poem_id}">{e(label)}</h3>{content}</section>')
    verses.append(
        f'<section class="verse" id="dhp{verse["no"]}" data-verse="{verse["no"]}" aria-labelledby="verse-title-{verse["no"]}">'
        f'<h2 class="sr-only" id="verse-title-{verse["no"]}">Verse {verse["no"]}</h2>'
        f'<div class="verse-grid" style="--line-count:{len(verse["rows"])}">' + "\n".join(poems) + '</div>'
        '</section>'
    )
render("index.html", COLUMN_HEADINGS="\n".join(headings), VERSES="\n".join(verses), LANGUAGE_SETTINGS="\n".join(settings))
render("contents.html")
render("notes.html")
dist = ROOT / "dist"
dist.mkdir(exist_ok=True)
for filename in ["index.html", "contents.html", "notes.html", "styles.css", "reader.js", ".nojekyll"]:
    shutil.copyfile(ROOT / filename, dist / filename)
print(f"Built Rosettapada: {len(VERSES)} sample verses, {len(SOURCES)} selectable columns (pinyin hidden by default).")


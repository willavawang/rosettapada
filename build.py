"""Render the Rosettapada reading study. Standard library only; no network access."""
from html import escape
from pathlib import Path
import json
import shutil
import hashlib
import re

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data/sample.json").read_text(encoding="utf-8"))
PINYIN = json.loads((ROOT / "data/pinyin.json").read_text(encoding="utf-8"))
PINYIN_VERSES = {verse["no"]: verse["lines"] for verse in PINYIN["verses"]}
SOURCES = list(DATA["sources"])
SOURCES.insert(6, {"key": "zh-pinyin", "language": "Chinese pinyin", "reference": "Mandarin reading aid"})
VERSES = DATA["verses"]
COLLECTION = json.loads((ROOT / "data/chapters.json").read_text(encoding="utf-8"))
CHAPTERS = COLLECTION["chapters"]
SOURCE_INDEX = {source["key"]: index for index, source in enumerate(DATA["sources"])}
LANGS = {"en": "en", "pi": "pi", "pd": "pra", "ga": "pgd", "sa": "sa", "zh": "zh-Hant", "zh-pinyin": "zh-Latn-pinyin", "bo": "bo"}
WIDTHS = {"en": "min(540px, calc(100vw - 56px))", "pi": "320px", "pd": "340px", "ga": "320px", "sa": "345px", "zh": "230px", "zh-pinyin": "300px", "bo": "285px"}


def e(value):
    return escape(str(value), quote=True)


def reading_text(value):
    # Bilara's nonprinting join markers are formatting, not verse text.
    return value.replace("<j>", "").strip()


def render(name, template=None, **values):
    text = (ROOT / "templates" / (template or name)).read_text(encoding="utf-8")
    values = {
        "STYLE_VERSION": hashlib.sha256((ROOT / "styles.css").read_bytes()).hexdigest()[:10],
        "READER_VERSION": hashlib.sha256((ROOT / "reader.js").read_bytes()).hexdigest()[:10],
        **values,
    }
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    (ROOT / name).write_text(text, encoding="utf-8")


def render_reader(name, sources, verses, title, chapter_id, profile="sample", previous="", next_page="", chapter_title="", help_note=""):
    headings, settings, verse_html = [], [], []
    for source in sources:
        key = source["key"]
        hidden = " hidden" if key == "zh-pinyin" else ""
        checked = "" if hidden else " checked"
        headings.append(
            f'<div class="column-heading" data-language="{key}" data-width="{WIDTHS[key]}"{hidden}>'
            f'<span class="column-name">{e(source["language"])}</span><span class="column-reference">{e(source["reference"])}</span></div>'
        )
        settings.append(
            f'<li class="language-option" data-language="{key}"><label for="show-{key}">'
            f'<input id="show-{key}" type="checkbox" data-language="{key}"{checked}>'
            f'<span>{e(source["language"])}</span></label>'
            f'<button class="drag-handle" type="button" data-language="{key}" '
            f'aria-label="Reorder {e(source["language"])}" aria-describedby="reorder-help" '
            f'title="Drag to reorder; use the up and down arrow keys with the keyboard"><span aria-hidden="true">⠿</span></button></li>'
        )
    for verse in verses:
        poems = []
        line_count = max(len(lines) for lines in verse["lines"].values())
        for source in sources:
            key = source["key"]
            lines = verse["lines"][key]
            hidden = " hidden" if key == "zh-pinyin" else ""
            poem_id = f'v{verse["no"]}-{key}'
            label = f'{source["language"]}, verse {verse["no"]}'
            if all(line is None for line in lines):
                content = '<p class="unverified" lang="en">Not yet verified.<span>Source and reading pending.</span></p>'
            else:
                rendered_lines = []
                for index, line in enumerate(lines):
                    segment = f' data-segment="{e(verse["segments"][index])}"' if "segments" in verse else ""
                    text = e(line) if line is not None else '<span class="unverified">Not yet verified</span>'
                    rendered_lines.append(f'<span class="poem-line"{segment}>{text}</span>')
                content = '<p class="poem">' + "".join(rendered_lines) + '</p>'
            poems.append(f'<section class="witness lang-{key}" data-language="{key}" lang="{LANGS[key]}" aria-labelledby="{poem_id}"{hidden}><h3 class="sr-only" id="{poem_id}">{e(label)}</h3>{content}</section>')
        verse_html.append(
            f'<section class="verse" id="dhp{verse["no"]}" data-verse="{verse["no"]}" aria-labelledby="verse-title-{verse["no"]}">'
            f'<h2 class="sr-only" id="verse-title-{verse["no"]}">Verse {verse["no"]}</h2>'
            f'<div class="verse-grid" style="--line-count:{line_count}">' + "\n".join(poems) + '</div></section>'
        )
    render(name, template="index.html", TITLE=e(title), CHAPTER_ID=chapter_id, PAGE_KEY=name.removesuffix(".html"),
           PROFILE=profile, PREVIOUS_PAGE=e(previous), NEXT_PAGE=e(next_page), CHAPTER_TITLE=e(chapter_title),
           INITIAL_LOCATION=e(f'Verse {verses[0]["no"]}, {chapter_title}' if chapter_title else f'Verse 1 of {len(verses)}'),
           DESCRIPTION=e(f'Rosettapada — {title}. Dhammapada reading with English and Pāli.' if profile == "pali" else 'Rosettapada — a two-verse comparative Dhammapada reading study.'),
           HELP_NOTE=e(help_note), COLUMN_HEADINGS="\n".join(headings), VERSES="\n".join(verse_html), LANGUAGE_SETTINGS="\n".join(settings))


sample_verses = [{"no": verse["no"], "lines": {
    source["key"]: PINYIN_VERSES[verse["no"]] if source["key"] == "zh-pinyin" else [row[SOURCE_INDEX[source["key"]]] for row in verse["rows"]]
    for source in SOURCES
}} for verse in VERSES]
sample_sources = [{**source, "reference": "Pāli working translation" if source["key"] == "en" else "Not yet verified" if source["key"] == "bo" else source["reference"]} for source in SOURCES]
render_reader("sample.html", sample_sources, sample_verses, "The pairs", "chapter1",
              help_note="Two verses are included in this comparative sample. The English follows Pāli; alignment across traditions is provisional. Complete English–Pāli chapters are available in Contents.")

for index, chapter in enumerate(CHAPTERS):
    uid = chapter["uid"]
    root = json.loads((ROOT / f'data/pali/{uid}_root-pli-ms.json').read_text(encoding="utf-8"))
    english = json.loads((ROOT / f'data/pali/{uid}_translation-en-sujato.json').read_text(encoding="utf-8"))
    markup = json.loads((ROOT / f'data/pali/{uid}_html.json').read_text(encoding="utf-8"))
    # The source marks actual verse lines explicitly; exclude story headings and chapter colophons.
    segments = [key for key, value in markup.items() if "class='verse-line'" in value]
    verses = []
    for number in range(chapter["start"], chapter["end"] + 1):
        keys = [key for key in segments if re.fullmatch(rf'dhp{number}:\d+', key)]
        assert keys and all(root[key].strip() and english[key].strip() for key in keys), f'Incomplete verse {number}'
        verses.append({"no": number, "segments": keys, "lines": {"en": [reading_text(english[key]) for key in keys], "pi": [reading_text(root[key]) for key in keys]}})
    sources = [{"key": "en", "language": "English", "reference": "Bhikkhu Sujato"}, {"key": "pi", "language": "Pāli", "reference": "Mahāsaṅgīti edition"}]
    previous = f'{CHAPTERS[index - 1]["page"]}#dhp{chapter["start"] - 1}' if index else ""
    next_page = f'{CHAPTERS[index + 1]["page"]}#dhp{chapter["end"] + 1}' if index + 1 < len(CHAPTERS) else ""
    render_reader(chapter["page"], sources, verses, chapter["title"], f'chapter{chapter["no"]}', profile="pali",
                  previous=previous, next_page=next_page, chapter_title=chapter["title"],
                  help_note="English by Bhikkhu Sujato, alongside the Mahāsaṅgīti Pāli. The first three chapters (verses 1–43) are available. Verse arrows continue across chapter boundaries.")

# Preserve links shared before Pairs became the homepage.
(ROOT / "pairs.html").write_bytes((ROOT / CHAPTERS[0]["page"]).read_bytes())
chapter_links = "\n".join(f'<a class="toc-page-link" href="{chapter["page"]}#chapter{chapter["no"]}"><span>{e(chapter["title"])}</span><span class="toc-arrow" aria-hidden="true">↗</span></a>' for chapter in CHAPTERS)
render("contents.html", CHAPTER_LINKS=chapter_links)
render("notes.html", BILARA_SOURCE_URL=f'https://github.com/suttacentral/bilara-data/tree/{COLLECTION["upstream"]["commit"]}')
dist = ROOT / "dist"
dist.mkdir(exist_ok=True)
for filename in ["sample.html", "pairs.html", "contents.html", "notes.html", "styles.css", "reader.js", ".nojekyll", *[chapter["page"] for chapter in CHAPTERS]]:
    shutil.copyfile(ROOT / filename, dist / filename)
print(f"Built Rosettapada: 3 English–Pāli chapters, 43 verses, plus the unchanged comparative sample.")


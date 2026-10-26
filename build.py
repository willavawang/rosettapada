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
PILOT_NUMBERS = COLLECTION["pilot_chapters"]
PILOT_CHAPTERS = [chapter for chapter in CHAPTERS if chapter["no"] in PILOT_NUMBERS]
SECONDARY_CHAPTERS = [chapter for chapter in CHAPTERS if chapter["no"] not in PILOT_NUMBERS]
READING_NUMBERS = [number for chapter in CHAPTERS for number in range(chapter["start"], chapter["end"] + 1)]
WITNESS_FILES = {"pd": "patna.json", "ga": "gandhari.json", "sa": "sanskrit.json", "zh": "chinese.json", "bo": "tibetan.json"}
WITNESSES = {key: json.loads((ROOT / "data/witnesses" / filename).read_text(encoding="utf-8")) for key, filename in WITNESS_FILES.items()}
WITNESS_INDEX = {key: {verse["pali"]: verse for verse in data["verses"]} for key, data in WITNESSES.items()}
TIBETAN_AUDIT = json.loads((ROOT / "data/witnesses/sources/tibetan/correspondence-audit.json").read_text(encoding="utf-8"))
NORMALIZATION = json.loads((ROOT / "data/witnesses/normalization.json").read_text(encoding="utf-8"))
CHARACTERS = {int(code, 16): record["unicode"] for code, record in NORMALIZATION["characters"].items()}
SOURCE_INDEX = {source["key"]: index for index, source in enumerate(DATA["sources"])}
LANGS = {"en": "en", "pi": "pi", "pd": "pra", "ga": "pgd", "sa": "sa", "zh": "zh-Hant", "zh-pinyin": "zh-Latn-pinyin", "bo": "bo"}
WIDTHS = {"en": "min(540px, calc(100vw - 56px))", "pi": "320px", "pd": "340px", "ga": "320px", "sa": "345px", "zh": "230px", "zh-pinyin": "300px", "bo": "400px"}


def e(value):
    return escape(str(value), quote=True)


def reading_text(value):
    # Bilara's nonprinting join markers are formatting, not verse text.
    return value.replace("<j>", "").translate(CHARACTERS).strip()


def preferred_reading(record):
    return next((reading for reading in record["readings"] if reading.get("preferred")), next(iter(record["readings"]), None))


def annotated_line(text, annotations):
    """Preserve actual readings while making the source's uncertainty inspectable."""
    ranges = []
    for annotation in annotations:
        kind = annotation.get("kind")
        needle = reading_text(annotation.get("text", ""))
        if kind not in {"i", "em", "s"} or not needle:
            continue
        start = text.find(needle)
        if start >= 0:
            note = "Conjectural reading in the source edition" if kind == "i" else "Uncertain reading in the source edition" if kind == "em" else "Contextual line: the source marks this part as not corresponding to the Pāli"
            ranges.append((start, start + len(needle), note, "parallel-context" if kind == "s" else "uncertain-reading"))
    result, end = [], 0
    for start, stop, note, css_class in sorted(ranges):
        if start < end:
            continue
        result.extend([e(text[end:start]), f'<span class="{css_class}" title="{note}">{e(text[start:stop])}</span>'])
        end = stop
    result.append(e(text[end:]))
    return "".join(result)


def historical_notes():
    labels = {"pd": "Patna", "ga": "Gāndhārī", "sa": "Sanskrit", "zh": "Chinese", "bo": "Tibetan"}
    rows, details = [], []
    for number in READING_NUMBERS:
        chapter = next(chapter for chapter in CHAPTERS if chapter["start"] <= number <= chapter["end"])
        cells = [f'<th scope="row"><a href="{chapter["page"]}#dhp{number}">{number}</a></th>']
        for key, label in labels.items():
            record = WITNESS_INDEX[key][number]
            links = []
            for reading in record["readings"]:
                source = next(source for source in WITNESSES[key]["sources"] if source["id"] == reading["source_id"])
                url = reading.get("source_url") or source["url"]
                links.append(f'<a href="{e(url)}">{e(reading_text(reading["reference"]))}</a>')
                flags = []
                if reading.get("fragmentary"):
                    flags.append("Fragmentary text")
                if reading.get("partial_correspondence"):
                    flags.append("Partial correspondence")
                if record["status"] == "partial" and not flags:
                    flags.append("Partial correspondence")
                annotations = reading.get("annotations", [])
                uncertain = [reading_text(a["text"]) for a in annotations if a["kind"] == "em"]
                conjectural = [reading_text(a["text"]) for a in annotations if a["kind"] == "i"]
                if uncertain:
                    flags.append("Uncertain: " + "; ".join(uncertain))
                if conjectural:
                    flags.append("Conjectural: " + "; ".join(conjectural))
                for field in ["note", "notes"]:
                    value = reading.get(field)
                    if value:
                        flags.extend(value if isinstance(value, list) else [value])
                if flags:
                    details.append(f'<li><a href="{chapter["page"]}#dhp{number}">Pāli {number}</a> · {label} · {e(reading_text(reading["reference"]))}: {e(reading_text(" ".join(flags)))}</li>')
            text = '<br>'.join(links) if links else "No parallel located"
            if record["status"] == "partial":
                text += '<span class="parallel-status">Partial correspondence</span>'
            if record.get("note") and not any(record["note"] == reading.get("note") for reading in record["readings"]):
                details.append(f'<li>Pāli {number} · {label}: {e(record["note"])}</li>')
            cells.append(f'<td>{text}</td>')
        rows.append(f'<tr id="parallel-{number}">' + "".join(cells) + '</tr>')
    head = '<thead><tr><th scope="col">Pāli</th>' + ''.join(f'<th scope="col">{name}</th>' for name in labels.values()) + '</tr></thead>'
    table = '<div class="parallel-table-wrap"><table class="parallel-table"><caption class="sr-only">Source references for the selected Pāli verse positions</caption>' + head + '<tbody>' + ''.join(rows) + '</tbody></table></div>'
    details_html = '<details class="source-detail"><summary>Reading differences and uncertainties</summary><ul>' + ''.join(details) + '</ul></details>'
    links, seen = [], set()
    for data in WITNESSES.values():
        for source in data["sources"]:
            if source["url"] not in seen:
                seen.add(source["url"])
                links.append(f'<li><a href="{e(source["url"])}">{e(source["title"])} ↗</a></li>')
    return table + details_html, '<ul class="source-list">' + ''.join(links) + '</ul>'


def render(name, template=None, **values):
    text = (ROOT / "templates" / (template or name)).read_text(encoding="utf-8")
    values = {
        "STYLE_VERSION": hashlib.sha256((ROOT / "styles.css").read_bytes()).hexdigest()[:10],
        "READER_VERSION": hashlib.sha256((ROOT / "reader.js").read_bytes()).hexdigest()[:10],
        **values,
    }
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
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
            record = verse.get("witnesses", {}).get(key)
            reading = preferred_reading(record) if record else None
            reference = reading_text(reading["reference"]) if reading else "No parallel located in the consulted sources" if record else ""
            status = record["status"] if record else "unverified" if all(line is None for line in lines) else "present"
            if reference:
                label += f', {reference}'
            if status == "partial":
                reference += " · partial correspondence; see Notes"
                label += ", partial correspondence"
            if all(line is None for line in lines):
                content = '<p class="unlocated" lang="en"><span aria-hidden="true">—</span><span class="sr-only">' + e(reference or "Not yet verified") + '</span></p>' if profile == "historical" else '<p class="unverified" lang="en">Not yet verified.<span>Source and reading pending.</span></p>'
            else:
                rendered_lines = []
                for index, line in enumerate(lines):
                    segment = f' data-segment="{e(verse["segments"][index])}"' if "segments" in verse and key in {"en", "pi"} else ""
                    annotations = [a for a in reading.get("annotations", []) if a["line"] == index] if reading else []
                    text = annotated_line(reading_text(line), annotations) if line is not None else '<span class="unverified">Not yet verified</span>'
                    rendered_lines.append(f'<span class="poem-line"{segment}>{text}</span>')
                content = '<p class="poem">' + "".join(rendered_lines) + '</p>'
            poems.append(f'<section class="witness lang-{key}" data-language="{key}" data-reading-status="{status}" lang="{LANGS[key]}" aria-labelledby="{poem_id}" title="{e(reference)}"{hidden}><h3 class="sr-only" id="{poem_id}">{e(label)}</h3>{content}</section>')
        verse_html.append(
            f'<section class="verse" id="dhp{verse["no"]}" data-verse="{verse["no"]}" aria-labelledby="verse-title-{verse["no"]}">'
            f'<h2 class="sr-only" id="verse-title-{verse["no"]}">Verse {verse["no"]}</h2>'
            f'<div class="verse-grid" style="--line-count:{line_count}">' + "\n".join(poems) + '</div></section>'
        )
    render(name, template="index.html", TITLE=e(title), CHAPTER_ID=chapter_id, PAGE_KEY=name.removesuffix(".html"),
           PROFILE=profile, PREVIOUS_PAGE=e(previous), NEXT_PAGE=e(next_page), CHAPTER_TITLE=e(chapter_title),
           INITIAL_LOCATION=e(f'Verse {verses[0]["no"]}, {chapter_title}' if chapter_title else f'Verse 1 of {len(verses)}'),
           DESCRIPTION=e(f'Rosettapada — {title}. English and six historical textual traditions on one continuous reading sheet.' if profile == "historical" else 'Rosettapada — a two-verse comparative Dhammapada reading study.'),
           HELP_NOTE=e(help_note), COLUMN_HEADINGS="\n".join(headings), VERSES="\n".join(verse_html), LANGUAGE_SETTINGS="\n".join(settings))


sample_verses = [{"no": verse["no"], "lines": {
    source["key"]: PINYIN_VERSES[verse["no"]] if source["key"] == "zh-pinyin" else [row[SOURCE_INDEX[source["key"]]] for row in verse["rows"]]
    for source in SOURCES
}} for verse in VERSES]
sample_sources = [{**source, "reference": "Pāli working translation" if source["key"] == "en" else "Not yet verified" if source["key"] == "bo" else source["reference"]} for source in SOURCES]
render_reader("sample.html", sample_sources, sample_verses, "The pairs", "chapter1",
              help_note="Two verses are included in this earlier comparative sample. The English follows Pāli; alignment across traditions is provisional. The multilingual chapter pages are available in Contents.")

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
        lines = {"en": [reading_text(english[key]) for key in keys], "pi": [reading_text(root[key]) for key in keys]}
        witnesses = {key: WITNESS_INDEX[key][number] for key in WITNESSES}
        for key, record in list(witnesses.items()):
            reading = preferred_reading(record)
            lines[key] = [reading_text(line) for line in reading["lines"]] if reading else [None]
            if key == "zh":
                lines["zh-pinyin"] = reading["pinyin"] if reading else [None]
                witnesses["zh-pinyin"] = record
        verses.append({"no": number, "segments": keys, "lines": lines, "witnesses": witnesses})
    references = {"en": "Bhikkhu Sujato · Pāli", "pi": "Mahāsaṅgīti edition", "pd": "Dharmapada", "ga": "Dharmapada", "sa": "Udānavarga", "zh": "Historical Chinese recensions", "zh-pinyin": "Modern Mandarin reading aid", "bo": "Udānavarga · Toh 326"}
    sources = [{**source, "reference": references[source["key"]]} for source in SOURCES]
    navigation = PILOT_CHAPTERS if chapter["no"] in PILOT_NUMBERS else CHAPTERS
    position = navigation.index(chapter)
    previous_chapter = navigation[position - 1] if position else None
    next_chapter = navigation[position + 1] if position + 1 < len(navigation) else None
    previous = f'{previous_chapter["page"]}#dhp{previous_chapter["end"]}' if previous_chapter else ""
    next_page = f'{next_chapter["page"]}#dhp{next_chapter["start"]}' if next_chapter else ""
    render_reader(chapter["page"], sources, verses, chapter["title"], f'chapter{chapter["no"]}', profile="historical",
                  previous=previous, next_page=next_page, chapter_title=chapter["title"],
                  help_note="Selected Pāli chapters guide the order across six historical traditions. English follows Pāli. A dash marks a parallel not located in the consulted sources; fragments and uncertain readings are retained. Verse arrows continue through the selected chapters.")

# Preserve links shared before Pairs became the homepage.
(ROOT / "pairs.html").write_bytes((ROOT / CHAPTERS[0]["page"]).read_bytes())
def chapter_link(chapter):
    return f'<a class="toc-page-link" href="{chapter["page"]}#chapter{chapter["no"]}"><span>{e(chapter["title"])}</span><span class="toc-arrow" aria-hidden="true">↗</span></a>'
chapter_links = "\n".join(chapter_link(chapter) for chapter in PILOT_CHAPTERS)
secondary_links = "\n".join(chapter_link(chapter) for chapter in SECONDARY_CHAPTERS)
render("contents.html", CHAPTER_LINKS=chapter_links, SECONDARY_CHAPTER_LINKS=secondary_links)
parallel_table, historical_sources = historical_notes()
chapter_sources = "\n".join(f'<li><a href="https://suttacentral.net/{chapter["uid"]}/en/sujato">{e(chapter["title"])} · English and Pāli on SuttaCentral ↗</a></li>' for chapter in CHAPTERS)
pilot_positions = [number for chapter in PILOT_CHAPTERS for number in range(chapter["start"], chapter["end"] + 1)]
tibetan_counts = {status: sum(WITNESS_INDEX["bo"][number]["status"] == status for number in pilot_positions) for status in ["present", "partial", "not-located"]}
render("notes.html", BILARA_SOURCE_URL=f'https://github.com/suttacentral/bilara-data/tree/{COLLECTION["upstream"]["commit"]}', CHAPTER_SOURCES=chapter_sources, PARALLEL_TABLE=parallel_table, HISTORICAL_SOURCES=historical_sources,
       TIBETAN_PRESENT=tibetan_counts["present"], TIBETAN_PARTIAL=tibetan_counts["partial"], TIBETAN_NOT_LOCATED=tibetan_counts["not-located"],
       TIBETAN_ATTESTED=TIBETAN_AUDIT["summary"]["attested_lower_bound"])
dist = ROOT / "dist"
dist.mkdir(exist_ok=True)
for filename in ["sample.html", "pairs.html", "contents.html", "notes.html", "styles.css", "reader.js", ".nojekyll", *[chapter["page"] for chapter in CHAPTERS]]:
    shutil.copyfile(ROOT / filename, dist / filename)
shutil.copytree(ROOT / "assets", dist / "assets", dirs_exist_ok=True)
print(f"Built Rosettapada: {len(PILOT_CHAPTERS)} pilot chapters, {len(CHAPTERS)} available pages, {len(READING_NUMBERS)} Pāli verse positions with six historical traditions, English, and optional pinyin.")


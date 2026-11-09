"""Generate blend/index.html, the Rosettapada Blend workbench, from data/blend/.

The workbench is the owner's review surface on the live site. It is not linked from the reader.

    python3 tools/blend_workbench.py
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEYS = ["pi", "pd", "ga", "sa", "zh", "bo"]
NAMES = {"pi": "Pāli", "pd": "Patna", "ga": "Gāndhārī", "sa": "Sanskrit", "zh": "Chinese", "bo": "Tibetan"}
TIER_WORDS = {1: "agree", 2: "word choice", 3: "rule", 4: "judgment"}
SHOWN_KINDS = {"wording", "variant", "structure", "partial", "translation"}
STAGES = {
    "checkpoint-1": "Waiting for you: approve the rulings and rules below.",
    "drafting": "Claude is drafting the Blend.",
    "review": "Claude is reviewing the draft against the sources.",
    "checkpoint-2": "Waiting for you: choose the open judgments and read the draft.",
    "shipped": "Shipped to the reader.",
}


def e(value):
    return html.escape(str(value), quote=True)


def lang_attr(key):
    return {"zh": ' lang="zh-Hant"', "bo": ' lang="bo"', "pi": ' lang="pi"', "pd": ' lang="pra"', "ga": ' lang="pgd"', "sa": ' lang="sa"'}.get(key, "")


def load():
    rulings_path = ROOT / "data/blend/rulings.json"
    rulings = json.loads(rulings_path.read_text(encoding="utf-8"))["rulings"] if rulings_path.exists() else []
    chapters = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "data/blend/chapters").glob("*.json"))]
    return rulings, chapters


def ruling_card(r):
    options = "".join(
        f'<li{" class=\"recommended\"" if o.get("recommended") else ""}><b>{e(o["key"])}</b> {e(o["text"])}'
        f'{" <small>recommended</small>" if o.get("recommended") else ""}</li>'
        for o in r.get("options", []))
    verses = ", ".join(f'<a href="#v{n}">{n}</a>' for n in r.get("verses", []))
    decided = f'<p class="decided">Decided: {e(r["decided"])}</p>' if r.get("decided") else ""
    return (f'<article class="ruling" id="{e(r["id"])}"><header><span class="rid">{e(r["id"])}</span>'
            f'<span class="tier t{r["tier"]}">T{r["tier"]}</span><h3>{e(r["title"])}</h3></header>'
            f'<p>{e(r["statement"])}</p>{f"<ol class=options>{options}</ol>" if options else ""}'
            f'{decided}<p class="touches">Verses: {verses or "—"}</p></article>')


def decision_card(d):
    options = "".join(
        f'<li{" class=\"recommended\"" if o.get("recommended") else ""}><b>{e(o["key"])}</b> {e(o["text"])}'
        f'{" <small>leaning</small>" if o.get("recommended") else ""}</li>'
        for o in d["options"])
    lines = ", ".join(f'<a href="#v{l.split(".")[0]}">{e(l)}</a>' for l in d["lines"])
    chosen = f'<p class="decided">Decided: {e(d["decided"])}</p>' if d.get("decided") else ""
    return (f'<article class="ruling" id="{e(d["id"])}"><header><span class="rid">{e(d["id"])}</span><span class="tier t4">T4</span>'
            f'<h3>{e(d["title"])}</h3></header><p>{e(d["question"])}</p><ol class="options">{options}</ol>'
            f'<p class="lean">Claude: {e(d["lean"])}</p>{chosen}<p class="touches">Lines: {lines}</p></article>')


def differences(line):
    seen, out = set(), []
    for reader in ("A", "B"):
        for d in line["differences"].get(reader, []):
            if d.get("kind") not in SHOWN_KINDS:
                continue
            key = (tuple(d.get("witnesses", [])), d.get("kind"))
            if key in seen:
                continue
            seen.add(key)
            who = ", ".join(NAMES.get(w, w) for w in d.get("witnesses", []))
            out.append(f'<li><span class="who">{e(who)}</span> <span class="kind">{e(d.get("kind"))}</span> {e(d.get("note", ""))}</li>')
    return f'<ul class="diffs">{"".join(out)}</ul>' if out else ""


def aligned_texts(line, witnesses):
    rows = []
    for k in KEYS[1:]:
        if witnesses.get(k) == "not-located":
            continue
        text = line["aligned"]["A"].get(k) or line["aligned"]["B"].get(k)
        gloss = line["witness_glosses"]["A"].get(k) or line["witness_glosses"]["B"].get(k)
        partial = " (partial)" if witnesses.get(k) == "partial" else ""
        rows.append(f'<tr><th>{NAMES[k]}{partial}</th><td><span class="src"{lang_attr(k)}>{e(text) if text else "—"}</span>'
                    f'{f"<span class=wg>{e(gloss)}</span>" if gloss else ""}</td></tr>')
    return f'<details><summary>Show the other texts</summary><table class="aligned">{"".join(rows)}</table></details>' if rows else ""


def verse_block(v):
    dots = "".join(f'<span class="dot {v["witnesses"].get(k, "not-located")}" title="{NAMES[k]}: {e(v["witnesses"].get(k, "not-located"))}">{NAMES[k][:2]}</span>' for k in KEYS)
    rows = []
    for line in v["lines"]:
        gloss = line["gloss"]["A"] or line["gloss"]["B"] or ""
        split = ""
        if "readers disagree" in line["flags"]:
            split = f'<p class="split">Readers split: A said T{line["tiers"]["A"]}, B said T{line["tiers"]["B"]}. Taken as T{line["tier"]}.</p>'
        flag = '<p class="split">One reader was unsure.</p>' if "low confidence" in line["flags"] and not split else ""
        refs = line.get("rules", []) + ([line["decision"]] if line.get("decision") else [])
        rules = "".join(f'<a class="rule-ref" href="#{e(r)}">{e(r)}</a>' for r in refs)
        rows.append(f'<li class="line"><span class="tier t{line["tier"]}" title="{TIER_WORDS[line["tier"]]}">T{line["tier"]}</span>'
                    f'<div><p class="pi" lang="pi">{e(line["pi"])}</p><p class="gloss">{e(gloss)}</p>{rules}{split}{flag}'
                    f'{differences(line)}{aligned_texts(line, v["witnesses"])}</div></li>')
    blend = ""
    if v.get("blend"):
        blend = '<div class="blend"><p class="label">Rosettapada Blend · draft</p>' + "".join(f'<p>{e(l["text"])}</p>' for l in v["blend"]) + "</div>"
    return (f'<section class="verse-card" id="v{v["no"]}"><header><h3>Verse {v["no"]}</h3><span class="tier t{v["tier"]}">T{v["tier"]}</span>'
            f'<span class="dots">{dots}</span></header>{blend}<ol class="lines">{"".join(rows)}</ol></section>')


def chapter_section(c):
    lines = [l for v in c["verses"] for l in v["lines"]]
    counts = {t: sum(l["tier"] == t for l in lines) for t in (1, 2, 3, 4)}
    vcounts = {t: sum(v["tier"] == t for v in c["verses"]) for t in (1, 2, 3, 4)}
    split = sum("readers disagree" in l["flags"] for l in lines)
    bar = "".join(f'<span class="seg t{t}" style="flex:{counts[t]}" title="T{t}: {counts[t]} lines"></span>' for t in (1, 2, 3, 4) if counts[t])
    legend = "".join(f'<li><span class="tier t{t}">T{t}</span> {TIER_WORDS[t]} · {counts[t]} lines, {vcounts[t]} verses</li>' for t in (1, 2, 3, 4))
    ch = c["chapter"]
    open_decisions = [d for d in c.get("decisions", []) if not d.get("decided")]
    decisions = ""
    if c.get("decisions"):
        decisions = (f'<h3 class="sub">Questions only you can answer (T4) · {len(open_decisions)} open</h3>'
                     '<p class="note">These come back to you with the drafted verses at the second checkpoint. Answer now if you already know.</p>'
                     + "".join(decision_card(d) for d in c["decisions"]))
    return (f'<section class="chapter" id="chapter{ch["no"]}"><h2>{e(ch["title"])} <small>verses {ch["start"]}–{ch["end"]}</small></h2>'
            f'<p class="stage">{e(STAGES.get(c["stage"], c["stage"]))}</p>'
            f'<div class="bar">{bar}</div><ul class="legend">{legend}</ul>'
            f'<p class="note">{len(lines)} lines read twice, blind. The readers gave different tiers on {split}; those take the higher tier. A verse takes the tier of its hardest line.</p>'
            f'{decisions}<h3 class="sub">Verse by verse</h3>{"".join(verse_block(v) for v in c["verses"])}</section>')


CSS = """
body { overflow: auto; }
.wb, .wb .gloss, .wb .wg, .wb .lean { font-family: Georgia, 'Noto Serif', 'Rosettapada Tibetan', serif; }
.wb { max-width: 900px; margin: 0 auto; padding: 0 var(--padding) 120px; }
.wb-head { display: flex; align-items: center; justify-content: space-between; height: 96px; }
.wb h1 { font-size: 52px; font-weight: 400; letter-spacing: -.045em; margin: 24px 0 12px; }
.lede { font: italic 19px/1.6 Georgia, serif; color: var(--muted); margin: 0 0 40px; }
.wb h2 { font-size: 32px; font-weight: 400; letter-spacing: -.03em; margin: 72px 0 8px; padding-top: 24px; border-top: 1px solid #dedfd7; }
.wb h2 small { font: 15px system-ui, sans-serif; color: var(--muted); letter-spacing: 0; margin-left: 8px; }
.stage { font: 600 15px/1.5 system-ui, sans-serif; color: var(--accent); margin: 0 0 20px; }
.note { font-size: 16px; line-height: 1.6; color: #3d4339; margin: 0 0 32px; }
.tier { display: inline-grid; place-items: center; min-width: 30px; height: 22px; padding: 0 6px; border-radius: 999px; font: 600 12px/1 system-ui, sans-serif; flex: none; }
.t1 { background: #e3e6dc; color: #4a5544; } .t2 { background: #d9e3d0; color: #34452b; } .t3 { background: #ecdcb8; color: #6a4c12; } .t4 { background: #e9c7bd; color: #7a2e1c; }
.bar { display: flex; height: 10px; border-radius: 999px; overflow: hidden; margin: 0 0 12px; gap: 2px; }
.bar .seg { display: block; }
.legend { list-style: none; padding: 0; margin: 0 0 16px; display: flex; flex-wrap: wrap; gap: 8px 22px; font: 14px system-ui, sans-serif; color: var(--muted); }
.ruling { background: #fff; border: 1px solid #dedfd7; border-radius: 10px; padding: 22px 24px; margin: 0 0 18px; }
.ruling header { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 8px; }
.ruling h3 { font-size: 22px; font-weight: 400; margin: 0; flex-basis: 100%; }
.rid { font: 600 13px system-ui, sans-serif; letter-spacing: .04em; color: var(--accent); }
.ruling p { font-size: 17px; line-height: 1.65; margin: 0 0 12px; }
.options { margin: 0 0 12px; padding-left: 0; list-style: none; }
.options li { font-size: 17px; line-height: 1.6; padding: 8px 12px; border-radius: 6px; margin-bottom: 4px; }
.options li b { font-family: system-ui, sans-serif; margin-right: 6px; }
.options li.recommended { background: var(--hover); }
.options small { font: 12px system-ui, sans-serif; color: var(--accent); margin-left: 6px; }
.lean { font-style: italic !important; font-size: 16px !important; line-height: 1.6 !important; color: var(--accent); }
.wb h3.sub { font-size: 24px; font-weight: 400; margin: 48px 0 14px; }
.touches, .decided { font: 14px/1.5 system-ui, sans-serif !important; color: var(--muted); }
.verse-card { margin: 0 0 44px; }
.verse-card > header { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 10px; }
.verse-card h3 { font-size: 24px; font-weight: 400; margin: 0; }
.dots { display: inline-flex; gap: 4px; margin-left: auto; }
.dot { font: 11px/20px system-ui, sans-serif; width: 26px; text-align: center; border-radius: 4px; background: #e3e6dc; color: #4a5544; }
.dot.partial { background: none; border: 1px dashed #9aa293; line-height: 18px; }
.dot.not-located { background: none; color: #b9bdb2; text-decoration: line-through; }
.lines { list-style: none; padding: 0; margin: 0; }
.line { display: flex; gap: 14px; padding: 12px 0; border-top: 1px solid #e6e6df; }
.line > div { min-width: 0; flex: 1; }
.line .tier { margin-top: 4px; }
.pi { font-size: 20px; line-height: 1.5; margin: 0; }
.gloss { font: italic 16px/1.55 Georgia, serif; color: var(--muted); margin: 2px 0 0; }
.split { font: 13px/1.5 system-ui, sans-serif; color: #7a2e1c; margin: 6px 0 0; }
.diffs { margin: 8px 0 0; padding: 0; list-style: none; font-size: 15px; line-height: 1.55; color: #3d4339; }
.diffs li { margin-bottom: 4px; }
.who { font: 600 13px system-ui, sans-serif; }
.kind { font: 12px system-ui, sans-serif; color: var(--muted); border: 1px solid #d2d4cb; border-radius: 4px; padding: 0 4px; }
.rule-ref { font: 600 12px system-ui, sans-serif; color: var(--accent); margin-right: 8px; }
details { margin-top: 8px; }
summary { font: 13px system-ui, sans-serif; color: var(--muted); cursor: pointer; }
.aligned { border-collapse: collapse; margin-top: 6px; width: 100%; }
.aligned th { font: 13px system-ui, sans-serif; color: var(--muted); text-align: left; vertical-align: top; padding: 6px 12px 6px 0; white-space: nowrap; font-weight: 500; }
.aligned td { padding: 6px 0; font-size: 17px; line-height: 1.5; }
.aligned .src { display: block; }
.aligned .src[lang="bo"] { font-family: 'Rosettapada Tibetan', 'Kailasa', serif; }
.wg { display: block; font: italic 14px/1.5 Georgia, serif; color: var(--muted); }
.blend { background: #fff; border-left: 3px solid var(--accent); padding: 12px 18px; margin: 0 0 12px; }
.blend p { font-size: 20px; line-height: 1.6; margin: 0; }
.blend .label { font: 600 12px system-ui, sans-serif; letter-spacing: .08em; text-transform: uppercase; color: var(--accent); margin-bottom: 6px; }
@media (max-width: 760px) { .wb h1 { font-size: 40px; } .wb { padding: 0 20px 80px; } .dots { margin-left: 0; flex-basis: 100%; } .aligned th { white-space: normal; } }
"""


def build():
    rulings, chapters = load()
    waiting = [r for r in rulings if r["status"] == "proposed"]
    settled = [r for r in rulings if r["status"] != "proposed"]
    waiting_html = "".join(ruling_card(r) for r in waiting) or '<p class="note">Nothing is waiting for you.</p>'
    settled_html = f'<details><summary>{len(settled)} settled rulings and rules</summary>{"".join(ruling_card(r) for r in settled)}</details>' if settled else ""
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Blend workbench · Rosettapada</title><meta name="robots" content="noindex">
<link rel="stylesheet" href="../styles.css"><style>{CSS}</style></head>
<body><main class="wb">
<header class="wb-head"><a class="wordmark" href="../index.html"><img class="brand-mark" src="../assets/logo-carved.png" alt="" width="27" height="40">Rosettapada</a><nav class="top-nav"><a href="../index.html">Reader</a></nav></header>
<h1>Blend workbench</h1>
<p class="lede">Where the Rosettapada Blend is made. Each Pāli line is read twice, blind, against the other five traditions and given a tier. Rulings and rules waiting for you are listed first: answer in chat by ID, for example “R-T2-01 B”.</p>
<h2>Waiting for you</h2>
{waiting_html}
{settled_html}
{"".join(chapter_section(c) for c in chapters)}
</main></body></html>
"""
    target = ROOT / "blend/index.html"
    target.parent.mkdir(exist_ok=True)
    target.write_text(page, encoding="utf-8")
    return target


if __name__ == "__main__":
    print(build().relative_to(ROOT))

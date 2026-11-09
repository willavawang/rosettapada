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


def pickable(item_id, options, note="recommended"):
    return "".join(
        f'<li><button type="button" class="pick" data-for="{e(item_id)}" data-key="{e(o["key"])}" aria-pressed="false">'
        f'<b>{e(o["key"])}</b> <span>{e(o["text"])}</span>{f" <small>{note}</small>" if o.get("recommended") else ""}</button></li>'
        for o in options)


def is_choice(r):
    return all(len(o["key"]) == 1 for o in r.get("options", []))


def ruling_card(r):
    if is_choice(r):
        options = pickable(r["id"], r.get("options", []))
    else:
        options = "".join(f'<li class="term"><b>{e(o["key"])}</b> {e(o["text"])}</li>' for o in r.get("options", []))
    verses = ", ".join(f'<a href="#v{n}">{n}</a>' for n in r.get("verses", []))
    decided = f'<p class="decided">Decided: {e(r["decided"])}</p>' if r.get("decided") else ""
    return (f'<article class="ruling" id="{e(r["id"])}"><header><span class="rid">{e(r["id"])}</span>'
            f'<span class="tier t{r["tier"]}">T{r["tier"]}</span><h3>{e(r["title"])}</h3></header>'
            f'<p>{e(r["statement"])}</p>{f"<ol class=options>{options}</ol>" if options else ""}'
            f'{decided}<p class="touches">Verses: {verses or "—"}</p></article>')


def decision_card(d):
    options = pickable(d["id"], d["options"], "leaning")
    lines = ", ".join(f'<a href="#v{l.split(".")[0]}">{e(l)}</a>' for l in d["lines"])
    chosen = f'<p class="decided">Decided: {e(d["decided"])}</p>' if d.get("decided") else ""
    return (f'<article class="ruling" id="{e(d["id"])}"><header><span class="rid">{e(d["id"])}</span><span class="tier t4">T4</span>'
            f'<h3>{e(d["title"])}</h3></header><p>{e(d["question"])}</p><ol class="options">{options}</ol>'
            f'<p class="lean">Claude: {e(d["lean"])}</p>{chosen}<p class="touches">Lines: {lines}</p></article>')


def draft_line(segments, ref=""):
    out = []
    for seg in segments:
        if isinstance(seg, str):
            out.append(e(seg))
        else:
            out.append(f'<span role="button" tabindex="0" class="slot" data-slot="{e(seg["slot"])}" data-ref="{e(ref)}" data-options="{e(json.dumps(seg["options"], ensure_ascii=False))}" '
                       f'aria-haspopup="dialog">{e(next(iter(seg["options"].values())))}</span>')
    return "".join(out)


def current_english():
    path = ROOT / "data/english/pi.json"
    return json.loads(path.read_text(encoding="utf-8"))["verses"] if path.exists() else {}


CURRENT = current_english()


def draft_verse(v, link=True, compare=False):
    if not v.get("draft"):
        return ""
    head = f'<a class="dv-no" href="#v{v["no"]}">{v["no"]}</a>' if link else ""
    draft = '<div class="dv-draft">' + "".join("<p>" + draft_line(l["segments"], f'{v["no"]}.{l["line"]}') + "</p>" for l in v["draft"]) + "</div>"
    current = ""
    if compare:
        lines = CURRENT.get(str(v["no"]), {}).get("lines", [])
        current = '<div class="dv-current"><span class="dv-label">Current site</span>' + "".join(f"<p>{e(l)}</p>" for l in lines) + "</div>"
    return f'<div class="dv{" compare" if compare else ""}">{head}{draft}{current}</div>'


def draft_section(chapters):
    blocks = []
    for c in chapters:
        if any(v.get("draft") for v in c["verses"]):
            blocks.append(f'<h3 class="sub">{e(c["chapter"]["title"])}</h3>'
                          '<div class="dv-heads"><span>Rosettapada Blend · draft</span><span>Current site · from the Pāli</span></div>'
                          + "".join(draft_verse(v, compare=True) for v in c["verses"]))
    if not blocks:
        return ""
    return ('<h2>Read the draft</h2><p class="note">A first Literal+ draft, made from the two source readings, so you can judge each decision in the verses. '
            'Underlined words change with a decision: point at one (or tap it on a phone) to see the question, the original texts behind it, and the options to switch between. Your picks are listed at the bottom of the screen, ready to paste into chat. '
            'The draft has not yet been reviewed against the sources.</p>' + "".join(blocks))


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
    blend = f'<div class="blend"><p class="label">Draft</p>{draft_verse(v, link=False)}</div>' if v.get("draft") else ""
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
                     '<p class="note">Try each option in the draft above. Answer now, or wait until the draft has been reviewed.</p>'
                     + "".join(decision_card(d) for d in c["decisions"]))
    return (f'<section class="chapter" id="chapter{ch["no"]}"><h2>{e(ch["title"])} <small>verses {ch["start"]}–{ch["end"]}</small></h2>'
            f'<p class="stage">{e(STAGES.get(c["stage"], c["stage"]))}</p>'
            f'<div class="bar">{bar}</div><ul class="legend">{legend}</ul>'
            f'<p class="note">{len(lines)} lines read twice, blind. The readers gave different tiers on {split}; those take the higher tier. A verse takes the tier of its hardest line.</p>'
            f'{decisions}<h3 class="sub">Verse by verse</h3>{"".join(verse_block(v) for v in c["verses"])}</section>')


SCRIPT = """
(() => {
  const D = JSON.parse(document.getElementById('defaults').textContent);
  const KEY = 'rosettapada-blend-choices-v1';
  let picks = {};
  try { picks = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) {}
  const state = new Proxy(picks, { get: (t, id) => (id in t ? t[id] : D.keys[id]) });
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(picks)); } catch (e) {} };
  function render() {
    document.querySelectorAll('.slot').forEach(s => {
      const opts = JSON.parse(s.dataset.options);
      const k = state[s.dataset.slot] in opts ? state[s.dataset.slot] : Object.keys(opts)[0];
      s.textContent = opts[k];
      s.classList.toggle('changed', k !== D.keys[s.dataset.slot]);
    });
    document.querySelectorAll('.pick').forEach(b => b.setAttribute('aria-pressed', String(state[b.dataset.for] === b.dataset.key)));
    const parts = D.order.map(id => `${id} ${id in picks ? picks[id] : D.open.includes(id) ? '?' : D.keys[id]}`).concat(D.fixed);
    document.getElementById('answer-text').textContent = parts.join(' · ');
  }
  const P = JSON.parse(document.getElementById('pop-data').textContent);
  const pop = document.getElementById('pop');
  const esc = t => String(t ?? '').replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
  const LANG = {pi: 'pi', pd: 'pra', ga: 'pgd', sa: 'sa', zh: 'zh-Hant', bo: 'bo'};
  let current = null, pinned = false, hideTimer = null;
  function fill(slot) {
    const id = slot.dataset.slot, issue = P.issues[id] || {}, t = P.texts[slot.dataset.ref];
    const opts = (issue.options || []).map(o => `<li><button type="button" class="pick" data-for="${esc(id)}" data-key="${esc(o.key)}" aria-pressed="${state[id] === o.key}"><b>${esc(o.key)}</b> <span>${esc(o.text)}</span>${o.recommended ? ' <small>' + (issue.tier === 4 ? 'leaning' : 'recommended') + '</small>' : ''}</button></li>`).join('');
    const rows = t ? t.rows.map(r => `<tr class="${r.involved ? 'involved' : ''}"><th>${esc(r.name)}</th><td>${r.text ? `<span class="src" lang="${LANG[r.key] || ''}">${esc(r.text)}</span>` : '<span class="src none">—</span>'}${r.gloss ? `<span class="wg">${esc(r.gloss)}</span>` : ''}</td></tr>`).join('') : '';
    const notes = t && t.notes.length ? '<ul class="diffs">' + t.notes.map(n => `<li><span class="who">${esc(n.who)}</span> <span class="kind">${esc(n.kind)}</span> ${esc(n.note)}</li>`).join('') + '</ul>' : '';
    pop.innerHTML = `<div class="pop-issue"><p class="pop-id"><span class="rid">${esc(id)}</span> <span class="tier t${issue.tier}">T${issue.tier}</span> <button type="button" class="pop-close" aria-label="Close">×</button></p>
      <h3>${esc(issue.title)}</h3><p>${esc(issue.text)}</p><ol class="options">${opts}</ol>${issue.lean ? `<p class="lean">Claude: ${esc(issue.lean)}</p>` : ''}</div>
      ${t ? `<div class="pop-texts"><p class="pop-label">The texts · ${esc(t.label)}</p><table class="aligned">${rows}</table>${notes}<a class="pop-more" href="#v${t.verse}">Full line-by-line reading of verse ${t.verse} ↓</a></div>` : ''}`;
  }
  function place(slot) {
    const narrow = matchMedia('(max-width: 760px)').matches;
    pop.classList.toggle('sheet', narrow);
    if (narrow) { pop.style.left = pop.style.top = ''; return; }
    const r = slot.getBoundingClientRect();
    const w = Math.min(760, innerWidth - 32);
    pop.style.width = w + 'px';
    pop.style.left = Math.max(16, Math.min(r.left + scrollX, scrollX + innerWidth - w - 16)) + 'px';
    pop.style.maxHeight = '';
    const h = pop.offsetHeight, below = innerHeight - r.bottom - 84, above = r.top - 20;
    if (h > below && above > below) {
      const room = Math.min(h, above);
      pop.style.maxHeight = room + 'px';
      pop.style.top = (r.top + scrollY - room - 10) + 'px';
    } else {
      pop.style.maxHeight = Math.max(240, below) + 'px';
      pop.style.top = (r.bottom + scrollY + 10) + 'px';
    }
  }
  function show(slot, pin) {
    clearTimeout(hideTimer);
    document.querySelectorAll('.slot.active').forEach(s => s.classList.remove('active'));
    document.querySelectorAll(`.slot[data-slot="${slot.dataset.slot}"]`).forEach(s => s.classList.add('active'));
    current = slot; pinned = pin || pinned;
    fill(slot); pop.hidden = false; place(slot);
  }
  function hide() {
    pop.hidden = true; current = null; pinned = false;
    document.querySelectorAll('.slot.active').forEach(s => s.classList.remove('active'));
  }
  const hover = matchMedia('(hover: hover)').matches;
  if (hover) {
    document.addEventListener('mouseover', ev => {
      const slot = ev.target.closest('.slot');
      if (slot && !pinned) show(slot, false);
      else if (ev.target.closest('#pop')) clearTimeout(hideTimer);
    });
    document.addEventListener('mouseout', ev => {
      if (pinned) return;
      if (ev.target.closest('.slot') || ev.target.closest('#pop')) { clearTimeout(hideTimer); hideTimer = setTimeout(hide, 250); }
    });
  }
  document.addEventListener('click', ev => {
    const slot = ev.target.closest('.slot');
    if (slot) { if (pinned && current === slot) hide(); else show(slot, true); return; }
    if (ev.target.closest('.pop-close')) { hide(); return; }
    const pick = ev.target.closest('.pick');
    if (pick) { picks[pick.dataset.for] = pick.dataset.key; save(); render(); if (current) fill(current); return; }
    if (!ev.target.closest('#pop') && !pop.hidden) hide();
  });
  document.addEventListener('keydown', ev => { if (ev.key === 'Escape' && !pop.hidden) hide(); });
  document.addEventListener('keydown', ev => { if ((ev.key === 'Enter' || ev.key === ' ') && ev.target.classList && ev.target.classList.contains('slot')) { ev.preventDefault(); ev.target.click(); } });
  document.getElementById('copy-answers').addEventListener('click', ev => {
    const text = document.getElementById('answer-text').textContent;
    const done = () => { ev.target.textContent = 'Copied'; setTimeout(() => { ev.target.textContent = 'Copy'; }, 1500); };
    if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, () => {});
    else { const r = document.createRange(); r.selectNodeContents(document.getElementById('answer-text')); getSelection().removeAllRanges(); getSelection().addRange(r); }
  });
  render();
})();
"""

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
.patterns, .notable { list-style: none; padding: 0; margin: 0; }
.patterns li { font-size: 17px; line-height: 1.6; margin-bottom: 14px; }
.notable li { padding: 14px 0; border-top: 1px solid #e6e6df; }
.notable p { font-size: 17px; line-height: 1.6; margin: 0 0 4px; }
.wb:has(.dv.compare) { max-width: 1180px; }
.dv { display: flex; gap: 18px; margin: 0 0 26px; }
.dv.compare { display: grid; grid-template-columns: 22px minmax(0, 1fr) minmax(0, 1fr); gap: 0 28px; padding-bottom: 22px; border-bottom: 1px solid #e6e6df; }
.dv-heads { display: grid; grid-template-columns: 22px minmax(0, 1fr) minmax(0, 1fr); gap: 0 28px; margin: 0 0 14px; font: 600 12px/1.4 system-ui, sans-serif; letter-spacing: .08em; text-transform: uppercase; color: var(--accent); }
.dv-heads::before { content: ''; }
.dv-heads span:last-child { color: var(--muted); }
.dv-current p { color: var(--muted); }
.dv-label { display: none; font: 600 11px/1.4 system-ui, sans-serif; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin: 10px 0 2px; }
.dv p { font-size: 20px; line-height: 1.6; margin: 0; }
.dv-no { font: 13px/34px system-ui, sans-serif; color: var(--muted); min-width: 22px; text-decoration: none; }
.blend .dv p { font-size: 20px; }
.slot { cursor: pointer; color: #34452b; text-decoration: underline dotted #52614b; text-decoration-thickness: 2px; text-underline-offset: .28em; }
.slot:hover { color: var(--ink); text-decoration-style: solid; }
.slot.changed { color: #7a5612; text-decoration-color: #a07a22; }
.options .pick { display: block; width: 100%; text-align: left; padding: 8px 12px; border: 1px solid transparent; border-radius: 6px; background: none; font: inherit; font-size: 17px; line-height: 1.6; }
.options .pick:hover { background: var(--hover); }
.options .pick[aria-pressed="true"] { border-color: var(--ink); background: #fff; }
.options li { padding: 0 !important; }
.options li.term { padding: 6px 12px !important; }
.slot.active { background: #e8ecdf; color: var(--ink); text-decoration-style: solid; }
.pop { position: absolute; z-index: 8; max-height: min(70vh, 640px); overflow: auto; background: #fff; border: 1px solid #d6d8cf; border-radius: 12px; box-shadow: 0 18px 50px rgba(40, 45, 35, .18); display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.15fr); gap: 0 28px; padding: 20px 24px; }
.pop[hidden] { display: none; }
.pop h3 { font-size: 21px; font-weight: 400; margin: 0 0 8px; line-height: 1.3; }
.pop p { font-size: 15px; line-height: 1.6; margin: 0 0 10px; }
.pop .options .pick { font-size: 15px; padding: 6px 10px; }
.pop .lean { font-size: 14px !important; }
.pop-id { display: flex; align-items: center; gap: 8px; }
.pop-close { margin-left: auto; width: 32px; height: 32px; border: 0; border-radius: 50%; background: var(--hover); font: 20px/1 system-ui, sans-serif; }
.pop-label { font: 600 12px/1.4 system-ui, sans-serif !important; letter-spacing: .08em; text-transform: uppercase; color: var(--accent); margin: 4px 0 6px !important; }
.pop .aligned td { font-size: 16px; }
.pop .aligned tr:not(.involved) { opacity: .62; }
.pop .aligned tr.involved th { color: var(--ink); font-weight: 600; }
.pop .src.none { color: #b9bdb2; }
.pop .diffs { font-size: 14px; }
.pop-more { display: inline-block; margin-top: 6px; font: 13px system-ui, sans-serif; color: var(--muted); }
.pop.sheet { position: fixed; left: 0 !important; right: 0; bottom: 0; top: auto !important; width: auto !important; max-height: 78vh; border-radius: 16px 16px 0 0; grid-template-columns: 1fr; padding: 18px 20px 28px; z-index: 9; }
.answers { position: fixed; left: 0; right: 0; bottom: 0; z-index: 5; display: flex; align-items: center; gap: 14px; padding: 10px max(20px, calc((100vw - 900px) / 2)); background: var(--ink); color: var(--paper); font: 13px/1.45 system-ui, sans-serif; }
.answers p { margin: 0; flex: 1; max-height: 3.2em; overflow: auto; }
.answers button { flex: none; min-height: 36px; padding: 0 16px; border: 1px solid var(--paper); border-radius: 999px; background: none; color: var(--paper); font: 600 13px system-ui, sans-serif; }
.wb { padding-bottom: 160px; }
@media (max-width: 760px) { .dv.compare { grid-template-columns: 22px minmax(0, 1fr); } .dv.compare .dv-current { grid-column: 2; } .dv-heads { display: none; } .dv-label { display: block; } .dv-current p { font-size: 17px !important; } }
@media (max-width: 760px) { .wb h1 { font-size: 40px; } .wb { padding: 0 20px 220px; } .dots { margin-left: 0; flex-basis: 100%; } .aligned th { white-space: normal; } }
"""


WEIGHTS = {"doctrine": "doctrine", "practice": "practice", "imagery": "imagery", "translation": "how it was translated"}


def findings_section():
    path = ROOT / "data/blend/findings.json"
    if not path.exists():
        return ""
    f = json.loads(path.read_text(encoding="utf-8"))
    patterns = "".join(
        f'<li id="{e(p["id"])}"><span class="rid">{e(p["id"])}</span> <span class="kind">{e(p["status"])}</span> {e(p["statement"])}'
        f' <span class="touches">Evidence: {", ".join(f"<a href=#{e(x)}>{e(x)}</a>" for x in p["evidence"]) or "—"}'
        f'{"; against: " + ", ".join(e(x) for x in p["against"]) if p["against"] else ""} · chapters {", ".join(str(c) for c in p["chapters"])}</span></li>'
        for p in f["patterns"])
    notable = "".join(
        f'<li id="{e(n["id"])}"><p><span class="rid">{e(n["id"])}</span> <span class="kind">{e(WEIGHTS.get(n["weight"], n["weight"]))}</span> '
        f'{", ".join(f"<a href=#v{l.split(chr(46))[0]}>{e(l)}</a>" for l in n["lines"])}</p><p>{e(n["what"])}</p><p class="gloss">{e(n["why"])}</p>'
        f'<p class="touches">{" ".join(f"<a class=rule-ref href=#{e(r)}>{e(r)}</a>" for r in n["refs"])}</p></li>'
        for n in f["notable"])
    return (f'<h2>What we are learning</h2><p class="note">The record behind the home page’s account of how the traditions differ. '
            f'Patterns stay hypotheses until later chapters support or weaken them.</p><h3 class="sub">Patterns</h3><ul class="patterns">{patterns}</ul>'
            f'<h3 class="sub">Differences that matter</h3><ul class="notable">{notable}</ul>')


def popover_data(rulings, chapters):
    issues = {}
    for r in rulings:
        if is_choice(r):
            issues[r["id"]] = {"tier": r["tier"], "title": r["title"], "text": r["statement"], "options": r["options"], "lean": None, "decided": r.get("decided")}
    for c in chapters:
        for d in c.get("decisions", []):
            issues[d["id"]] = {"tier": 4, "title": d["title"], "text": d["question"], "options": d["options"], "lean": d.get("lean"), "decided": d.get("decided")}
    texts = {}
    for c in chapters:
        for v in c["verses"]:
            for dl in v.get("draft") or []:
                if all(isinstance(seg, str) for seg in dl["segments"]):
                    continue
                line = v["lines"][dl["line"] - 1]
                involved, notes, seen = set(), [], set()
                for reader in ("A", "B"):
                    for d in line["differences"].get(reader, []):
                        if d.get("kind") not in {"variant", "wording", "structure", "partial", "translation"}:
                            continue
                        involved |= set(d.get("witnesses", []))
                        key = (tuple(d.get("witnesses", [])), d.get("kind"))
                        if key not in seen:
                            seen.add(key)
                            notes.append({"who": ", ".join(NAMES.get(w, w) for w in d.get("witnesses", [])), "kind": d.get("kind"), "note": d.get("note", "")})
                rows = [{"key": "pi", "name": "Pāli", "text": line["pi"], "gloss": line["gloss"]["A"] or line["gloss"]["B"] or "", "involved": True}]
                for k in KEYS[1:]:
                    status = v["witnesses"].get(k)
                    if status == "not-located":
                        rows.append({"key": k, "name": NAMES[k], "text": None, "gloss": "not found for this verse", "involved": False})
                        continue
                    text = line["aligned"]["A"].get(k) or line["aligned"]["B"].get(k)
                    gloss = line["witness_glosses"]["A"].get(k) or line["witness_glosses"]["B"].get(k) or ""
                    rows.append({"key": k, "name": NAMES[k] + (" (partial)" if status == "partial" else ""), "text": text, "gloss": gloss, "involved": k in involved})
                texts[f'{v["no"]}.{dl["line"]}'] = {"label": f'Verse {v["no"]}, line {dl["line"]}', "verse": v["no"], "rows": rows, "notes": notes[:4]}
    return {"issues": issues, "texts": texts}


def build():
    rulings, chapters = load()
    waiting = [r for r in rulings if r["status"] == "proposed"]
    settled = [r for r in rulings if r["status"] != "proposed"]
    waiting_html = "".join(ruling_card(r) for r in waiting) or '<p class="note">Nothing is waiting for you.</p>'
    settled_html = f'<details><summary>{len(settled)} settled rulings and rules</summary>{"".join(ruling_card(r) for r in settled)}</details>' if settled else ""
    order, defaults = [], {}
    for item in [r for r in rulings if r["status"] == "proposed" and is_choice(r)] + [d for c in chapters for d in c.get("decisions", []) if not d.get("decided")]:
        order.append(item["id"])
        defaults[item["id"]] = next((o["key"] for o in item["options"] if o.get("recommended")), item["options"][0]["key"])
    open_items = [item["id"] for item in [d for c in chapters for d in c.get("decisions", []) if not d.get("decided")] if not any(o.get("recommended") for o in item["options"])]
    defaults = {"order": order, "keys": defaults, "open": open_items, "fixed": [r["id"] + " approve" for r in waiting if not is_choice(r)]}
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Blend workbench · Rosettapada</title><meta name="robots" content="noindex">
<link rel="stylesheet" href="../styles.css"><style>{CSS}</style></head>
<body><main class="wb">
<header class="wb-head"><a class="wordmark" href="../index.html"><img class="brand-mark" src="../assets/logo-carved.png" alt="" width="27" height="40">Rosettapada</a><nav class="top-nav"><a href="../index.html">Reader</a></nav></header>
<h1>Blend workbench</h1>
<p class="lede">Where the Rosettapada Blend is made. Each Pāli line is read twice, blind, against the other five traditions and given a tier. Read the draft, try the options, and paste your picks into chat.</p>
{draft_section(chapters)}
<h2>Rulings and rules waiting for you</h2>
{waiting_html}
{settled_html}
{"".join(chapter_section(c) for c in chapters)}
{findings_section()}
</main>
<div class="answers" id="answers"><p id="answer-text"></p><button type="button" id="copy-answers">Copy</button></div>
<div class="pop" id="pop" role="dialog" aria-modal="false" hidden></div>
<script type="application/json" id="pop-data">{json.dumps(popover_data(rulings, chapters), ensure_ascii=False).replace("<", "\\u003c")}</script>
<script type="application/json" id="defaults">{json.dumps(defaults, ensure_ascii=False)}</script>
<script>{SCRIPT}</script>
</body></html>
"""
    target = ROOT / "blend/index.html"
    target.parent.mkdir(exist_ok=True)
    target.write_text(page, encoding="utf-8")
    return target


if __name__ == "__main__":
    print(build().relative_to(ROOT))

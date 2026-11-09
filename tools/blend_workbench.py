"""Generate blend/index.html, the Rosettapada Blend workbench, from data/blend/.

The workbench is the owner's review surface on the live site, not linked from the reader.
It is organised by verse: the draft beside the current site's English, the open questions for
that verse with whole-line options, and on hover the line in all six traditions. Book-wide
word choices and the principles for weighing the traditions follow.

    python3 tools/blend_workbench.py
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEYS = ["pi", "pd", "ga", "sa", "zh", "bo"]
NAMES = {"pi": "Pāli", "pd": "Patna", "ga": "Gāndhārī", "sa": "Sanskrit", "zh": "Chinese", "bo": "Tibetan"}
SHOWN_KINDS = {"wording", "variant", "structure", "partial", "translation"}
TIER_WORDS = {1: "the traditions agree", 2: "a word choice", 3: "a difference a principle settles", 4: "needs judgment"}


def e(value):
    return html.escape(str(value), quote=True)


def load():
    rulings = json.loads((ROOT / "data/blend/rulings.json").read_text(encoding="utf-8"))
    chapters = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "data/blend/chapters").glob("*.json"))]
    english = ROOT / "data/english/pi.json"
    current = json.loads(english.read_text(encoding="utf-8"))["verses"] if english.exists() else {}
    return rulings, chapters, current


def default_key(item):
    return next((o["key"] for o in item.get("options", []) if o.get("recommended")), item["options"][0]["key"] if item.get("options") else None)


# ---------- verse cards ----------

def slot(seg):
    first = next(iter(seg["options"].values()))
    return f'<span class="slot" data-slot="{e(seg["slot"])}" data-options="{e(json.dumps(seg["options"], ensure_ascii=False))}">{e(first)}</span>'


def draft_lines(v):
    out = []
    for dl in v.get("draft") or []:
        text = "".join(e(s) if isinstance(s, str) else slot(s) for s in dl["segments"])
        out.append(f'<p class="dl" tabindex="0" data-ref="{v["no"]}.{dl["line"]}">{text}</p>')
    return "".join(out)


def option_buttons(item_id, options, note):
    return "".join(
        f'<li><button type="button" class="pick" data-for="{e(item_id)}" data-key="{e(o["key"])}" aria-pressed="false">'
        f'<b>{e(o["key"])}</b> <span>{e(o["text"])}</span>{f" <small>{note}</small>" if o.get("recommended") else ""}</button></li>'
        for o in options)


def question_card(q):
    settled = q.get("decided")
    head = f'<header><span class="qid">{e(q["id"])}</span><h4>{e(q["title"])}</h4>{"<span class=settled>settled</span>" if settled else ""}</header>'
    owner = f'<p class="owner"><span>You said</span> {e(q["owner"])}</p>' if q.get("owner") else ""
    body = f'<p>{e(q["text"])}</p>{owner}'
    if settled:
        return f'<article class="question done" id="q{e(q["id"])}">{head}{body}<p class="decided">{e(settled)}</p></article>'
    return (f'<article class="question" id="q{e(q["id"])}">{head}{body}<ol class="options">{option_buttons(q["id"], q["options"], "Claude leans")}</ol>'
            f'<p class="also">Or write your own version of the line.</p></article>')


def readers_notes(v):
    rows = []
    for line in v["lines"]:
        seen, diffs = set(), []
        for reader in ("A", "B"):
            for d in line["differences"].get(reader, []):
                key = (tuple(d.get("witnesses", [])), d.get("kind"))
                if d.get("kind") in SHOWN_KINDS and key not in seen:
                    seen.add(key)
                    who = ", ".join(NAMES.get(w, w) for w in d.get("witnesses", []))
                    diffs.append(f'<li><span class="who">{e(who)}</span> <span class="kind">{e(d.get("kind"))}</span> {e(d.get("note", ""))}</li>')
        split = f' · readers said T{line["tiers"]["A"]} and T{line["tiers"]["B"]}' if "readers disagree" in line["flags"] else ""
        diff_list = f'<ul class="diffs">{"".join(diffs)}</ul>' if diffs else ""
        rows.append(f'<li><p class="pi" lang="pi"><span class="tier t{line["tier"]}">T{line["tier"]}</span> {e(line["pi"])}<span class="split">{split}</span></p>'
                    f'<p class="gloss">{e(line["gloss"]["A"] or line["gloss"]["B"] or "")}</p>{diff_list}</li>')
    return f'<details class="notes"><summary>The two readers’ line-by-line notes</summary><ol class="rn">{"".join(rows)}</ol></details>'


def verse_card(v, questions, current, shown):
    dots = "".join(f'<span class="dot {v["witnesses"].get(k, "not-located")}" title="{NAMES[k]}: {e(v["witnesses"].get(k, "not-located"))}">{NAMES[k][:2]}</span>' for k in KEYS)
    tier = v.get("owner_tier") or v["tier"]
    cur = "".join(f"<p>{e(l)}</p>" for l in current.get(str(v["no"]), {}).get("lines", []))
    cards, pointers = [], []
    for qid in v.get("questions", []):
        if qid in shown:
            pointers.append(f'<a href="#q{e(qid)}">{e(qid)}</a>')
        else:
            shown.add(qid)
            cards.append(question_card(questions[qid]))
    see = f'<p class="see">Also changes with {", ".join(pointers)} above.</p>' if pointers else ""
    return (f'<section class="verse-card" id="v{v["no"]}"><header class="vh"><h3>Verse {v["no"]}</h3>'
            f'<span class="tier t{tier}" title="{e(TIER_WORDS[tier])}">T{tier}</span><span class="dots">{dots}</span></header>'
            f'<div class="pair"><div class="dv"><span class="col-label">Rosettapada Blend · draft</span>{draft_lines(v)}</div>'
            f'<div class="cur"><span class="col-label">Current site</span>{cur}</div></div>'
            f'{see}{"".join(cards)}{readers_notes(v)}</section>')


def chapter_section(c, current):
    questions = {q["id"]: q for q in c.get("questions", [])}
    open_count = sum(1 for q in questions.values() if not q.get("decided"))
    shown = set()
    ch = c["chapter"]
    tiers = [v.get("owner_tier") or v["tier"] for v in c["verses"]]
    summary = " · ".join(f'<span class="tier t{t}">T{t}</span> {sum(x == t for x in tiers)}' for t in (1, 2, 3, 4))
    return (f'<section class="chapter" id="chapter{ch["no"]}"><h2>{e(ch["title"])} <small>verses {ch["start"]}–{ch["end"]}</small></h2>'
            f'<p class="note">{e(c.get("draft_note", ""))} {open_count} questions open. Verses by tier: {summary}.</p>'
            f'{"".join(verse_card(v, questions, current, shown) for v in c["verses"])}</section>')


# ---------- words and principles ----------

def word_card(w):
    settled = '<span class="settled">settled</span>' if w["status"] == "decided" else ""
    head = f'<header><span class="qid">{e(w["id"])}</span><h4>{e(w["title"])}</h4>{settled}</header>'
    if w["status"] == "decided":
        return f'<article class="question done" id="w-{e(w["id"])}">{head}<p>{e(w["statement"])}</p><p class="decided">{e(w["decided"])}</p></article>'
    if all(len(o["key"]) == 1 for o in w["options"]):
        opts = f'<ol class="options">{option_buttons(w["id"], w["options"], "Claude recommends")}</ol>'
    else:
        opts = '<ul class="terms">' + "".join(f'<li><b>{e(o["key"])}</b> {e(o["text"])}</li>' for o in w["options"]) + "</ul>"
    return f'<article class="question" id="w-{e(w["id"])}">{head}<p>{e(w["statement"])}</p>{opts}</article>'


def principle_item(p):
    done = f' <span class="settled">{e(p["decided"])}</span>' if p.get("decided") else ""
    return f'<li id="{e(p["id"])}"><span class="qid">{e(p["id"])}</span> <b>{e(p["title"])}.</b> {e(p["statement"])}{done}</li>'


def findings_section():
    path = ROOT / "data/blend/findings.json"
    if not path.exists():
        return ""
    f = json.loads(path.read_text(encoding="utf-8"))
    notable = "".join(f'<li><p><span class="qid">{e(n["id"])}</span> {", ".join(e(l) for l in n["lines"])}: {e(n["what"])}</p><p class="gloss">{e(n["why"])}</p></li>' for n in f["notable"])
    return f'<details class="findings"><summary>Differences noted so far ({len(f["notable"])})</summary><ul class="notable">{notable}</ul></details>'


# ---------- hover data ----------

def popover_data(chapters):
    texts = {}
    for c in chapters:
        questions = {q["id"]: q for q in c.get("questions", [])}
        for v in c["verses"]:
            for line in v["lines"]:
                involved, notes, seen = set(), [], set()
                for reader in ("A", "B"):
                    for d in line["differences"].get(reader, []):
                        if d.get("kind") not in SHOWN_KINDS:
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
                    rows.append({"key": k, "name": NAMES[k] + (" (partial)" if status == "partial" else ""),
                                 "text": line["aligned"]["A"].get(k) or line["aligned"]["B"].get(k),
                                 "gloss": line["witness_glosses"]["A"].get(k) or line["witness_glosses"]["B"].get(k) or "",
                                 "involved": k in involved})
                q = questions.get(line.get("decision") or "")
                texts[f'{v["no"]}.{line["line"]}'] = {
                    "label": f'Verse {v["no"]}, line {line["line"]}', "rows": rows, "notes": notes[:4],
                    "question": {"id": q["id"], "title": q["title"], "decided": bool(q.get("decided"))} if q else None}
    return texts


SCRIPT = """
(() => {
  const D = JSON.parse(document.getElementById('defaults').textContent);
  const T = JSON.parse(document.getElementById('pop-data').textContent);
  const KEY = 'rosettapada-blend-choices-v2';
  let picks = {};
  try { picks = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) {}
  const pick = id => (id in picks ? picks[id] : D.keys[id]);
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(picks)); } catch (e) {} };
  const esc = t => String(t ?? '').replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
  const LANG = {pi: 'pi', pd: 'pra', ga: 'pgd', sa: 'sa', zh: 'zh-Hant', bo: 'bo'};
  function render() {
    document.querySelectorAll('.slot').forEach(s => {
      const opts = JSON.parse(s.dataset.options), k = pick(s.dataset.slot);
      s.textContent = opts[k in opts ? k : Object.keys(opts)[0]];
      s.classList.toggle('changed', k !== D.keys[s.dataset.slot]);
    });
    document.querySelectorAll('.pick').forEach(b => b.setAttribute('aria-pressed', String(pick(b.dataset.for) === b.dataset.key)));
    document.getElementById('answer-text').textContent = D.order.map(id => `${id} ${pick(id)}`).join(' · ');
  }
  const pop = document.getElementById('pop');
  let current = null, pinned = false, hideTimer = null;
  function fill(line) {
    const t = T[line.dataset.ref];
    if (!t) return false;
    const rows = t.rows.map(r => `<tr class="${r.involved ? 'involved' : ''}"><th>${esc(r.name)}</th><td>${r.text ? `<span class="src" lang="${LANG[r.key]}">${esc(r.text)}</span>` : '<span class="src none">—</span>'}${r.gloss ? `<span class="wg">${esc(r.gloss)}</span>` : ''}</td></tr>`).join('');
    const notes = t.notes.length ? '<ul class="diffs">' + t.notes.map(n => `<li><span class="who">${esc(n.who)}</span> <span class="kind">${esc(n.kind)}</span> ${esc(n.note)}</li>`).join('') + '</ul>' : '<p class="quiet">The readers found no difference of sense in this line.</p>';
    const q = t.question ? `<a class="pop-q" href="#q${esc(t.question.id)}">${esc(t.question.id)} · ${esc(t.question.title)}${t.question.decided ? ' (settled)' : ' ↓'}</a>` : '';
    pop.innerHTML = `<p class="pop-head"><span>${esc(t.label)}</span>${q}<button type="button" class="pop-close" aria-label="Close">×</button></p><table class="aligned">${rows}</table>${notes}`;
    return true;
  }
  function place(line) {
    const narrow = matchMedia('(max-width: 900px)').matches;
    pop.classList.toggle('sheet', narrow);
    if (narrow) { pop.style.left = pop.style.top = pop.style.maxHeight = pop.style.width = ''; return; }
    const r = line.getBoundingClientRect(), w = Math.min(600, innerWidth - 32);
    pop.style.width = w + 'px';
    pop.style.maxHeight = (innerHeight - 110) + 'px';
    const card = line.closest('.pair').getBoundingClientRect();
    pop.style.left = Math.max(16, Math.min(card.left + card.width / 2 + scrollX, scrollX + innerWidth - w - 16)) + 'px';
    const h = pop.offsetHeight;
    const top = r.top + h <= innerHeight - 84 ? r.top : Math.max(16, innerHeight - 84 - h);
    pop.style.top = (top + scrollY) + 'px';
  }
  function show(line, pin) {
    clearTimeout(hideTimer);
    if (!fill(line)) return;
    document.querySelectorAll('.dl.active').forEach(x => x.classList.remove('active'));
    line.classList.add('active');
    current = line; pinned = Boolean(pin);
    pop.hidden = false; place(line);
  }
  function hide() {
    pop.hidden = true; current = null; pinned = false;
    document.querySelectorAll('.dl.active').forEach(x => x.classList.remove('active'));
  }
  if (matchMedia('(hover: hover)').matches) {
    document.addEventListener('mouseover', ev => {
      const line = ev.target.closest('.dl');
      if (line && !pinned && line !== current) show(line, false);
      else if (line || ev.target.closest('#pop')) clearTimeout(hideTimer);
    });
    document.addEventListener('mouseout', ev => {
      if (!pinned && (ev.target.closest('.dl') || ev.target.closest('#pop'))) { clearTimeout(hideTimer); hideTimer = setTimeout(hide, 300); }
    });
  }
  document.addEventListener('click', ev => {
    const b = ev.target.closest('.pick');
    if (b) { picks[b.dataset.for] = b.dataset.key; save(); render(); return; }
    if (ev.target.closest('.pop-close')) { hide(); return; }
    if (ev.target.closest('.pop-q')) { hide(); return; }
    const line = ev.target.closest('.dl');
    if (line) { if (pinned && current === line) hide(); else show(line, true); return; }
    if (!ev.target.closest('#pop') && !pop.hidden) hide();
  });
  document.addEventListener('keydown', ev => {
    if (ev.key === 'Escape' && !pop.hidden) hide();
    if (ev.key === 'Enter' && ev.target.classList && ev.target.classList.contains('dl')) show(ev.target, true);
  });
  document.getElementById('copy-answers').addEventListener('click', ev => {
    const text = document.getElementById('answer-text').textContent;
    const done = () => { ev.target.textContent = 'Copied'; setTimeout(() => { ev.target.textContent = 'Copy'; }, 1500); };
    if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, () => {});
  });
  render();
})();
"""

CSS = """
body { overflow: auto; }
.wb, .wb .gloss, .wb .wg { font-family: Georgia, 'Noto Serif', 'Rosettapada Tibetan', serif; }
.wb { max-width: 1180px; margin: 0 auto; padding: 0 var(--padding) 180px; }
.wb-head { display: flex; align-items: center; justify-content: space-between; height: 96px; }
.wb h1 { font-size: 52px; font-weight: 400; letter-spacing: -.045em; margin: 24px 0 12px; }
.lede { font: italic 19px/1.6 Georgia, serif; color: var(--muted); margin: 0 0 12px; max-width: 820px; }
.how { font-size: 16px; line-height: 1.65; color: #3d4339; max-width: 820px; margin: 0 0 24px; }
.how b { font-family: system-ui, sans-serif; font-size: 14px; }
.wb h2 { font-size: 32px; font-weight: 400; letter-spacing: -.03em; margin: 64px 0 8px; padding-top: 24px; border-top: 1px solid #dedfd7; }
.wb h2 small { font: 15px system-ui, sans-serif; color: var(--muted); letter-spacing: 0; margin-left: 8px; }
.note { font-size: 16px; line-height: 1.6; color: #3d4339; margin: 0 0 28px; max-width: 820px; }
.tier { display: inline-grid; place-items: center; min-width: 30px; height: 22px; padding: 0 6px; border-radius: 999px; font: 600 12px/1 system-ui, sans-serif; vertical-align: 2px; }
.t1 { background: #e3e6dc; color: #4a5544; } .t2 { background: #d9e3d0; color: #34452b; } .t3 { background: #ecdcb8; color: #6a4c12; } .t4 { background: #e9c7bd; color: #7a2e1c; }
.verse-card { padding: 34px 0 30px; border-top: 1px solid #e3e3dc; }
.vh { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 14px; }
.vh h3 { font-size: 24px; font-weight: 400; margin: 0; }
.dots { display: inline-flex; gap: 4px; margin-left: auto; }
.dot { font: 11px/20px system-ui, sans-serif; width: 26px; text-align: center; border-radius: 4px; background: #e3e6dc; color: #4a5544; }
.dot.partial { background: none; border: 1px dashed #9aa293; line-height: 18px; }
.dot.not-located { background: none; color: #b9bdb2; text-decoration: line-through; }
.pair { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 0 44px; margin-bottom: 18px; }
.col-label { display: block; font: 600 11px/1.4 system-ui, sans-serif; letter-spacing: .08em; text-transform: uppercase; color: var(--accent); margin-bottom: 8px; }
.cur .col-label { color: var(--muted); }
.dl { font-size: 21px; line-height: 1.55; margin: 0 -8px; padding: 1px 8px; border-radius: 4px; cursor: help; }
.dl:hover, .dl.active { background: #eceee4; }
.dl:focus-visible { outline: 2px solid var(--accent); }
.cur p { font-size: 19px; line-height: 1.7; margin: 0; color: var(--muted); }
.slot { color: #34452b; text-decoration: underline dotted #52614b; text-decoration-thickness: 2px; text-underline-offset: .28em; }
.slot.changed { color: #7a5612; text-decoration-color: #a07a22; }
.see { font: 14px system-ui, sans-serif; color: var(--muted); margin: 0 0 12px; }
.question { background: #fff; border: 1px solid #dedfd7; border-radius: 10px; padding: 18px 22px; margin: 0 0 14px; max-width: 900px; }
.question.done { background: none; }
.question header { display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; margin-bottom: 6px; }
.question h4 { font-size: 20px; font-weight: 400; margin: 0; }
.qid { font: 600 13px system-ui, sans-serif; color: var(--accent); }
.settled { font: 600 12px system-ui, sans-serif; color: #4a5544; background: #e3e6dc; border-radius: 999px; padding: 2px 8px; }
.question p { font-size: 16px; line-height: 1.65; margin: 0 0 10px; }
.owner { border-left: 3px solid #d9cfae; padding-left: 12px; color: #4b4535; }
.owner span { display: block; font: 600 11px/1.6 system-ui, sans-serif; letter-spacing: .08em; text-transform: uppercase; color: #8a7a4a; }
.decided { font: 14px/1.55 system-ui, sans-serif !important; color: #34452b; }
.also { font: 13px system-ui, sans-serif !important; color: var(--muted); }
.options { margin: 4px 0 8px; padding: 0; list-style: none; }
.pick { display: block; width: 100%; text-align: left; padding: 8px 12px; border: 1px solid transparent; border-radius: 6px; background: none; font: inherit; font-size: 17px; line-height: 1.55; }
.pick:hover { background: var(--hover); }
.pick[aria-pressed="true"] { border-color: var(--ink); background: #fafaf6; }
.pick b { font-family: system-ui, sans-serif; margin-right: 6px; }
.pick small { font: 12px system-ui, sans-serif; color: var(--accent); margin-left: 6px; }
.terms { list-style: none; padding: 0; margin: 0; columns: 2; column-gap: 32px; font-size: 15px; line-height: 1.6; }
.terms li { break-inside: avoid; margin-bottom: 4px; }
.principles { list-style: none; padding: 0; margin: 0; max-width: 900px; }
.principles li { font-size: 17px; line-height: 1.65; margin-bottom: 14px; }
details.notes, details.findings { margin-top: 10px; }
summary { font: 13px system-ui, sans-serif; color: var(--muted); cursor: pointer; }
.rn { list-style: none; padding: 0; margin: 10px 0 0; }
.rn li { padding: 8px 0; border-top: 1px solid #ecece6; }
.rn .pi { font-size: 17px; margin: 0; }
.split { font: 12px system-ui, sans-serif; color: #7a2e1c; }
.gloss { font: italic 15px/1.5 Georgia, serif; color: var(--muted); margin: 2px 0 0; }
.diffs { margin: 6px 0 0; padding: 0; list-style: none; font-size: 14px; line-height: 1.55; color: #3d4339; }
.diffs li { margin-bottom: 4px; }
.who { font: 600 12px system-ui, sans-serif; }
.kind { font: 11px system-ui, sans-serif; color: var(--muted); border: 1px solid #d2d4cb; border-radius: 4px; padding: 0 4px; }
.notable { list-style: none; padding: 0; }
.notable li { padding: 10px 0; border-top: 1px solid #ecece6; font-size: 15px; }
.notable p { margin: 0 0 4px; }
.pop { position: absolute; z-index: 8; overflow: auto; background: #fff; border: 1px solid #d6d8cf; border-radius: 12px; box-shadow: 0 18px 50px rgba(40, 45, 35, .18); padding: 16px 20px 18px; }
.pop[hidden] { display: none; }
.pop-head { display: flex; align-items: center; gap: 12px; margin: 0 0 8px; font: 600 12px/1.4 system-ui, sans-serif; letter-spacing: .06em; text-transform: uppercase; color: var(--accent); }
.pop-q { text-transform: none; letter-spacing: 0; font-weight: 500; color: #7a5612; }
.pop-close { margin-left: auto; width: 30px; height: 30px; border: 0; border-radius: 50%; background: var(--hover); font: 19px/1 system-ui, sans-serif; flex: none; }
.aligned { border-collapse: collapse; width: 100%; }
.aligned th { font: 13px system-ui, sans-serif; color: var(--muted); text-align: left; vertical-align: top; padding: 6px 14px 6px 0; white-space: nowrap; font-weight: 500; }
.aligned td { padding: 5px 0; font-size: 16px; line-height: 1.45; }
.aligned tr:not(.involved) { opacity: .6; }
.aligned tr.involved th { color: var(--ink); font-weight: 600; }
.src { display: block; }
.src[lang="bo"] { font-family: 'Rosettapada Tibetan', 'Kailasa', serif; }
.src.none { color: #b9bdb2; }
.wg { display: block; font: italic 14px/1.45 Georgia, serif; color: var(--muted); }
.quiet { font-size: 14px; color: var(--muted); margin: 8px 0 0; }
.pop .diffs { margin-top: 10px; }
.pop.sheet { position: fixed; left: 0 !important; right: 0; bottom: 0; top: auto !important; width: auto !important; max-height: 72vh; border-radius: 16px 16px 0 0; z-index: 9; padding-bottom: 28px; }
.answers { position: fixed; left: 0; right: 0; bottom: 0; z-index: 5; display: flex; align-items: center; gap: 14px; padding: 10px max(20px, calc((100vw - 1180px) / 2 + 20px)); background: var(--ink); color: var(--paper); font: 13px/1.45 system-ui, sans-serif; }
.answers p { margin: 0; flex: 1; max-height: 3.2em; overflow: auto; }
.answers button { flex: none; min-height: 36px; padding: 0 16px; border: 1px solid var(--paper); border-radius: 999px; background: none; color: var(--paper); font: 600 13px system-ui, sans-serif; }
@media (max-width: 900px) { .pair { grid-template-columns: 1fr; } .cur { margin-top: 14px; padding-top: 10px; border-top: 1px dashed #dcdcd4; } .cur p { font-size: 16px; } .dl { cursor: pointer; } }
@media (max-width: 760px) { .wb h1 { font-size: 40px; } .wb { padding: 0 20px 220px; } .dots { margin-left: 0; flex-basis: 100%; } .terms { columns: 1; } .dl { font-size: 19px; } }
"""


def build():
    rulings, chapters, current = load()
    words, principles = rulings["words"], rulings["principles"]
    order, keys = [], {}
    for c in chapters:
        for q in c.get("questions", []):
            if not q.get("decided") and q.get("options"):
                order.append(q["id"])
                keys[q["id"]] = default_key(q)
    for w in words:
        if w["status"] == "proposed" and all(len(o["key"]) == 1 for o in w["options"]):
            order.append(w["id"])
            keys[w["id"]] = default_key(w)
    defaults = {"order": order, "keys": keys}
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Blend workbench · Rosettapada</title><meta name="robots" content="noindex">
<link rel="stylesheet" href="../styles.css"><style>{CSS}</style></head>
<body><main class="wb">
<header class="wb-head"><a class="wordmark" href="../index.html"><img class="brand-mark" src="../assets/logo-carved.png" alt="" width="27" height="40">Rosettapada</a><nav class="top-nav"><a href="../index.html">Reader</a></nav></header>
<h1>Blend workbench</h1>
<p class="lede">The Rosettapada Blend, verse by verse: the draft beside the current site, and under each verse the questions it raises.</p>
<p class="how">Point at any line of the draft (or tap it on a phone) to see that line in all six traditions. Questions are named by verse and line, like <b>1.2</b>; their options are whole lines, and choosing one rewrites the draft. Answer in chat with the bar at the bottom, in your own words, or with your own version of a line or verse. If a verse's tier looks wrong to you, say so: the tier only shows where the hard choices are.</p>
{"".join(chapter_section(c, current) for c in chapters)}
<h2>Words for the whole book</h2>
<p class="note">Choices that apply wherever the word appears. Settled ones are kept with your reasons.</p>
{"".join(word_card(w) for w in words)}
<h2>Principles</h2>
<p class="note">How the first draft weighs the traditions. They set the starting point and flag departures; they never stop you choosing the best reading. Say “agree”, or change any of them.</p>
<ul class="principles">{"".join(principle_item(p) for p in principles)}</ul>
{findings_section()}
</main>
<div class="pop" id="pop" role="dialog" aria-modal="false" hidden></div>
<div class="answers" id="answers"><p id="answer-text"></p><button type="button" id="copy-answers">Copy</button></div>
<script type="application/json" id="pop-data">{json.dumps(popover_data(chapters), ensure_ascii=False).replace("<", "\\u003c")}</script>
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

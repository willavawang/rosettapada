# Rosettapada Blend — method (for agents)

The Rosettapada Blend is the site's own English Dhammapada, drawn from all six traditions on the sheet. It will replace the Pāli-based placeholder in the English column, chapter by chapter. Decisions below were made by the project owner on 2026-11-08/09; do not reopen them without being asked.

## Decisions

- **Name:** Rosettapada Blend. The subheading is undecided.
- **Aim:** the best reading wherever it appears. A lone reading or a Chinese image can be the best reading; principles only set the first draft (below).
- **Voice: Literal+.** Translate literally. Depart from the literal only when (1) the literal English is unclear or misleading, or (2) the original has a poetic quality that a literal rendering loses. After a batch is drafted, a separate **style layer** pass may even out unevenness (for example, thinly attested verses that read differently). Never import metaphysics the source does not state ("eternal law" for *sanantano* asserts eternity). **The original's own poetry belongs in Literal+, now**, not in the style pass: e.g. the Pāli's terse three-fold *mano-* in verse 1 (owner, 2026-11-09). The style pass is only for evenness across the book. English must stay intelligible as a set: a word's plural and negation must read naturally ("hostilities", "non-hostility" do not), so recast the line rather than force the word.
- **Conventions already fixed for the site's English:** traditional voicing (do not neutralize the original's gender), "mendicant", "brahmin", line-for-line with the verse, brackets: […] lacuna, [restored], ⟨supplied⟩.
- **Readers see only the translation.** No per-line source display. Provenance is kept internally (below) and is mandatory.
- **Scope:** all 423 Pāli verse positions, all 26 chapters. Verses that exist only in other traditions are a separate later phase (logs/backlog.md).
- **Release:** chapter 1 (Pairs), then 3 chapters, then 7, then the remaining 15.
- **Review:** the project owner and Claude only. No outside expert.

## How work is organised (revised 2026-11-09 after the owner's first review)

The owner found word-level toggles and issue-level tiers too rigid: most choices change a whole line or verse, a tier fixed on an issue hides where we disagree, and the owner thinks about verses as wholes. So:

- **Questions belong to verses and lines**, named by where they occur: `1.2` (verse 1, line 2), `5` (a whole verse). Options are **whole lines** (or a whole verse), never single words. The owner may answer with a letter, in their own words, or with their own version; record their words in `owner` and the outcome with date in `decided`.
- **Tiers are triage, not law.** A line's tier says how much judgment it needs (T1 the traditions agree; T2 a word choice; T3 a difference a principle settles; T4 needs judgment). A verse takes its hardest line. Tiers are never attached to rulings or issues. If the owner says a verse's tier is wrong, set `owner_tier` on the verse.
- **Words for the whole book** (`words` in `data/blend/rulings.json`, ids like `vera`, `mara`, `samana`): renderings that apply wherever the word appears. No tier. A word may be decided as "by context" (e.g. `dhamma`), which sends each occurrence to a verse question.
- **Principles** (`principles`, ids `rule-1`…): defaults for weighing the traditions in the first draft. They flag departures; they never stop the owner choosing the best reading.
- The draft starts from Claude's leanings; the workbench shows it beside the current site, with every line's six source texts on hover.

### Uncertainty and single witnesses

Uncertainty moves a line's tier **up**, never down. A line with a single witness is T1 "unopposed", not "agreed".

### Witness relationships (count lineages, not columns)

- Pāli (Theravāda) and Patna are often very close; agreement between them is weaker evidence than agreement between distant witnesses.
- The Tibetan (Toh 326) is a translation of the Udānavarga, so Sanskrit + Tibetan is **one** line of transmission. Where they differ from each other, that is usually a Tibetan translation matter.
- The Gāndhārī is the oldest manuscript, but it survives in fragments; fragmentary lines are weak alone.
- The Chinese (T210 Faju jing, 3rd century; some positions fall back to T212/T213) translates a lost Indic text, often freely and with native vocabulary (道, 法). It is evidence for its Indic source *and* for how an early reader understood it.

## Guards against compounding errors

1. **Source-first.** Readings and drafts are made from the original-language texts only (`python3 tools/blend_packet.py <chapter>`). Do **not** read the site's English while reading or drafting: `data/english/*`, `data/pali/*translation-en-sujato*`, generated `*.html` pages, `logs/translation-review*`, `logs/backlog.md`. Those are cross-checks for *after* a draft exists.
2. **Two blind readings.** Two independent passes align and tier each chapter without seeing each other. Where they disagree on tier, the higher tier wins and the line is flagged.
3. **Provenance is mandatory** (internal). Every Blend line records the witnesses it rests on, its tier, and the words, principles or questions it relies on. Changing one, or correcting a witness, flags every dependent line. `tools/check.py` enforces the data shape.
4. **Release gate.** A chapter ships only when every open question is decided by the owner and an independent review of the draft against the sources is clean.

## The knowledge record (light touch)

Owner's instruction (2026-11-09): keep this minimal; the translation comes first, analysis happens after the translation is finished, and the home page will say only a couple of sentences on it.

- While reading a chapter, add a one-line entry to `data/blend/findings.json` → `notable` only for a striking difference between traditions (a few per chapter at most). Do not spend extra time on it.
- Leave `patterns` as they are until the translation is complete; do not update or promote them per chapter.
- When the owner settles a question, word or principle, record the choice, the reason if given, and the date in `decided`.

## Files

- `tools/blend_packet.py N`: source packet for chapter N (original texts, statuses, references; no English).
- `tools/blend_merge.py`: merges two blind readings into the chapter file; raw readings are kept in `data/blend/readings/`.
- `data/blend/rulings.json`: `words` (id, title, status proposed | decided, statement, options, decided) and `principles` (id, title, statement, status, decided).
- `data/blend/chapters/NN-slug.json`: per chapter: `questions` (id = verse.line or verse, verses, lines, title, text, options with whole-line text joined by " / " across the lines or verses they cover, owner, decided); per verse: `lines` (Pāli line, both readers' alignment, glosses, differences, tiers, flags, word/principle refs, `decision` = question id), `tier`, optional `owner_tier`, `questions`, `draft` (line-for-line segments; a slot names a question or word and holds each option's text), `blend` (null until shipped).
- `blend/index.html`: the workbench on the live site (not linked from the reader), generated by `tools/blend_workbench.py`, which `build.py` runs.

## Stages per chapter

1. Packet → two blind readings (alignment, glosses and tier per line, candidate questions).
2. Merge; draft Literal+ from the readings, with whole-line options wherever a question is open; show beside the current site.
3. Owner review on the workbench: answers questions, words and principles, in their own words where they like.
4. Revise the draft; independent review of it against the sources; only then cross-check against the site's existing English.
5. Owner reads the final chapter on the workbench.
6. Ship: the chapter's English column switches to the Blend.

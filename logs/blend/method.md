# Rosettapada Blend — method (for agents)

The Rosettapada Blend is the site's own English Dhammapada, drawn from all six traditions on the sheet. It will replace the Pāli-based placeholder in the English column, chapter by chapter. Decisions below were made by the project owner on 2026-11-08/09; do not reopen them without being asked.

## Decisions

- **Name:** Rosettapada Blend. The subheading is undecided.
- **Aim:** the best reading wherever it appears. The degree of authority we exercise is set by tier (below).
- **Voice: Literal+.** Translate literally. Depart from the literal only when (1) the literal English is unclear or misleading, or (2) the original has a poetic quality that a literal rendering loses. After a batch is drafted, a separate **style layer** pass may even out unevenness (for example, thinly attested verses that read differently). Never import metaphysics the source does not state. Example: "eternal law" for *sanantano* asserts eternity; whether to say "age-old" or "eternal" is a ruling, not a stylistic whim.
- **Conventions already fixed for the site's English:** traditional voicing (do not neutralize the original's gender), "mendicant", "brahmin", line-for-line with the verse, brackets: […] lacuna, [restored], ⟨supplied⟩.
- **Readers see only the translation.** No per-line source display. Provenance is kept internally (below) and is mandatory.
- **Scope:** all 423 Pāli verse positions, all 26 chapters. Verses that exist only in other traditions are a separate later phase (logs/backlog.md).
- **Release:** chapter 1 (Pairs), then 3 chapters, then 7, then the remaining 15.
- **Review:** the project owner and Claude only. No outside expert.

## Tiers

Tier is set **per line** (Pāli pāda line); a verse takes its highest line tier. Uncertainty moves a line **up**, never down. A line with a single witness is T1 "unopposed", not "agreed".

| Tier | Meaning | Who decides |
|---|---|---|
| T1 | All present witnesses agree in sense. Spelling, dialect and grammar-neutral differences do not count. A Chinese or Tibetan rendering that renders the same Indic sense counts as agreement. | Claude: translation craft only. |
| T2 | Same idea, different word choice, or a word whose English rendering must be fixed once for the whole book (e.g. *dhammā*: states/phenomena/experience; Chinese 道 "the Way" rendering the Indic "goal/good"; *sanantano*). | A **ruling** (R-T2-nn), approved once by the owner, then applied everywhere. |
| T3 | A real difference of sense at line or verse level that a general rule can settle (e.g. one lineage against the rest; Sanskrit and Tibetan agreeing against all others counts as one voice; a partial parallel informing but not supplying a line; a fragmentary witness unable to carry a reading alone; a Chinese paraphrase). | A **rule** (R-T3-nn), approved once, applied case by case, spot-checked. |
| T4 | Needs its own judgment about what the text says or which reading is best. | Claude lays out 2–3 options; the owner chooses. |

### Witness relationships (count lineages, not columns)

- Pāli (Theravāda) and Patna are often very close; agreement between them is weaker evidence than agreement between distant witnesses.
- The Tibetan (Toh 326) is a translation of the Udānavarga, so Sanskrit + Tibetan is **one** line of transmission. Where they differ from each other, that is usually a Tibetan translation matter.
- The Gāndhārī is the oldest manuscript, but it survives in fragments; fragmentary lines are weak alone.
- The Chinese (T210 Faju jing, 3rd century; some positions fall back to T212/T213) translates a lost Indic text, often freely and with native vocabulary (道, 法). It is evidence for its Indic source *and* for how an early reader understood it.

## Guards against compounding errors

1. **Source-first.** Readings and drafts are made from the original-language texts only (`python3 tools/blend_packet.py <chapter>`). Do **not** read the site's English while reading or drafting: `data/english/*`, `data/pali/*translation-en-sujato*`, generated `*.html` pages, `logs/translation-review*`, `logs/backlog.md`. Those are cross-checks for *after* a draft exists.
2. **Two blind readings.** Two independent passes align and tier each chapter without seeing each other. Where they disagree on tier, the higher tier wins and the line is flagged.
3. **Provenance is mandatory** (internal). Every Blend line records the witnesses it rests on, its tier, and any ruling or rule IDs it relies on. Changing a ruling or correcting a witness flags every dependent line. `tools/check.py` enforces the data shape.
4. **Release gate.** A chapter ships only when every T4 is decided by the owner and an independent review of the draft against the sources is clean.

## The knowledge record

The site's purpose is a scholarly account of the Dhammapada tradition, not only a translation. The Blend work must leave a record we can speak from, and the home page's introduction will be written from it.

- **Differences that matter** (`data/blend/findings.json` → `notable`): every real variant at T3/T4, and any T2 choice with consequences, gets an entry: lines, witnesses, what differs, and *why it matters* to a reader or practitioner (weight: doctrine, practice, imagery, or translation). Spelling and same-sense wording do not.
- **Patterns** (`patterns`): cross-verse observations stated as hypotheses, with the notable entries for and against, and the chapters checked. Each new chapter must update them: add evidence, add counter-evidence, or mark them supported, weakened or dropped. Do not promote a pattern on one chapter.
- **Decisions keep their reasons.** When the owner settles a ruling, rule or T4, record the choice and the reason (in their words where given) and the date in `decided`.
- **The home page statement** is drafted from this record at each release milestone (after 1, 3, 7 and all 26 chapters) and claims only what the record supports.

## Files

- `tools/blend_packet.py N` — source packet for chapter N (original texts, statuses, references; no English).
- `data/blend/rulings.json` — T2 rulings and T3 rules: `id`, `tier`, `status` (proposed | approved | rejected | revised), `title`, `statement`, `options`, `verses`, `decided`.
- `data/blend/chapters/NN-slug.json` — per chapter: stage, readings summary, and per verse: `lines` (Pāli line, aligned witness text, differences, tier, rule refs, flags), `tier`, `blend` (null until drafted), `status`.
- `blend/index.html` — the workbench on the live site (not linked from the reader), generated by `python3 tools/blend_workbench.py`, which `build.py` runs. The owner reviews here and answers in chat by ID.

## Stages per chapter

1. Packet → two blind readings (alignment + tier per line + candidate rulings/rules).
2. Merge: compare tiers, escalate disagreements, write the chapter file; propose rulings/rules.
3. Owner checkpoint 1: approve rulings/rules.
4. Draft Literal+ Blend from the sources with provenance; prepare T4 options.
5. Independent review of the draft against the sources; only then cross-check against the site's existing English.
6. Owner checkpoint 2: T4 decisions; read the chapter on the workbench.
7. Ship: the chapter's English column switches to the Blend.

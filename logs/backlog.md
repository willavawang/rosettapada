# Translation backlog

Open items from the translation review (`translation-review-ranked.md`), parked for later. Nothing here is applied.

## Small decisions (Tier 4, deferred 2026-11-08)

- [ ] **甘露 in the Chinese.** Rendered "the deathless" at zh 21, 411 and "sweet dew" at zh 114, 226, 374. Choose one, and put the other in a note. (#59, raw F4)
- [ ] **Witness spellings of names.** Patna's "Ādhora" is kept as printed at pd 227, while Gāndhārī "adura" is normalized to "Atula" at ga 227. Either keep each manuscript's form or normalize both. (#60, raw C17)
- [ ] **dharmā in verses 1–2.** The same Indic word reads "all states" (pd), "experience" (ga, Pāli-based English) and "phenomena" (sa, bo). Use one rendering unless the difference is meant. (#61, raw E3)
- [ ] **Chapter title "Monastics".** The English now says "mendicant" throughout. The chapter could be titled "Mendicants"; its URL (monastics.html) stays either way.

## Tier 5: refinements (#62–95, #122)

About 35 moderate-confidence wording improvements, such as "Māra's flower-tipped arrows" (pi 46) and "a person of insight" (zh 193). See the ranked list.

## Tier 6: needs a source check (#96–116)

- [ ] sa 218 *avasrāvī*: both editions print it, but the English "not flowing out" negates it. Drop "not" once a reading is chosen.
- [ ] Uncertain construals in the Chinese and Tibetan (zh 204, 205, 271, 34; bo 44–45, 151, 153, 371, 383), the Gāndhārī (280, 294), and the Patna (73, 83, 236).
- [ ] pi 143 *niddaṁ*/*nindaṁ*; pi 355 "as well as others"; pi 39 "seepage"; sa 54 *vāhnija*; zh 69/119 shared-stanza note.
- [ ] A second reader for the Chinese and Tibetan translations, where most of the meaning errors were found.

## Rosettapada Blend (pilot under way: see logs/blend/method.md and blend/index.html)

- [ ] Write the Blend: one English rendering per verse that draws on all six traditions, picking the best reading from each or building it up from what they show together. Until then the English column ("Rosettapada Blend · from the Pāli for now") shows the Pāli-based draft from `data/english/pi.json`. Decide the final name, where the Blend data lives (e.g. `data/english/blend.json`), and how a Blend line credits the tradition it came from. When the Blend replaces the placeholder, update `BLEND_REFERENCE` in build.py, the English section of notes.html and WORK_BRIEF.md.

## Home page (introduction to the site)

- [ ] A short written introduction: what the site is, the six traditions, and a couple of sentences on the main differences between them for those on the path and how they shaped the Rosettapada Blend. Write it after the translation is finished, from `data/blend/findings.json`; claim only what the record supports. Owner reviews on the live site.

## Verses found only in other traditions (owner asked 2026-11-09; after the 423 Pāli positions)

- [ ] **Inventory first, for the owner to look at.** For each tradition: total verses, chapters, and how many have no Pāli counterpart; then group the non-Pāli verses by which other traditions share them (one tradition only, two, three or more) and by chapter. Show it on the live site as a table. Rough sizes from the scholarship, to be verified against the full texts: Sanskrit Udānavarga ≈1,000 verses in 33 chapters; Tibetan Toh 326 follows the Udānavarga; Chinese T210 ≈750 verses in 39 chapters (13 chapters beyond the Pāli's 26); Patna ≈414 verses in 22 chapters; Gāndhārī ≈350 surviving verses.
- [ ] Groundwork already here: full-text sources we cite (CBETA T210/T212/T213, Esukhia Derge Kangyur, Ānandajoti's comparative Dhammapada with its concordance tables). Our witness files hold only the lines matched to Pāli positions, so the inventory needs the full texts extracted, with the same source pinning as the existing witnesses.
- [ ] Then decide with the owner: which non-Pāli verses join the Blend, where they sit (end of the matching chapter? new chapters?), and how the reader numbers them without breaking the existing verse URLs.

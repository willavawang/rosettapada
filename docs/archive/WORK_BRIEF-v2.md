# Dhammapada Rosetta — Work handoff

## Current phase: reading design only

Do not start the extensive corpus research, scraping, licensing audit, translation, or large-scale concordance work until explicitly authorized.

## Goal

A website for contemplative reading of verses across six textual traditions, not a book or data table. The primary reader looks like a single very large, borderless sheet of paper. Horizontally aligned poetic lines let readers scan English / Pāli / Patna / Gāndhārī / Sanskrit / Chinese / Tibetan. Reading downward progresses through the verse and then to the next, without a spreadsheet appearance.

## Specific design directives — 23 October 2026

1. **One giant sheet:** Do not visually show table cells, boxes, ruled rows, card edges, or repeated individual mini-tables. Underlying grid/row markup is fine to ensure alignment, provided that it is visually invisible. Aim for the sensation of a large paper folio that one moves around.
2. **Legibility over fitting:** It is not necessary to fit all seven columns simultaneously. Default type should be comfortable at 100%; allow zooming out for overview and zooming in for actual reading.
3. **Trackpad navigation:** Two-finger horizontal and vertical scrolling pan around one continuous sheet; support trackpad pinch-to-zoom when available, and offer accessible fallback buttons and Space+drag.
4. **Verse navigation:** Fixed bottom controls with ‹ and › for previous and next verses. These change the reading position, rather than separate language columns.
5. **Table of contents:** A separate index page linking directly to individual verses. Ultimately add chapters and corpus navigation; at prototype stage only first two verses are real links.
6. **Keep research paused:** The first two verses are a sample only. The Tibetan text should explicitly say 'not yet verified' rather than falsely implying it does not exist.

## What is built

- `index.html`: single-sheet static reader for Dhammapada 1–2
- `contents.html`: separate table of contents page
- `notes.html`: design and textual notes
- `styles.css`, `reader.js`: no-dependency implementation
- `data/sample.json`: initial sample data, not a verified corpus
- `build.py`: regenerates the three static pages from the sample

## Deferred scope and methodological principles

- Complete multilingual catalogue and concordance, all six witnesses + English availability flags
- Tallies: total verse occurrences per collection, distinct sayings, overlaps by any 1–6 witnesses, pairwise overlap matrix, full versus partial parallels, manuscript gaps / genuinely absent / not digitized / not verified
- Textual and editorial verification, provenance, licenses, translation choice
- Work toward these only after a separate go-ahead.

## Questions for later, not blockers now

- English as one Pāli pivot versus separate renderings for each tradition
- Whether the eventual catalogue's primary ordering is Pāli or pan-corpus / polycentric
- GitHub publication visibility and whether to enable Pages

## Version boundary

Design iteration 02 is a usability experiment. Do not assume the zoom behavior, line alignment, or navigation has been approved until the user reviews it. Preserve the existing Atlas repository untouched. A *separate* repository is intended if publication is authorized.

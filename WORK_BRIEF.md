# Rosettapada — Work brief

## Current phase: multilingual reading experience, study 07

Renamed from Dhammapada Rosetta on 23 October 2026. The user explicitly requested the first three chapters across all six historical traditions, with English alongside them. This authorizes the bounded comparison of Pāli verses 1–43 with Patna, Gāndhārī, Sanskrit, Chinese, and Tibetan counterparts. Expansion beyond these 43 Pāli verse positions remains paused.

`index.html` opens Pairs (1–20); `pairs.html` remains a compatible alias. `heedfulness.html` (21–32) and `mind.html` (33–43) complete the selection. Each page has English and all six historical traditions. English is Bhikkhu Sujato's Pāli-based translation, beside the Mahāsaṅgīti Pāli from the unchanged, pinned CC0 SuttaCentral/Bilara snapshot. `data/chapters.json` records that source revision. The other traditions and their exact references are in `data/witnesses/`; its provenance ledger freezes the bounded datasets and source extracts. These are historical counterparts, not new translations of Pāli. Preserve each recension's differences, fragments, uncertain readings, and gaps. The original two-verse sample remains unchanged at `sample.html`.

## Publishing preference

The user will review Rosettapada exclusively on GitHub Pages at https://willavawang.github.io/rosettapada/. It is the only publishing target. Commit authorized changes to the GitHub repository and verify that its live homepage and changed pages actually serve the update before reporting completion. Do not deploy to or return the internal ChatGPT-hosted Site unless the user explicitly requests it. `AGENTS.md` records this preference for future development.

## Reading requirements

1. One continuous, borderless sheet. English, Pāli, Patna, Gāndhārī, Sanskrit, Chinese, and Tibetan remain horizontally aligned. No visible table grid, cards, or fixed English pane.
2. Legibility takes priority over fitting. Default English is 22px; historical romanized text is 21px. Horizontal overflow is intentional. Fit is an overview, not a reading-size default.
3. Use native two-axis trackpad scrolling. Support pointer-centered pinch/gesture magnification and accessible zoom buttons. Preserve ordinary text selection; Space+drag is the optional pointer pan.
4. Previous/next verse arrows sit in the fixed bottom bar. They retain horizontal reading position and use addressable verse anchors. Remove visible verse labels and editorial titles; leave a compact stanza gap.
5. Contents links directly to the three chapter pages with an up-right arrow; do not list verses. Verse arrows continue across chapter boundaries, retaining zoom and horizontal reading position. Do not imply the rest of the catalogue is available.
6. Keep the reading view quiet. Remove contextual taglines and introductory eyebrows. The wordmark is Rosettapada with no period. Put source explanations and uncertainty in Notes. A dash means no counterpart located in the consulted sources; it is not proof of absence. Only the preserved earlier sample keeps its unverified Tibetan placeholder.
7. The bottom bar uses icons: a globe opens a window-style language panel, and a diagonal expand symbol fits visible columns. Keep useful magnification feedback. Hide scrollbars everywhere without disabling native scrolling.
8. Language checkboxes show/hide columns without empty gaps. The entire language row except its checkbox supports dragging to reorder both headings and poems; quiet handles also support keyboard reordering. Persist choices across all three chapter pages. Modern Mandarin pinyin covers every displayed Chinese counterpart and is hidden by default; it is an editorial reading aid, not another historical tradition.

## Review before broader milestones

Evaluate line spacing, column widths, panning at 100%, Fit versus reading size, verse changes from the right side of the sheet, and the contents round trip. Physically test Safari trackpad gestures on the user's Mac before treating that path as approved.

The comparative sample's English remains a provisional Pāli-based rendering. The chapter pages attribute their English to Bhikkhu Sujato. Align verse beginnings across the sheet; retain each tradition's own reading line divisions and length. Alignment is a reading aid, not a word-by-word concordance. Preserve the inherited sample and references. Keep edition-specific line breaks, omitted commentary-derived story headings, title choices, and textual uncertainties documented in Notes.

Keep this project separate from the Buddhist Scripture Atlas. Its source repository is `https://github.com/willavawang/rosettapada`. The original brief is retained in `docs/archive/WORK_BRIEF-v2.md`.


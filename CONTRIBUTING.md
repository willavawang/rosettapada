# Working on Rosettapada

The current task is the six-tradition pilot for Pāli chapters 1, 2, 8, 12, 17, and 21, while preserving the earlier Mind page (chapter 3). These seven available pages cover 99 verse positions; the six pilot chapters cover 88. Further reader expansion remains deferred. A full 26-chapter Tibetan contents audit is separately authorized for research.

- Preserve `data/sample.json` and the three inherited source URLs. Do not silently normalize spellings, punctuation, source numbers, or translations.
- A missing or unverified reading is not evidence of absence from a tradition.
- Keep historical counterparts distinct from new translations. Preserve recensional differences, uncertainty markings, and exact references. Freeze deliberate source updates in `data/witnesses/provenance.json`; never fill a historical gap by translating Pāli.
- Keep one horizontal sheet and meaningful text selection. Avoid visible cells, repeated status labels, overlays over the poems, or controls that replace verse navigation with language navigation.
- Keep fonts and scripts local. No corpus fetches, analytics, account system, or backend is needed in this phase.
- Change templates rather than only generated HTML. Run the build, integrity check, and JavaScript syntax check. Check the changed interaction in a browser.
- Prefer small, reviewable interface changes. Record hardware-specific limitations honestly.

Keep the Atlas repository untouched. GitHub Pages at https://willavawang.github.io/rosettapada/ is the user's only review and publishing target. Publish authorized changes there and verify the live homepage and changed pages. Do not deploy to or return the internal ChatGPT-hosted Site unless explicitly requested. See `AGENTS.md` for the persistent project instructions.


# Working on Rosettapada

The current task is interface evaluation. Keep changes within the reading experience unless the user explicitly expands the phase.

- Preserve `data/sample.json` and the three inherited source URLs. Do not silently normalize spellings, punctuation, source numbers, or translations.
- A missing or unverified reading is not evidence of absence from a tradition.
- Keep one horizontal sheet and meaningful text selection. Avoid visible cells, repeated status labels, overlays over the poems, or controls that replace verse navigation with language navigation.
- Keep fonts and scripts local. No corpus fetches, analytics, account system, or backend is needed in this phase.
- Change templates rather than only generated HTML. Run the build, integrity check, and JavaScript syntax check. Check the changed interaction in a browser.
- Prefer small, reviewable interface changes. Record hardware-specific limitations honestly.

Keep the Atlas repository untouched. GitHub Pages at https://willavawang.github.io/rosettapada/ is the user's only review and publishing target. Publish authorized changes there and verify the live homepage and changed pages. Do not deploy to or return the internal ChatGPT-hosted Site unless explicitly requested. See `AGENTS.md` for the persistent project instructions.


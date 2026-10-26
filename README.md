# Rosettapada

A quiet Dhammapada reading surface. **Reading study 08** presents a six-chapter pilot: **Pairs**, **Heedfulness**, **Thousands**, **Self**, **Anger**, and **Miscellaneous**, across **Pāli, Patna, Gāndhārī, Sanskrit, Chinese, and Tibetan**, with Bhikkhu Sujato’s Pāli-based English alongside them. The six selected chapters contain 88 Pāli verse positions. The earlier **Mind** page remains available separately, bringing the total to 99. Historical counterparts follow Pāli order without harmonizing their wording; fragments, partial matches, and unlocated counterparts remain explicit in Notes. Optional modern Mandarin pinyin starts hidden. The earlier two-verse sample is preserved at `sample.html`. Further reader expansion remains paused while a separate Tibetan contents audit covers all 26 Pāli chapters.

## Read

Open `index.html` for Pairs, `contents.html` for the six-chapter selection and earlier Mind page, or `sample.html` for the earlier comparative sample. The previous `pairs.html` URL continues to work. Files work directly in a modern browser, or serve the project over HTTP:

```sh
python3 build.py
python3 -m http.server 8000
```

Open `http://localhost:8000/`. No installation, API key, account, external font request, or runtime dependency is required for the static reader. Tibetan uses a local Noto Serif Tibetan font.

- Two-finger scroll pans horizontally and vertically. Pinch zooms the sheet where supported.
- `+` / `−` magnifies; `0` or the percentage button returns to 100%. **Fit** shows the visible columns.
- Hold Space and drag to pan with a pointer. Without Space, text remains selectable.
- Arrows in the bottom bar or `[` / `]` move between verses while retaining horizontal position. On the full chapter pages, they continue across chapter boundaries with the same zoom.
- The globe button opens the Languages window. Show or hide columns with checkboxes; drag anywhere else on a language row to reorder it. With a handle focused, the up and down arrow keys also reorder columns. Choices persist in the browser.
- Chinese pinyin starts hidden and can be shown independently of Chinese characters. Fit follows the currently visible columns; its button uses a diagonal expand icon.
- Contents links to the six pilot chapter pages, with Mind listed separately, rather than listing verses. Direct verse anchors work. Zoom and position are remembered per page; language settings are shared across all multilingual chapter pages and kept separate from the comparative sample. The new language preference key opens all six traditions for readers coming from the old two-column pages.
- Scrollbars are hidden throughout the site; native scrolling and panning remain available.
- Browser zoom shortcuts remain available. The question-mark button explains the controls.

## Develop

Python 3.10+ and Node 18+ are sufficient for the build and checks. Node is only used to check JavaScript syntax.

```sh
python3 build.py
python3 tools/check.py
node --check reader.js
```

Edit `templates/*.html`, `styles.css`, and `reader.js`, then rebuild. Generated root HTML is tracked so the site also works by opening a file. `dist/` is reproducible deployment output and is ignored by Git.

| Location | Purpose |
| --- | --- |
| `data/sample.json` | Unchanged text from the v2 prototype; not a verified corpus |
| `data/pinyin.json` | Optional modern Mandarin reading aid for the two Chinese sample verses |
| `data/chapters.json` | Chapter order, ranges, source revision, and checksums |
| `data/pali/` | Frozen Pāli, English, source markup, license, and publication metadata for the selected 99 verse positions |
| `data/witnesses/` | Five additional historical traditions, per-verse source references, optional Chinese pinyin, bounded source extracts, coverage, and checksums |
| `assets/fonts/` | Local Tibetan reading font and SIL Open Font License |
| `templates/` | Reader, contents, and textual-notes templates |
| `styles.css` | Typography, invisible line alignment, and responsive controls |
| `reader.js` | Native panning, zoom, navigation, keyboard and session position |
| `build.py` | Offline standard-library page generator |
| `tools/check.py` | All 99 available verse positions, historical readings, native Chinese/Tibetan source fidelity, frozen hashes, links, deployment output, and sample integrity |
| `tools/import_pali.py` | Fetch new chapters at the existing pinned Bilara revision; verify existing frozen sources |
| `tools/import_indic.py` | Recreate the bounded Patna, Gāndhārī, and Sanskrit datasets from downloaded comparative-edition pages |
| `docs/DESIGN.md` | Interface decisions and review questions |
| `docs/TEXTUAL_NOTES.md` | Inherited references and unresolved readings |
| `docs/READING_QA.md` | Verification record and remaining hardware checks |
| `docs/archive/` | Original Work brief and source notes, retained for provenance |

## GitHub

Source repository: [willavawang/rosettapada](https://github.com/willavawang/rosettapada). The user's only review and publishing site is [willavawang.github.io/rosettapada](https://willavawang.github.io/rosettapada/). Do not deploy to or return the internal ChatGPT-hosted Site unless explicitly requested. Verify the GitHub Pages homepage and changed pages before reporting completion. This project is separate from the Buddhist Scripture Atlas. CI checks the static build on pushes and pull requests. Generated root HTML supports Pages publishing from `main` / `(root)`. The optional **Publish GitHub Pages** workflow remains manual for deployments configured to use GitHub Actions.

The repository was created public; its visibility has been preserved. SuttaCentral texts are CC0. Chinese text is credited to CBETA under CC BY-NC-SA 4.0, with its notice and edition headers retained. Tibetan follows Esukhia's public-domain Digital Derge Kangyur. Indic ancient verse texts follow Ānandajoti Bhikkhu's comparative edition; modern edition and compilation rights are documented separately, without asserting a blanket license. Source details and uncertainty are in `docs/TEXTUAL_NOTES.md` and the reading site's Notes. The tracked `.openai/hosting.json` is legacy configuration only.

See [WORK_BRIEF.md](WORK_BRIEF.md) for the phase boundary. Review the reading experience before expanding the corpus.


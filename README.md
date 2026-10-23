# Rosettapada

A quiet Dhammapada reading surface: English and six historical textual traditions on one continuous, unruled sheet. This is **reading study 05**, containing only the inherited two-verse sample and an optional Mandarin pinyin reading aid. Corpus research and the six-tradition concordance have not started.

## Read

Open `index.html` directly in a modern browser, or serve the project over HTTP:

```sh
python3 build.py
python3 -m http.server 8000
```

Open `http://localhost:8000/`. No installation, API key, account, external font, or runtime dependency is required for the static reader.

- Two-finger scroll pans horizontally and vertically. Pinch zooms the sheet where supported.
- `+` / `−` magnifies; `0` or the percentage button returns to 100%. **Fit** shows all seven columns.
- Hold Space and drag to pan with a pointer. Without Space, text remains selectable.
- Arrows in the bottom bar or `[` / `]` move between verses while retaining horizontal position.
- The globe button opens the Languages window. Show or hide columns with checkboxes; drag anywhere else on a language row to reorder it. With a handle focused, the up and down arrow keys also reorder columns. Choices persist in the browser.
- Chinese pinyin starts hidden and can be shown independently of Chinese characters. Fit follows the currently visible columns; its button uses a diagonal expand icon.
- Contents links to chapter pages, rather than listing verses. Direct verse anchors still work. The current zoom and reading position survive visits to Notes within the browser tab.
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
| `templates/` | Reader, contents, and textual-notes templates |
| `styles.css` | Typography, invisible line alignment, and responsive controls |
| `reader.js` | Native panning, zoom, navigation, keyboard and session position |
| `build.py` | Offline standard-library page generator |
| `tools/check.py` | Local links, fragments, generated assets, and sample integrity |
| `docs/DESIGN.md` | Interface decisions and review questions |
| `docs/TEXTUAL_NOTES.md` | Inherited references and unresolved readings |
| `docs/READING_QA.md` | Verification record and remaining hardware checks |
| `docs/archive/` | Original Work brief and source notes, retained for provenance |

## GitHub

Source repository: [willavawang/rosettapada](https://github.com/willavawang/rosettapada). Reading site: [willavawang.github.io/rosettapada](https://willavawang.github.io/rosettapada/). This project is separate from the Buddhist Scripture Atlas. CI checks the static build on pushes and pull requests. Generated root HTML supports Pages publishing from `main` / `(root)`. The optional **Publish GitHub Pages** workflow remains manual for deployments configured to use GitHub Actions.

The repository was created public; its visibility has been preserved. The working reading-study Site is private. No blanket license has been applied to the inherited text samples; source permissions and editorial verification remain deferred. The tracked `.openai/hosting.json` binds the private working Site and should be preserved when continuing that Site.

See [WORK_BRIEF.md](WORK_BRIEF.md) for the phase boundary. Review the reading experience before expanding the corpus.


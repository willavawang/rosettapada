# Rosettapada

A quiet Dhammapada reading surface: English and six historical textual traditions on one continuous, unruled sheet. This is **reading study 03**, containing only the inherited two-verse sample. Corpus research and the six-tradition concordance have not started.

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
- Bottom arrows or `[` / `]` move between verses while retaining horizontal position.
- Contents links open individual verses. The current zoom and reading position survive visits to Contents and Notes within the browser tab.
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

Source repository: [willavawang/rosettapada](https://github.com/willavawang/rosettapada). This project is separate from the Buddhist Scripture Atlas. CI checks the static build on pushes and pull requests. The optional **Publish GitHub Pages** workflow is manual; it does not publish on push. It requires Pages to be configured for GitHub Actions and a suitable repository/account plan.

The repository was created public; its visibility has been preserved. The working reading-study Site is private. No blanket license has been applied to the inherited text samples; source permissions and editorial verification remain deferred. The tracked `.openai/hosting.json` binds the private working Site and should be preserved when continuing that Site.

See [WORK_BRIEF.md](WORK_BRIEF.md) for the phase boundary. Review the reading experience before expanding the corpus.


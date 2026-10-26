# Reading study 08 — six-chapter pilot verification

26 October 2026. Source and managed Chromium preview checks for six pilot chapters plus the retained Mind page.

- Contents lists Pairs, Heedfulness, Thousands, Self, Anger, and Miscellaneous. Mind remains under Also available. All seven chapter pages contain English, six historical traditions, and hidden-by-default pinyin. The six pilot pages contain 88 Pāli positions; all available pages contain 99.
- Native source checks cover all 248 selected Indic readings, 105 Chinese reading occurrences, and 96 Tibetan selections (408 pādas). Chinese whole text and punctuation match the pinned full CBETA edition; Tibetan lines occur verbatim and in order within their exact pinned Derge spans. The first43 historical verse records and42 Tibetan excerpts are unchanged. Patna158 uses a separately verified primary-text correction, and documented edition differences remain visible in Notes.
- The independent Tibetan research ledger covers all423 Pāli positions. It distinguishes305 secure published attestations,18 direct additions, one tentative citation,99 reviewed reader positions, and96 located native texts. Its323/423 total is a lower bound, not semantic identity or a complete absence census.
- Browser navigation checks verify32→100,115→157 and the reverse,166→221,234→290, and the disabled Next endpoint at305 after the font-dependent position restoration. The115↔157 transition retains164% magnification and a2429px horizontal offset.
- At desktop Fit (45%), all seven default columns share one continuous borderless sheet. First-verse tops coincide. The local Rosettapada Tibetan font loads and renders. Source glyph normalization also covers references and accessible labels, with no private-use glyphs in generated chapter pages.
- Showing pinyin, hiding Chinese, and keyboard-reordering Tibetan persist across a new chapter transition. Restore defaults restores the seven default columns and hides pinyin.
- Embedded320px and375px viewports have no document overflow. The320px footer controls stay within x=6–314; its Languages window stays within x=12–308 and has a440px height. The reading sheet retains intentional horizontal overflow.
- The Python build,99-position integrity checks, source hashes, local links and navigation targets, preserved sample, deployable assets, and JavaScript syntax pass. Temporary responsive fixtures were removed from deployment output.

Physical Safari trackpad gestures and physical mobile touch input remain unverified. These checks establish source fidelity and the selected reading behavior, not an exhaustive critical edition or a uniform semantic-equivalence judgment.

---

# Reading study 07 — multilingual verification

24 October 2026. Chromium preview at desktop size, plus embedded 320px and 375px reading viewports.

- All three chapter pages contain English, Pāli, Patna, Gāndhārī, Sanskrit, Chinese, Tibetan, and hidden-by-default Chinese pinyin. The homepage contains Pairs 1–20, followed by Heedfulness 21–32 and The Mind 33–43 through Contents.
- At desktop Fit (45%), all seven default columns appear on one borderless sheet. Verse beginnings align; each tradition retains its own number of lines. Tibetan renders in the bundled reading font, and missing counterparts appear as quiet dashes.
- Language controls show pinyin and hide Chinese independently. Keyboard reordering moves Tibetan and updates every verse. These choices survive reload and chapter changes. Restore defaults restores all six traditions and English, hiding pinyin.
- Pairs 20 → Heedfulness 21 and the reverse retain 139% magnification and a 1412px horizontal offset. Heedfulness 32 → The Mind 33 also retains those values. Restoration waits for the local font to load. Next is disabled at 43; Previous remains available.
- Contents lists exactly the three chapter pages, without verses. Its Pairs link opens the beginning. No visible verse labels, editorial titles, grid lines, or scrollbars have been introduced.
- At 320px, document width is exactly 320px, with all seven footer controls inside the viewport. The eight-option language window is 440px high and spans x=12 to x=308. The 375px reader also displays normally; only the reading sheet overflows horizontally.
- The Indic datasets regenerate byte-identically from the retained working source HTML. All 42 Tibetan source selections match exact line spans in the complete pinned volume. All 43 selected Chinese passages (42 verse positions plus the additional counterpart for 29) also match the complete pinned upstream CBETA text and punctuation. Offline checks compare every historical reading to the dataset, Chinese to retained CBETA selections, and Tibetan to its verbatim native excerpts, as well as checking source hashes, original sample integrity, links, and assets.
- Python build, integrity checks, and JavaScript syntax pass. No live corpus requests are required by the reader.

Physical Safari trackpad gestures and physical mobile touch input remain unverified. This establishes the source fidelity and reading behavior of the bounded selection, not an exhaustive critical concordance. GitHub Pages publication was verified for source commit `4e781b8a8521db9ec70c74f6f88fbd1b5bb011d2`: all three public chapter pages render the seven default columns, and the deployed HTML, CSS, JavaScript, and Tibetan font are byte-identical to the tested build. Both GitHub CI and Pages deployment succeeded.

---

# Reading study 06 — verification

Homepage follow-up, 23 October 2026: the canonical homepage now contains Pairs verses 1–20. The old `pairs.html` link remains a compatible alias. The earlier eight-option, two-verse comparison is preserved at `sample.html` and linked from Notes. Preview checks verified the homepage verse count, the three Contents links, and the preserved sample. Automated integrity checks require the complete first chapter at the homepage. The user now reviews this project exclusively on GitHub Pages; internal hosting is no longer a publishing target.

23 October 2026. Chromium preview at desktop size and embedded 375px / 320px viewports.

- Verified: Contents lists exactly Pairs, Heedfulness, and The Mind, with chapter links and no verse list. Each opens its beginning.
- Verified: the three pages contain 20, 12, and 11 verses respectively, with English and Pāli columns and visible translator/edition attribution.
- Verified: verse 20 → 21 and 21 → 20 cross chapter pages, retaining 164% magnification and a 243px horizontal offset. Verse 32 → 33 opens The Mind. Next is disabled at verse 43.
- Verified: hiding Pāli removes all twelve Pāli poems in Heedfulness; the final English column is protected. Restore defaults restores both columns.
- Verified: the new chapter pages display at 100% in 375px and 320px windows. The 320px document has no overflow; only the reading sheet pans horizontally. All footer buttons fit and scrollbar styles remain hidden.
- Offline checks compare all 43 verses, every source segment, and line divisions with the pinned source snapshot. All nine source files match both SHA-256 and upstream Git blob hashes. The inherited sample checksum and all three original reference links are retained.
- JavaScript syntax and generated deployment/link checks pass.

Physical Safari trackpad gestures and physical mobile touch input remain unverified. No historical concordance has been added beyond the original two-verse sample.

## Previous study 05 record

23 October 2026. Chromium preview, desktop and embedded 375px / 320px viewports.

- Verified: previous/next arrows are in the bottom bar; none remain between poems. The stanza gap is 40px.
- Verified: dragging English by its name moved it from first to third place, updating headings and both verse grids without changing its checkbox. Dragging the blank middle of its row restored it to first place.
- Verified: clicking the Chinese checkbox hid the heading and both Chinese poems without changing the column order.
- Verified: next/previous preserve a 1363px horizontal reading offset; endpoint buttons disable correctly.
- Verified: the new diagonal fit icon fits all default columns into the 1363px reading viewport at 47%.
- Verified: all bottom controls fit within 320px with no document overflow. The language window also fits, from x=12px to x=308px. Scrollbars remain hidden.
- Offline checks preserve the original sample checksum, sources, local links, and generated deployment pages. JavaScript syntax passes.

Physical Safari trackpad gestures and physical mobile touch input remain unverified.

## Previous study 04 record

23 October 2026. Chromium preview, desktop and embedded 375px / 320px viewports.

- Verified: no visible verse labels or wordmark period; compact 48px interval between verse grids; arrows appear after verses and are absent from the bottom bar.
- Verified: globe opens the Languages window; Chinese can be hidden; pinyin can be shown independently and starts hidden on a clean preference set.
- Verified: pointer drag changed English from second to third position, updating headings and both poems; keyboard up/down moved pinyin to first position. Language choices survived a reload.
- Verified: one-column mode works and protects the final visible column; Restore defaults restores the original order and pinyin-off state.
- Verified: Fit recomputes for selected columns; the fitted sheet measured 1362.86px in a 1363px viewport after hiding Chinese.
- Verified: Contents contains a chapter link, no verse list, and opens the start of the chapter even after reading verse 2.
- Verified: scrollbar styles are `none` on the reader, document, and window. Native panning and verse navigation still work.
- Verified: the bottom bar and language window fit at 375px and 320px. A small 320px masthead overflow was corrected by reducing the wordmark size and header gap.
- Offline checks preserve the original sample checksum, local links, source references, and pinyin/sample line counts.

Physical Safari trackpad gestures and physical mobile touch input remain unverified.

## Previous study 03 record

23 October 2026. Checked in the managed Chromium preview at 1363 × 936 pixels.

## Verified in a browser

- English uses six unbroken sample lines at desktop 100%; line 2 initially wrapped, and the English column was widened to 540px.
- The six populated traditions share the same row positions. A wrapped line makes the same space in every tradition rather than misaligning subsequent lines.
- Native horizontal scrolling reached the right-hand traditions. The verse marker remained visible at the left edge of the viewport.
- Next and previous brought the correct verse beneath the sticky headings. A horizontal scroll offset of 1363px was retained on the verse change.
- Four zoom-in button presses reached 194%. Navigation continued to target the correct verse and retained horizontal position.
- Fit reached 47% and displayed all seven columns within a 1353px reading viewport. Reset returned to 100%.
- Contents linked directly to verse 2; the correct hash and bottom label were restored with the saved zoom.
- Reading help opened as a modal with a focused close button; its close control returned to the reader.
- Accessibility structure presents complete language poems, meaningful headings, named controls, and disabled previous/next endpoints.

## Verified offline

- Sample JSON is byte-identical to the inherited v2 data, recorded by SHA-256 in `data/provenance.json`.
- All three inherited external source references remain on Notes.
- Local page links and verse fragments resolve; generated source and deployment pages match.
- Python build and JavaScript syntax checks pass.

## Not yet verified

- Physical Mac/Safari trackpad pinch and Space+drag. Separate Safari gesture and Chromium ctrl+wheel paths are implemented, but no physical gesture was available in this check.
- Touch pinch and narrow-window rendering on iPhone/iPad. Zoom controls stay available in the responsive CSS. The preview browser stopped responding when opening the narrow-window QA fixture; that fixture was removed before publication.
- User acceptance of poetic spacing and column widths. This is a design review, not a completed usability study.


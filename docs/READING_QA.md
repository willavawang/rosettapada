# Reading study 05 — verification

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


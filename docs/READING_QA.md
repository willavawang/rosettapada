# Reading study 03 — verification

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


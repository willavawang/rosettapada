# Reading study 05

The primary action is reading a poem. Comparison should be available with a movement of the hand, without turning each line into a database row.

## One paper surface

The same warm paper color extends through the page, with no outline around the sheet, poem panels, row stripes, or column dividers. Whitespace separates verses. A modest green-grey accent distinguishes English without giving it a fixed pane. Native text remains selectable.

## Type and alignment

English is 22px and romanized witnesses are 21px at 100%; Chinese is 23px. The English column is wide enough for the inherited six lines on a desktop. On narrow windows it wraps; CSS subgrid shares row heights across the whole verse so other traditions continue to align. Screen readers encounter each tradition as a complete poem rather than hopping between languages on every line.

The overall sheet intentionally exceeds the viewport. Fit reveals all seven columns; 100% returns to a comfortable reading scale. This explicitly trades simultaneous visibility for readable text. Labels scale with the sheet and are intentionally small in the overview.

## Orientation and movement

Language headings stay visible during vertical reading and move horizontally with their text. Visible verse titles and numbers are removed, leaving a 40px stanza gap. Previous/next verse arrows stay in the bottom bar beside a globe and scale controls. The fit icon uses two diagonal arrows, with rounded strokes in the spirit of Apple's system iconography. Contextual taglines and introductory eyebrows are removed from the pages.

Ordinary wheel and touch scrolling stay native. Trackpad pinch uses ctrl+wheel in Chromium and Safari gesture events where available. Browser Cmd/Ctrl zoom keyboard shortcuts remain untouched. Space+drag is optional, never required for basic navigation.

Zoom preserves the sheet point under the pointer; button zoom uses the viewport center. At a sheet boundary, native scroll clamping may prevent exact preservation. Extra trailing paper lets the final verse rise to the same reading position as the first. Verse jumps preserve horizontal offset at the current scale. Contents links to chapter pages and opens their beginning; direct verse anchors and per-tab position memory remain available. Scrollbars are hidden throughout the site, while native scrolling remains enabled.

## Language window

The globe opens a small nonmodal window with a title bar, close button, and language checkboxes. Changes immediately remove or restore the corresponding columns without leaving empty tracks. The whole row can be dragged, including its name and empty space; only the checkbox is reserved for visibility changes. Subdued handles appear on hover or focus and provide keyboard up/down reordering. Reordering updates the entire sheet, including its accessible reading order. Choices persist locally; Restore defaults restores the original order and hides pinyin. At least one column remains visible. Fit recomputes when the selected languages change.

Pinyin is a separate optional modern Mandarin reading aid for the existing Chinese sample, initially hidden. It does not expand the historical corpus. Existing sample bytes and source references remain unchanged.

## Textual restraint

The sample text and source references are unchanged. One status message per Tibetan poem replaces six repeated placeholders. Notes explains that the English follows Pāli and that line alignment and source numbers await verification. These limits remain visible without repeating a research disclaimer between poetic lines.

## The review that matters

Read one verse slowly at 100%, then move across and back. Does the comparison deepen attention, or interrupt it? Adjust spacing and controls based on that experience before adding texts. Test the physical Mac trackpad, especially Safari pinch, before accepting the interaction design.


# Chinese witnesses

The reader indexes historical Chinese counterparts to all 423 Pāli positions. The Chinese column draws on the 法句經 (T210), 出曜經 (T212), and 法集要頌經 (T213). Ken Su's 26 correspondence tables identify candidate passages. The verse wording and punctuation come from the pinned CBETA edition, with source collection and Taishō line span recorded for each reading.

## Coverage

A selected Chinese passage is displayed at 413 positions. The status ledger classifies 374 as present and 39 as partial. No candidate is listed at Pāli 42, 130, 195, 196, 216, 235, 236, 282, 295, or 343. These are gaps in the consulted correspondence tables. Status tracks the selected historical relationship and documented qualifications. It is not a complete semantic grading of the Chinese against the Pāli.

The displayed passages come from T210 at 384 positions, T212 at 21, and T213 at eight. Retained alternatives bring the record count to 452 occurrences across 438 distinct references. Every occurrence has been checked for wording, punctuation, and locator in the pinned native edition. All 99 previously published position records retain their original values.

## Editorial selection

T210 is the default where a correspondence is identified. Exceptions prioritize a consequential feature of the Pāli passage. T212 31.3 preserves the harmful action at Pāli 131. T212 13.5 and T213 12.9 preserve the explicit formulas for impermanence and not-self at 277 and 279. At Pāli 278, T210 28.20 takes precedence over T210 28.4 for its express reference to the suffering of conditioned things. At 410, 411, and 415, the selected T212 readings preserve closer formulations of the key themes. The record notes explain each choice and retain references to other listed parallels.

The same Chinese source stanza can correspond to several Pāli positions. T210 6.11 gathers Buddha, Dharma, and Saṅgha recollection across 296–298. T210 34.1 gathers sense restraint with restraint of body and mind across 360–361. Shared stanzas are indexed as distinct reading occurrences at each position, with a separate shared-reference ledger in `chinese.json`. The original Chinese word order and lines stay visible.

## Source and regeneration

The XML snapshots keep the complete unchanged TEI headers, original chapter headings, ancient verse wording and punctuation, and Taishō line markers for the selected passages. The full source XML hashes are recorded in `cbeta-provenance.json`. `verification.json` records the source check for each reading. `correspondence-mapping.json` retains the source identifiers and Chinese quotations from the table columns. The tables' modern Pāli translations are outside the dataset.

`extract.py` resolves the historical characters through CBETA's character declarations and extracts the text from the matching chapter section. T213's printed chapter 30 is embedded in the preceding TEI division, and subsequent printed chapter headings are offset from the TEI index. Fuzzy matching works at native clause boundaries so that edition variants cannot shorten a displayed clause to the table quotation's length. Edition differences in a selected quotation are recorded alongside the native reading.

The static site can build with its retained data. To verify the selected snapshots independently of the full working copies, run `python3 data/witnesses/sources/chinese/build_chinese.py` with lxml and pypinyin 0.55.0 available. For a full re-extraction, add `--source-directory DIRECTORY` containing the pinned complete CBETA XMLs. Add `--correspondence-directory DIRECTORY` to reparse the expansion chapters' Ken Su tables. The complete working copies stay outside the repository. No network request is made by these scripts.

Pinyin is a modern Mandarin reading aid with spaced citation tones. Contextual corrections cover common polyphonic words and rare historical forms. The rare forms 𦾨, 𣧑, and 𭶑 use the readings of 孽, 凶, and 黠 from the corresponding table quotation or CBETA normalization. The expansion pinyin has received limited contextual review.

See `CBETA-NOTICE.txt` and the source metadata for attribution and CC BY-NC-SA 4.0 terms.

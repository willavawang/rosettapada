# Textual status — reading study 08

The six-chapter pilot follows Pairs (1–20), Heedfulness (21–32), Thousands (100–115), Self (157–166), Anger (221–234), and Miscellaneous (290–305), totaling 88 Pāli positions. The earlier Mind page (33–43) remains available separately, bringing the total to 99. All seven pages present English plus Pāli, Patna, Gāndhārī, Sanskrit, Chinese, and Tibetan. These are historical textual counterparts placed in Pāli order, not six new translations of the Pāli. Each verse begins at the same horizontal level; its internal line divisions and length follow its own source.

## Coverage

“Present” means a selected historical counterpart, not identical wording. “Partial” includes fragmentary surviving text and incomplete correspondence. A dash marks “not located in the consulted sources,” never proof of absence throughout a tradition. These counts describe the bounded selection, not all surviving witnesses.

| Tradition | Present | Partial | Not located (Pāli verse numbers) |
| --- | --- | --- | --- |
| Pāli | 99 | 0 | None |
| Patna | 79 | 4 | 17, 18, 27, 30, 42, 43, 101, 109, 222, 223, 295, 296, 297, 298, 302, 304 |
| Gāndhārī | 54 | 17 | 3, 4, 5, 6, 17, 18, 23, 35, 36, 42, 43, 104, 105, 110, 111, 114, 157, 159, 160, 161, 165, 225, 226, 231, 232, 233, 295, 304 |
| Sanskrit Udānavarga | 77 | 15 | 6, 17, 18, 36, 101, 106, 109 |
| Chinese | 71 | 26 | 42, 295 |
| Tibetan Udānavarga | 92 | 4 | 36, 101, 109 |

The site’s Notes includes every selected reference and the differences or uncertainties on individual records. Multiple recorded counterparts may be retained in the data even where the sheet displays one preferred reading.

## English and Pāli

English is Bhikkhu Sujato’s *Sayings of the Dhamma*, alongside SuttaCentral’s Mahāsaṅgīti Pāli. The same pinned revision, upstream paths, Git blob IDs, and SHA-256 checksums remain frozen in `data/chapters.json`; source JSON and the CC0 publication record remain in `data/pali/`.

Words, punctuation, and verse-line divisions follow that edition. Surrounding whitespace and three nonprinting `<j>` markers in English verse 17 are omitted. Only markup identified as verse lines is displayed; commentary-derived story headings and chapter colophons are excluded. The second source heading is “Diligence”; the site uses “Heedfulness.” English translates Pāli and must not be read as a translation of every neighboring witness. Its word order can also differ from Pāli, notably in verses 42–43.

## Patna, Gāndhārī, and Sanskrit

The selected ancient verse texts and correspondence references follow Ānandajoti Bhikkhu’s *A Comparative Edition of the Dhammapada*, fourth revised edition (April 2020), chapters 1, 2, 3, 8, 12, 17, and 21. The edition in turn identifies Cone’s Patna, Brough’s Gāndhārī, and Bernhard’s Sanskrit Udānavarga texts. URLs and original HTML hashes accompany the records. `tools/import_indic.py` recreates the bounded datasets from downloaded source pages; the imports were compared byte for byte with the retained working HTML before publication.

Surviving lacunae and source uncertainty marks are retained. Dotted underlining marks the edition’s uncertain or conjectural readings; grey text marks contextual lines the source does not align to Pāli. Its comparison emphasis is not reinterpreted as conjecture. Five legacy private-use transliteration glyphs are rendered as standard Unicode equivalents, checked against the source font’s actual glyph names; `normalization.json` records them. The source’s critical editions and compilation have separate rights notices; no blanket project license is asserted. Modern commentary and unrelated parallel works are not copied. The Patna counterpart of Pāli 158 is corrected against the independently checked native chapter 17 because the comparative page repeats the preceding stanza under the correct reference. The original duplicate, replacement, primary-source hash, and reason are retained in `sources/indic/corrections.json`. Four other edition differences remain explicitly documented, without harmonization. `sources/indic/selected-source-passages.json` and `verification.json` retain the bounded source proof.

## Chinese and modern Mandarin pinyin

Ken Su’s (蘇錦坤) chapter 1, 2, 3, 8, 12, 17, and 21 correspondence tables identify counterparts; the displayed text follows the pinned CBETA TEI edition. T210 is preferred. Seven positions use documented historical fallbacks: 3 → T212 15.7; 4 → T213 14.10; 30 → T213 4.24; 32 → T213 4.32; 34 → T212 32.2; 299 → T213 15.20; 300 → T212 16.18. The actual collection, Taishō page/column/line, source revision, and edition date accompany each reading. Pāli 29 has two recorded T210 counterparts, with the horse comparison displayed first. Pāli 42 and 295 remain unlocated in these tables. T210 combines Buddha, Dharma, and Saṅgha recollection in one stanza; at 296–298 the repeated whole stanza is explicitly marked as a grouped partial correspondence. It is not treated as three independent Chinese verses.

The source selection retains CBETA wording and punctuation, including difficult historical characters and differences from the correspondence table. Some matches are partial: the Chinese verse corresponding to 25 uses lamp/illumination language where Pāli has an island; 30 lacks the Pāli Indra reference; 39 praises merit restraining evil rather than abandoning merit and demerit; 40 opens with a tortoise and six faculties rather than a body-as-pot. These differences are preserved, not repaired to fit Pāli. Exact references and additional differences are in Notes and `sources/chinese/README.md`.

Pinyin is a modern editorial Mandarin reading aid for every displayed Chinese reading, hidden by default. It uses citation tones, character spacing, and manual contextual corrections; it does not assert historical pronunciation, tone sandhi, or independently reviewed interpretation of difficult phrases. Chinese source extracts retain CBETA’s attribution, complete edition headers, and CC BY-NC-SA 4.0 notice.

## Tibetan

The native text comes from Esukhia’s public-domain Digital Derge Kangyur, Toh 326, volume 72, folios 209a.1–253a.7, pinned at commit `a582cf471b7c85a101035071078032f106a8e536`. Each reading cites its actual folio and complete-source line span. Native spelling is checked against verbatim retained excerpts, not generated from Pāli, Sanskrit, or an English translation.

Sanskrit correspondence starts from the comparative edition; University of Oslo’s Bibliotheca Polyglotta and Rockhill’s public-domain 1883 Tibetan translation/concordance support identification. Sanskrit and Tibetan numbers are not interchangeable. Native Tibetan counterparts of Pāli 17–18 are included even though the selected Sanskrit mapping lacks them. Related passages at Pāli 6 and 106 are explicitly provisional and partial. Published partial counterparts are retained at 115 and 230. Pāli 36, 101, and 109 remain unlocated.

Physical folio markers and newlines are removed for reading. Shad-delimited reading line breaks are editorial. Where the electronic source records an original spelling and a proposed correction, the original is retained and the suggestion is recorded. Tibetan’s own order and recensional differences remain: verse 1 ends with a wheel cutting off a head; verse 20 is shorter than Pāli; verse 27 ends with exhaustion of the taints. The font is local Noto Serif Tibetan under SIL OFL 1.1. See `sources/tibetan/README.md` for provenance and verification limits.

## Tibetan contents audit

The independent Rockhill 1883 Tibetan–Pāli index was visually checked across all six printed concordance pages (217–222). The 423-position ledger records 305 secure published attestations and 18 additional independently checked native counterparts, establishing a **323/423 (76.4%) lower bound**. One printed tentative reference remains excluded. An unlisted position is not proof of textual absence; semantic closeness outside the native selection remains unassessed.

All 99 available reader positions were reviewed. The 96 located Tibetan selections, totaling 408 pādas, match their cited pinned Derge source spans. The six pilot chapters contain 82 present counterparts, four partial or provisional related selections, and two not-located positions. The first 43 verse records and 42 retained native excerpts are unchanged. Present identifies an authentic counterpart, not identical wording. Numerical, imagery, and clause-order differences remain visible.

The detailed methods, 26-chapter counts, new native identifications, and numbering differences are in [TIBETAN_ANALYSIS.md](TIBETAN_ANALYSIS.md). `sources/tibetan/correspondence-audit.json` separates published references, direct native checks, reviewed gaps, qualified related passages, and lower-bound counts. Sanskrit presence flags are not used as Tibetan evidence.

## Preserved earlier sample

`data/sample.json` is byte-identical to the inherited v2 prototype and remains at `sample.html`, including its working English and unverified Tibetan placeholder. Its provisional sense-based line alignment has not become a verified concordance. The three inherited reference links remain in Notes:

- https://ancient-buddhist-texts.net/Buddhist-Texts/C3-Comparative-Dhammapada/CD-01-Yamaka.htm
- https://cbetaonline.dila.edu.tw/T0210
- https://nanda.online-dhamma.net/tipitaka/sutta/khuddaka/dhammapada/dhp-correspondence-tables/dhp-correspondence-tables-pali-chap01/

## Scope and verification limits

The frozen datasets and source excerpts are recorded in `data/witnesses/provenance.json`. Offline checks compare every displayed reading to its dataset, Chinese text to retained CBETA passages, and Tibetan lines to their cited native excerpts. These establish transcription fidelity and explicit coverage, not a new critical edition or exhaustive manuscript collation. Corrections require deliberate source review. Further reader expansion beyond the six pilot chapters and preserved Mind page remains deferred. The full 26-chapter Tibetan research inventory is a lower-bound correspondence audit, not a full semantic collation or a six-way identity count.

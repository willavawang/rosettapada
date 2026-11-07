# Tibetan witnesses and contents audit

The reader and research audit cover all 423 Pāli positions across 26 chapters. The 99 prior records from the pilot and Mind page are preserved. The research ledger includes published correspondence references alongside the native passages chosen for display.

## Primary Tibetan text

Display text is from Esukhia’s Digital Derge Kangyur, Toh 326, *Ched du brjod pa’i tshoms* (Udānavarga), vol. 72, *mdo sde sa*, ff. 209a.1–253a.7.

- Repository: <https://github.com/Esukhia/derge-kangyur>
- Pinned commit: `a582cf471b7c85a101035071078032f106a8e536`
- Path: `text/072_མདོ་སྡེ།_ས.txt`
- Git blob: `d9abab24ddfc32ccd5dc65973cfbbef1dd6bd959`
- Full volume: 2,787,425 bytes; SHA-256 `437362220fde32d7c4e4311b4aa0885a5ab76612fe5efc0d9afd62605b763041`
- Initially accessed 24 October 2026. Tier 2 expansion checked 4 November 2026.

The source README declares the electronic text public domain; `esukhia-README.md` retains its verbatim license and edition statement. The digital edition preserves archaic spellings, carving mistakes, and proposed corrections. It is not an error-free critical edition. The translation colophon is at 253a.7; requested attribution remains in `../../tibetan.json`.

`selected-derge-excerpts.json` retains exact physical source-line spans for every located passage, including folio markers and correction braces. The whole multi-text volume is not distributed here. Display preparation removes physical markers/newlines, joins split words, retains the first/printed form in correction annotations, and breaks reading lines at native shad boundaries. Native words and punctuation remain unchanged. Folios identify the primary source; Sanskrit stanza numbers do not determine Tibetan numbering.

`verification.json` records a direct check of 339 native selections and 1,434 displayed pādas. Every displayed line occurs verbatim and in order in its cited source span after those structural/annotation operations. Raw excerpts match their full-volume line ranges and the pinned volume hash is verified. This checks transcription fidelity, not identity of meaning with Pāli.

`pilot-selection-map.json` records the pilot selection spans. `tier2-selection-map.json` records the 231 new selections, pinned to their actual Derge opening and ending lines. Pāda indices refer to the importer’s shad-delimited chapter stream. Rockhill's numbers are discovery references, and the Derge source-line and folio locators cite the passages actually displayed.

Run `tools/import_tibetan.py --volume PATH` using the pinned source volume to regenerate the selections, verification, and research audit. The first 43 records are read from the tracked dataset, and the other 56 prior records regenerate from the pilot selection map.

## Reader outcomes

Across 423 positions, **291 present historical counterparts, 36 partial or provisional readings, and 96 without a displayed passage**. The six pilot chapters alone still have 82 present, four partial or related, and two not located among 88 positions. The Mind page has ten present and one not located. The 231 added native selections have direct verse-by-verse correspondence assessments based on wording and structure. Present records can preserve variants in wording or arrangement. The notes distinguish grouped passages, differing images, and provisional comparisons.


- Pāli 6 remains provisional and related: Tibetan 14.8 has a different conclusion about gentle speech. It is excluded from secure coverage.
- Pāli 106 has a provisional partial from Tibetan 24.26: monthly thousandfold offerings over a century are shared, but Tibetan contrasts them with faith in the Buddha rather than momentary homage to a developed person. It is excluded from secure coverage.
- Pāli 115 follows the independent concordance’s Tibetan 24.10, concerning the state difficult to see rather than the supreme Dhamma. It is partial.
- Pāli 229–230 correspond to one six-pāda Tibetan 29.51 stanza. Its first four pādas are aligned with 229, the last two with 230. Missing Pāli gods/Brahmā clauses are not invented; 230 is partial.
- Pāli 36, 101, and 109 remain not located. General mind-guarding, repeated word/stanza comparisons, and unrelated blessings have not been substituted. This does not claim absence throughout Tibetan literature.

Other recensional differences remain on individual records: the wheel cutting off a head at 1; source order and desire rather than Māra at 7–8; roof variants at 13–14; shorter 20; the taints conclusion at 27; expanded Self and mindfulness series; and extra clauses at 234, 292, and 293. Native wording is not harmonized to Pāli, Sanskrit, or Rockhill’s English.

## Full-26 independent concordance

W. Woodville Rockhill’s 1883 *Udânavarga: a collection of verses from the Buddhist canon* supplies an independent Tibetan–Pāli index on printed pp. 217–222. All six page images were read and checked. `rockhill-concordance-transcription.txt` retains factual references only. Imperfect OCR was not accepted without image inspection. Source: <https://archive.org/details/udnavargacolle00bkah>.

`correspondence-audit.json` has one record for every Pāli position and 26 chapter summaries. Its evidence levels distinguish:

1. **Native checked:** located Tibetan text directly checked against the pinned source; locators and correspondence qualifications recorded.
2. **Published reference:** Rockhill lists a parallel. This remains a separate evidence level for the 14 secure citations without a native passage on display.
3. **Tentative reference:** a printed question mark is retained. Pāli 395 / Tibetan 33.62 is excluded from secure totals.
4. **Unresolved:** no counterpart established by the consulted sources; not an absence claim.

The index gives **305 secure positions**. Direct native checks add 28 omitted positions, yielding **333/423 (78.7%) as a documentary lower bound**. This count includes secure published attestations without a displayed Derge counterpart. The display count also includes partial and provisional readings. The two numbers measure different evidence. The gaps leave room for future identifications. The lower bound measures correspondence attestation and cannot determine semantic similarity across six traditions.

`native_reviewed` counts considered reader outcomes, including not-located results. `native_checked` counts located text actually checked. Published parallels, secure attested union, direct native status, semantic grade, and same-title chapter counts remain separate.

Index and edition discrepancies are explicit. Rockhill’s index groups Pāli 31–32 under 4.28, whereas the directly checked native selections have their own locators. His 31.14 differs from the selected Derge good-roof/desire stanza. His index points 225 to related 20.19, while the matching bodily-restraint/deathless-state passage is directly checked at 7.7. Printed index numbers are not imposed on native text.

## Other sources

Ānandajoti Bhikkhu’s comparative Dhammapada supplied starting Indic correspondence references. They guided searches, but did not count as Tibetan proof. Bibliotheca Polyglotta (University of Oslo) supplied alignment metadata during the earlier 43-position work. It returned HTTP 500 during this expansion; new passages were checked against Derge and Rockhill. No license is assumed for modern alignments and no modern commentary is reproduced.

`rockhill1883-selected-ocr.json` preserves the earlier bounded, uncorrected OCR excerpts for tracing identifications. Native Tibetan spelling never comes from OCR. The public-domain 1883 English translation is not displayed in the reader.

The Derge colophon spells the Indian translator’s name བིདྱཱ་པྲ་བྷ་ཀ་ར. Oslo metadata conventionally identifies Vidyākaraprabhā. The source spelling is retained rather than silently normalized.

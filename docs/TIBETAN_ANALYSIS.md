# Tibetan contents audit for Rosettapada

Updated 4 November 2026. The reader now considers all 26 Pāli chapters. The 99 earlier Tibetan records were retained.

The reader displays 339 native Tibetan passages across 423 Pāli positions. These include 298 present and 41 partial or provisional readings. 84 positions have no selected native passage.

The published concordance indexes 305 secure Pāli positions. The combined documentary lower bound is 333/423, or 78.7%, using the concordance and additional native matches. Published references can remain in this total without a displayable Derge selection.

These counts measure source attestations and the native passages displayed. A present reading can differ from Pāli in wording, clause order, imagery, or length. The gaps record the scope of this search.

| Pāli chapter | Positions | Published | Attested lower bound | Native present | Native partial | No display selection |
|---|---:|---:|---:|---:|---:|---:|
| 1. Pairs | 20 | 19 | 19 | 19 | 1 | 0 |
| 2. Heedfulness | 12 | 7 | 12 | 12 | 0 | 0 |
| 3. Mind | 11 | 7 | 10 | 10 | 0 | 1 |
| 4. Flowers | 16 | 15 | 15 | 15 | 0 | 1 |
| 5. Fools | 16 | 16 | 16 | 15 | 1 | 0 |
| 6. The Wise | 14 | 7 | 7 | 7 | 0 | 7 |
| 7. Arhats | 10 | 5 | 5 | 4 | 1 | 5 |
| 8. Thousands | 16 | 13 | 13 | 12 | 2 | 2 |
| 9. Evil | 13 | 13 | 13 | 12 | 1 | 0 |
| 10. Violence / punishment | 17 | 15 | 15 | 13 | 2 | 2 |
| 11. Old Age | 11 | 9 | 9 | 3 | 6 | 2 |
| 12. Self | 10 | 10 | 10 | 10 | 0 | 0 |
| 13. World | 12 | 9 | 9 | 7 | 2 | 3 |
| 14. The Buddha | 18 | 14 | 14 | 12 | 2 | 4 |
| 15. Happiness | 12 | 10 | 10 | 10 | 0 | 2 |
| 16. The Dear | 12 | 8 | 8 | 8 | 0 | 4 |
| 17. Anger | 14 | 9 | 14 | 13 | 1 | 0 |
| 18. Stains | 21 | 9 | 9 | 8 | 1 | 12 |
| 19. The Just | 17 | 6 | 6 | 5 | 1 | 11 |
| 20. The Path | 17 | 13 | 14 | 13 | 1 | 3 |
| 21. Miscellaneous | 16 | 11 | 16 | 16 | 0 | 0 |
| 22. Hell | 14 | 10 | 10 | 7 | 3 | 4 |
| 23. Elephants | 14 | 12 | 12 | 12 | 0 | 2 |
| 24. Craving | 26 | 19 | 19 | 13 | 4 | 9 |
| 25. Monastics | 23 | 15 | 16 | 12 | 6 | 5 |
| 26. Brahmins | 41 | 24 | 32 | 30 | 6 | 5 |

## Selection method

Rockhill’s 1883 index on printed pages 217–222 supplied candidate references. The index was checked visually against the six page images during the pilot. The expansion checks the wording and boundaries of the native stanzas in the pinned Derge edition. Published verse numbers can identify neighboring variants and remain discovery references. The cited Derge folio and source line span identify each displayed passage.

The new selection map records native stanza spans and opening and closing anchors. This catches changes in paragraph segmentation or source markup on regeneration. It records textual variants and grouped correspondences where consequential. For example, the four truths fall within the same native stanza as the refuges at Pāli 190–191, and the shame and danger passages at 316–317 share a single native stanza.

Displayed native lines follow Derge Toh 326 in Esukhia’s Digital Derge Kangyur, volume 72. The import verifies the complete source hash, cited source-line excerpts, and the order of all displayed lines. Correspondence decisions remain editorial and await external review.

- [Rockhill 1883, Internet Archive](https://archive.org/details/udnavargacolle00bkah)
- [Pinned Derge source repository](https://github.com/Esukhia/derge-kangyur/tree/a582cf471b7c85a101035071078032f106a8e536)
- [Full correspondence ledger](../data/witnesses/sources/tibetan/correspondence-audit.json)
- [Tier 2 selection map](../data/witnesses/sources/tibetan/tier2-selection-map.json)
- [Native excerpts](../data/witnesses/sources/tibetan/selected-derge-excerpts.json)
- [Transcription verification](../data/witnesses/sources/tibetan/verification.json)

Regenerate with `python3 tools/import_tibetan.py --volume PATH` using the pinned volume. Use `--audit-only` to regenerate the evidence ledger from current reader data and the transcribed index.

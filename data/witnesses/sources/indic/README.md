# Indic witnesses across the Dhammapada

The Patna, Gāndhārī, and Sanskrit datasets each contain **423 Pāli position records** across all 26 chapters. The 99 previously published position records are identical to the six-chapter pilot and earlier Mind datasets. A gap indicates that the consulted edition lists no selected counterpart at that position.

## Sources and reproduction

The ancient verse texts and Pāli correspondence references follow the 26 chapters of Ānandajoti Bhikkhu's *A Comparative Edition of the Dhammapada*, fourth revised edition (April 2020). Its underlying editions are Margaret Cone's Patna Dharmapada, John Brough's Gāndhārī Dharmapada, and Franz Bernhard's Sanskrit Udānavarga. The exact URLs and complete working-HTML SHA-256 values accompany each dataset. All 26 cached HTML inputs were checked against the chapter-parity research source ledger.

`selected-source-passages.json` retains only selected ancient readings, original reference headings, source uncertainty/context markup, and factual source metadata. It omits modern commentary and unselected parallel works. The original download pages remain working inputs outside the repository. Selected text is not modernized or silently harmonized to Pāli; the edition's uncertain and conjectural readings, surviving lacunae, and contextual noncorresponding lines remain visible or documented in Notes.

The offline, standard-library importer reads the actual available selection from `data/chapters.json`:

```sh
python3 tools/import_indic.py /path/to/source-pages data/witnesses
```

Supply the 26 original `CD-xx-Name.htm` chapter files and `17-Atta.htm` from the separately checked Patna edition. The importer also accepts `indic-xx.html` chapter filenames from the research cache. It checks chapter anchors and asserts the known primary-source hash and text before applying the Patna correction below. Rerunning with identical source files deterministically reproduces the three datasets and selected passages.

Ancient texts and modern critical editions have different rights histories. Source attribution and [separate rights notices](https://ancient-buddhist-texts.net/Miscellaneous/Copyright-Notice.htm) are retained; no blanket project license is asserted. Cone's native digital edition states that the Pali Text Society retains the critical-edition copyright and granted reproduction permission to that edition.

## A verified source correction and retained differences

The comparative page for **Pāli 158** labels its Patna reading **317 [17.12]** but accidentally repeats the text of Patna 312, the counterpart of Pāli 157. The separately checked [native Patna chapter 17](https://ancient-buddhist-texts.net/Buddhist-Texts/C5-Patna/17-Atta.htm#PDhp_317) supplies the genuine stanza beginning **āttānam eva paṭhamaṁ**. The reader uses that native text. `corrections.json` retains the original duplicate, replacement, reason, source link, primary HTML hash, and line-break method. No Pāli words are used to reconstruct the Patna.

During the pilot expansion, **46 Patna readings** were also compared with their numbered verses in the native Cone/Ānandajoti digital edition. After ignoring punctuation and line breaks and applying the documented font mapping, 42 have identical letters. Four show edition differences at Pāli 106, 157, 224, and 290. `native-patna-check.json` retains the selected ancient text, result, primary source URLs, and HTML hashes. The new chapter imports were verified against the comparative edition.

At **Pāli 106**, two distinct Gāndhārī stanzas parallel different portions of the longer Pāli verse. Both references and texts are retained. The sheet displays the stanza about honoring a developed person for a moment, and Notes identifies the separate monthly-sacrifice stanza. At **129–130**, one Patna stanza and one Sanskrit stanza are aligned to both Pāli positions. **275–276** and **316–317** also show how the traditions divide related material differently. These remain separate source occurrences with their contextual lines marked. `corrections.json` documents some unusual spellings and notation retained from the comparative edition.

## Fragments and font characters

A standalone dot can mark a lost letter as well as a sequence of dots marking a larger lacuna. Both are classified as fragmentary. Sentence-final periods attached to a word are retained as punctuation. The source's struck contextual lines identify partial correspondence.

The pilot identified five private-use characters used by the site's original `ITM_TMS_UNI-Regular.ttf`. `../../normalization.json` maps them to standard Unicode for display. The original data retains the source code points. All selected Indic source headings and lines in the expanded collection are covered by the existing mappings.

## Coverage and limits

| Tradition | Present | Partial | Not located | Total positions |
| --- | ---: | ---: | ---: | ---: |
| Patna | 260 | 44 | 119 | 423 |
| Gāndhārī | 136 | 80 | 207 | 423 |
| Sanskrit | 292 | 77 | 54 | 423 |

These figures count positions with selected counterparts, including partial readings. One native passage may correspond to more than one position. Present means that the selected edition lists a counterpart with neither a marked lacuna nor struck contextual text in the record. Wording and chapter arrangement can still differ. Arhats has no selected Gāndhārī counterpart in the consulted edition.

`verification.json` records the 900 source occurrences and 3,872 lines confirmed by an independent DOM extraction, the unchanged earlier records, and the source-font mapping. The checks address transcription fidelity to the selected edition. Semantic closeness and manuscript collation require separate review.

## Restored line openings

The comparative pages sometimes omit the first characters of a verse line (for example *ṣa mārgo* for *eṣa mārgo* at Uv 12.8, or *aphalā* for *saphalā* at Uv 18.7, which reverses the sense). Each displayed line was compared with Bernhard's Udānavarga (GRETIL) and Cone's Patna Dharmapada (GRETIL), and every line-initial difference was confirmed in Ānandajoti's separate digital Udānavarga or Patna editions. `corrections.json` → `line_corrections` records 42 restorations with both citations; only the cited characters change, and `selected-source-passages.json` keeps the printed forms. At Uv 14.14 (Pāli 329) both of Ānandajoti's editions print *sa cel*, repeating the opening of 14.13; the display follows Bernhard's *no cel*. Gāndhārī has no comparable independent digital edition in reach; an internal scan found no sign of the same defect.

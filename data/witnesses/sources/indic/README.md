# Indic witnesses for the six-chapter pilot

The selected Patna, Gāndhārī, and Sanskrit passages cover the **88 Pāli positions** in Pairs (1–20), Heedfulness (21–32), Thousands (100–115), Self (157–166), Anger (221–234), and Miscellaneous (290–305). The earlier Mind page (33–43) remains available, so each dataset contains **99 position records**. A record with no located counterpart deliberately has no invented text.

## Sources and reproduction

The ancient verse texts and Pāli correspondence references follow Ānandajoti Bhikkhu's *A Comparative Edition of the Dhammapada*, fourth revised edition (April 2020), chapters 1, 2, 3, 8, 12, 17, and 21. Its underlying editions are Margaret Cone's Patna Dharmapada, John Brough's Gāndhārī Dharmapada, and Franz Bernhard's Sanskrit Udānavarga. The exact URLs and complete working-HTML SHA-256 values accompany each dataset. The first three source snapshots remain the previously retained selection; the four additional chapter pages were retrieved on 24 October 2026 and checked during the expanded pilot work.

`selected-source-passages.json` retains only selected ancient readings, original reference headings, source uncertainty/context markup, and factual source metadata. It omits modern commentary and unselected parallel works. The original download pages remain working inputs outside the repository. Selected text is not modernized or silently harmonized to Pāli; the edition's uncertain and conjectural readings, surviving lacunae, and contextual noncorresponding lines remain visible or documented in Notes.

The offline, standard-library importer reads the actual available selection from `data/chapters.json`:

```sh
python3 tools/import_indic.py /path/to/source-pages data/witnesses
```

Supply the seven original `CD-xx-Name.htm` chapter files and `17-Atta.htm` from the separately checked Patna edition. The importer also accepts `indic-xx.html` chapter filenames from the research cache. It asserts the known primary-source hash and text before applying the Patna correction below. Rerunning with identical source files deterministically reproduces the three datasets and selected passages.

Ancient texts and modern critical editions have different rights histories. Source attribution and [separate rights notices](https://ancient-buddhist-texts.net/Miscellaneous/Copyright-Notice.htm) are retained; no blanket project license is asserted. Cone's native digital edition states that the Pali Text Society retains the critical-edition copyright and granted reproduction permission to that edition.

## A verified source correction and retained differences

The comparative page for **Pāli 158** labels its Patna reading **317 [17.12]** but accidentally repeats the text of Patna 312, the counterpart of Pāli 157. The separately checked [native Patna chapter 17](https://ancient-buddhist-texts.net/Buddhist-Texts/C5-Patna/17-Atta.htm#PDhp_317) supplies the genuine stanza beginning **āttānam eva paṭhamaṁ**. The reader uses that native text. `corrections.json` retains the original duplicate, replacement, reason, source link, primary HTML hash, and line-break method. No Pāli words are used to reconstruct the Patna.

All **46 new Patna readings** were also compared with their actual numbered verses in the native Cone/Ānandajoti digital edition. After ignoring punctuation and line breaks and applying the documented font mapping, 42 have identical letters. Four show edition differences at Pāli 106, 157, 224, and 290. Their comparative readings are retained, with explicit notes; these differences are not silently resolved. `native-patna-check.json` retains the selected ancient text, result, primary source URLs, and HTML hashes. This comparison does not authenticate the ancient manuscript or settle the relative authority of the two electronic editions.

At **Pāli 106**, two distinct Gāndhārī stanzas parallel different portions of the longer Pāli verse. Both references and texts are retained. The sheet displays the stanza about honoring a developed person for a moment, and Notes identifies the separate monthly-sacrifice stanza. They are not combined into a new Gāndhārī verse.

## Fragments and font characters

A standalone dot can mark a lost letter as well as a sequence of dots marking a larger lacuna. Both are classified as fragmentary; sentence-final periods attached to a word are retained as punctuation. The source's struck contextual lines identify partial correspondence, not a conjecture. First-43 per-verse records remain identical to their preceding published dataset.

The new Gāndhārī passages include two additional private-use characters from the site's original `ITM_TMS_UNI-Regular.ttf`. Its actual cmap identifies **F83C** as `smacrondotbelow` and **F84F** as `gmacronacute`. `../../normalization.json` maps them to **ṣ̄** and **ḡ́** for display. The original data retains the source code points. The original font is not redistributed. The three earlier mappings remain unchanged.

## Coverage and limits

| Tradition | Present | Partial | Not located | Total positions |
| --- | ---: | ---: | ---: | ---: |
| Patna | 79 | 4 | 16 | 99 |
| Gāndhārī | 54 | 17 | 28 | 99 |
| Sanskrit | 77 | 15 | 7 | 99 |

Within the six-chapter, 88-position pilot alone, the respective present/partial/not-located counts are **71/3/14**, **53/11/24**, and **69/13/6**. These figures count selected counterparts, including partial readings; they do not claim identical wording, identical chapter arrangement, or absence throughout a language's literature.

`verification.json` records source-extraction checks, the unchanged earlier records, and the source-font mapping. A faithful transcription is a separate claim from an exact semantic correspondence or a complete manuscript collation.

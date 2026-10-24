# Chinese witness selection for Rosettapada

Scope: Pāli Dhammapada 1–43 only. The Chinese column uses historical Chinese recensions, with T210 preferred and explicitly referenced T212/T213 fallbacks. These are not new translations of Pāli. Ken Su's correspondence tables identify the relations; displayed text is checked against the pinned CBETA edition.

`correspondence-mapping.json` retains only correspondence identifiers and ancient verse quotations, omitting modern Pāli translations and commentary. The XML files retain complete TEI headers. Every XML body is a derived selection of exactly the displayed ancient verse passages: 38 readings from T210, two from T212, and three from T213. No unrelated verse or prose commentary is retained. Complete TEI header content, original chapter labels, decoded historical characters, source wording and punctuation, and original Taishō line markers are preserved. The chapter-level working copies are outside the repository in scratch. `cbeta-provenance.json` records original-download and selected-snapshot hashes.

`extract.py` resolves CBETA encoded characters through its character declarations. `build_chinese.py` derives the selected passages and generates modern Mandarin pinyin. These preparation scripts are not needed to build or run the static site. Optional regeneration requires Python, lxml, and pypinyin 0.55.0, then `python3 data/witnesses/sources/chinese/build_chinese.py`.

Pinyin is an editorial modern Mandarin aid, not historical pronunciation. Contextual corrections cover polyphonic characters and the historical characters 㺃 (gǒu) and 𠎝 (qiān). Source wording, punctuation, and meaningful recension differences are retained. The table's verse divisions can differ from CBETA punctuation. Exact Taishō line locators accompany every reading.

Coverage: 42 of the 43 Pāli verses have a displayed historical Chinese counterpart; no counterpart to Pāli 42 is identified in the selected table across T210/T212/T213. This is not a claim of absence from all Chinese Buddhist literature. The five fallback references are Pāli 3 → T212 15.7; 4 → T213 14.10; 30 → T213 4.24; 32 → T213 4.32; 34 → T212 32.2. Chinese 29 has two readings, with the horse counterpart displayed first.

See `CBETA-NOTICE.txt` and the source metadata for attribution and CC BY-NC-SA 4.0 reuse terms.

# Tibetan witnesses for the 43-verse reading sample

These files document historical Tibetan counterparts to Pāli Dhammapada 1–43. They are not newly made Tibetan translations. Research is bounded to this sample.

## Primary text

The display text comes from **Esukhia’s Digital Derge Kangyur**, Toh 326, *Ched du brjod pa’i tshoms* (Udānavarga), volume 72, *mdo sde sa*, folios 209a.1–253a.7.

- Repository: <https://github.com/Esukhia/derge-kangyur>
- Pinned commit: `a582cf471b7c85a101035071078032f106a8e536`
- Path: `text/072_མདོ་སྡེ།_ས.txt`
- Git blob: `d9abab24ddfc32ccd5dc65973cfbbef1dd6bd959`
- Complete volume size: `2787425` bytes
- Complete volume SHA-256: `437362220fde32d7c4e4311b4aa0885a5ab76612fe5efc0d9afd62605b763041`
- Accessed: 2026-10-24

The pinned [source README](https://github.com/Esukhia/derge-kangyur/blob/a582cf471b7c85a101035071078032f106a8e536/README.md) declares the electronic text **public domain**. A verbatim copy is retained as `esukhia-README.md`. The work’s colophon is at 253a.7. The repository explains that the digital edition preserves archaic spellings, carving mistakes, and variants; it is not an error-free critical edition.

Requested attribution: ཆོས་ཀྱི་འབྱུང་གནས། [1721–31], བཀའ་འགྱུར་སྡེ་དགེ་པར་མ།. Etexts from UVA, BDRC OCR, ACIP, and Adarsha combined and further proofread by Esukhia on behalf of Barom Theksum Choling, 2012–2018.

## What is retained

`selected-derge-excerpts.json` retains exact source lines containing the selected passages, including their folio markers and correction markup. Each excerpt records its line numbers in the complete pinned source file and a GitHub link to those lines. The opening work title and translation colophon are also retained for identification. This preserves enough adjacent source context to verify words that cross physical folio lines. The whole multi-text volume is not part of the site repository.

The application dataset is `../../tibetan.json`. It contains all 43 Pāli verse keys: 41 present counterparts, one provisional partial parallel (6), and one not-located counterpart (36). “Present” identifies a historical counterpart, not identity of wording or a new literal translation of Pāli.

Display preparation removes the folio markers, joins words split by physical source lines, and breaks the reading into shad-delimited pādas. These reading line breaks are editorial. They do not claim to reproduce the woodblock’s physical line breaks. Source spelling is retained: where the electronic source has `{original,correction suggestion}`, the first form is displayed and both forms are recorded in `source_annotations`. Tibetan stanza order is retained within each selection. No readings are silently harmonized to Pāli or Sanskrit.

`verification.json` records a direct text check of all 180 displayed pādas in 42 readings: each displayed line, including punctuation, occurs verbatim and in order within its cited source-line span after the stated structural and annotation operations. It also records the verified complete-volume SHA-256 and Git blob. This checks transcription fidelity; it does not remove the correspondence uncertainties below.

## Correspondence and uncertainties

Ānandajoti Bhikkhu’s comparative Dhammapada, chapters 1–3, supplies the starting Pāli–Sanskrit Udānavarga correspondence. Bibliotheca Polyglotta at the University of Oslo supplies Sanskrit–Tibetan alignment and edition metadata. The native text is checked against those identifications and against W. Woodville Rockhill’s 1883 translation of the Tibetan Udānavarga. Sanskrit verse numbers are cross-references; they are **not** assigned to the Tibetan source as though its order were identical.

Rockhill’s numbering is recorded separately where useful. His version and the Derge source differ in places. For example, this Derge source pairs the bad-roof/desire and good-roof/desire stanzas. Rockhill’s English sequence lacks the latter exact stanza, so that Derge reading is not assigned his verse number. The Sanskrit comparison remains Uv 31.17.

`rockhill1883-selected-ocr.json` retains bounded, uncorrected OCR excerpts from the public-domain 1883 edition. They document the identification of Tibetan 28.37 with Pāli 17 and Tibetan 28.39 with Pāli 18, on page 139 and in the concordance on page 217. This adds genuine Tibetan counterparts absent from the supplied Sanskrit mapping. Native Tibetan spelling is never taken from this OCR. Consult the [page images](https://archive.org/details/udnavargacolle00bkah) for typography and numbers.

Pāli 6 is represented only by a related Tibetan 14.8 passage. Shared motifs do not establish an exact correspondence: its conclusion concerns gentle speech and its wording differs substantially. Rockhill does not identify it as Pāli 6 in his concordance. It remains explicitly provisional and partial.

No sufficiently close Tibetan counterpart to Pāli 36 was located. Other verses about guarding mind have not been substituted. This records the limit of this bounded comparison; it is not a claim of absence throughout Tibetan literature.

Further visible recensional differences are noted on the individual records. The Tibetan counterpart of Pāli 1 ends with a wheel cutting off a head, and that of Pāli 27 ends with exhaustion of the taints. The shorter Tibetan counterpart of Pāli 20 is not padded out to the six pādas of Pāli.

The Derge colophon spells the Indian translator’s name བིདྱཱ་པྲ་བྷ་ཀ་ར. Oslo’s metadata identifies the translator as Vidyākaraprabhā; the discrepancy in name order is stated in the source metadata rather than silently corrected.

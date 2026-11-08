# Translation review — raw candidate list (unranked)

Reviewer stance: a specialist in the Dhammapada and its parallels (Pāli, Patna, Gāndhārī, Udānavarga, T210/T212/T213, Derge Toh 326), reading each English line against its own source line.
Format: ID · scope · kind · current → proposed · why. No changes have been applied.

## A. Whole-corpus findings (machine checks)

A1 · all · status label · "Rosettapada · X draft", "Alternate editorial drafts", "draft unavailable", pi.json id/label "Pāli-based draft" → drop "draft" (e.g. "Rosettapada · Patna translation"; "English from Patna"); notes copy to describe them as editorial translations with a review date. Why: the user's goal; labels are in build.py, reader.js, templates/index.html help card, templates/notes.html, data/english/pi.json label.
A2 · all alternates vs pi · person/gender · pi (main English) is gender-neutral (155 they/them vs 8 he/his); alternates use he/him heavily (pd 85, ga 95, sa 139, zh 72, bo 111), incl. the brahmin refrain "him I call a brahmin". → choose one policy. Options: (a) neutral throughout, matching pi; (b) keep masculine in alternates as closer to the grammatical gender of the witnesses, and say so in Notes. Why: switching the English source currently changes the voice as well as the witness.
A3 · alternates vs pi · term · bhikkhu/bhikṣu/苾芻/比丘/dge slong: pi "monastic" (29), alternates "monk" (pd 18, ga 23, sa 28, zh 19, bo 21) plus stray "mendicant" (pi 1, sa 2, bo 2: Heedfulness 31–32). → one term per corpus; at minimum remove "mendicant" strays.
A4 · all · spelling · corpus is American (color 18, honor 41, gray 5, traveler 6) with strays "colour" (bo 262) and "smouldering" (zh 418). → color, smoldering.
A5 · all · typography · 16 straight apostrophes (pd 1, bo 1, zh 15, pi 19, bo 19, zh 21, pi 34, 37, 43(zh, bo), 44, 45, 46, 49, 50, 62) → ’ (curly), as used everywhere else.
A6 · pi vs alternates · typography · em dash: pi unspaced ("alone and content—such a one", 362; "partners—", 345); alternates spaced " — " → pick one (spaced in alternates is the majority; pi's house style is unspaced). 
A7 · zh · punctuation · 72 Chinese verses end with ";" because the refrain "this is called a brahmin;" (是謂梵志；) and other T210 stanza-final ； were carried into English → end each verse with "." (T210 uses ； between stanzas of a series, which English does not need).
A8 · pi + early alternates · line policy · pi and the first-chapter alternates (Pairs/Heedfulness/Mind, e.g. ga 1–2, sa 1–2, 7–8, 13–14, pd 5, 13–14, 22, 26, 28; ga 33–40 compressed to one line) use English sense lines; all later alternates are line-for-line with their witness. → bring early alternates to line-for-line (Notes say English uses its own lines, so pi may keep sense lines; but the alternates should be uniform). ga 34, 37–40 collapse four Gāndhārī lines into one English line though only line 1 survives — acceptable, but line-for-line with "[…]" lines would show the lacuna shape.
A9 · cross-verse refrains · consistency (each pair has identical source text):
  - pi 396 "Claiming nothing, grasping nothing" vs 421 "holding nothing and grasping nothing" (akiñcanaṁ anādānaṁ).
  - pi 172–173 "freed from a cloud" vs 382 "released from clouds" (abbhā muttova candimā).
  - pi 80 "Fletchers shape the arrow" vs 145 "Arrow-makers straighten their shafts" (usukārā namayanti tejanaṁ).
  - pi 69 "When the wrongdoing ripens" vs 119 "When the evil ripens" (yadā ca paccati pāpaṁ).
  - pi 161 "The evil you do yourself" vs 165 "By your own doing is evil done" (attanā hi kataṁ pāpaṁ) — 165 is a different stanza but same opening.
  - pi 238 vs 348 "never come to birth and aging again" / "come again to neither birth nor old age".
  - bo 401 "tip of a reed" vs 407 "tip of a needle" (same Tibetan སྨྱུང་བུའི་རྩེ).
  - bo 278 "becomes purity" vs 277, 279 "becomes purification" (same line).
  - bo 110–115 refrain "who lives / who live / and lives a hundred years", 197–200 "ah" vs "oh" (199).
  - bo/sa 31–32 "A mendicant who delights in heedfulness" vs 327 "The monk who…" (see A3).
  - sa 397 "well-gone" vs 419 "well gone" (sugato).
  - zh 404 "without the fears of the homeless" vs 411 "with no fear of homelessness" (無家之畏) — meanings differ; one is wrong (see review).
  - zh 401 "as a snake sheds its skin" vs 407 "like a snake shedding its skin" (如蛇脫皮).
  - pd 23 "safety" vs 368 "security" from bondage (yogacchemaṁ anuttaraṁ).
  - ga 393 "put away evils" vs 265 "removed evils" (brahetva pavaṇa).
  - ga 396 "grasping nothing" vs 421 "taking nothing" (aṇadaṇa).

## B. Pāli-based English (pi.json, the default English)

B1 · pi 11 · sense · "taking substance for emptiness" → "and the substantial as without substance". Why: "emptiness" imports suññatā; the Pāli only says asāra (no core).
B2 · pi 13–14 · term · rāgo "Desire" → "Passion" (pi uses passion for rāga at 20, 202, 251; desire is kept for kāma/icchā).
B3 · pi 31–32 · term · pamāde "sees danger in neglect" → "in heedlessness" (the chapter's key pair is heedfulness/heedlessness; neglect breaks it).
B4 · pi 33, 80, 145 · consistency · usukāra … tejanaṁ: "fletcher straightens an arrow" / "Fletchers shape the arrow" / "Arrow-makers straighten their shafts" → "Fletchers straighten arrows" throughout.
B5 · pi 36 · omission · "the mind is worth guarding" → "let the wise guard the mind" (cittaṁ rakkhetha medhāvī; 35 is "worth taming" because of sādhu, 36 is an imperative with a subject).
B6 · pi 46 · sense · "Cut down Māra's blossoms" → "Cut Māra's flower-tipped arrows" (papupphaka; Norman, Ṭhānissaro; commentary: the three rounds). Add a one-line note. Optional: keep "blossoms" and note the arrow reading.
B7 · pi 56 · weak · "those who live well" → "the virtuous" (sīlavataṁ; the stanza contrasts the scent of sīla).
B8 · pi 61 · sense · "There is no fellowship in folly" → "There is no companionship with a fool" (natthi bāle sahāyatā; cf. 330, rendered differently again).
B9 · pi 78 · line order · English opens with "Keep company with good friends" beside Pāli "Na bhaje pāpake mitte"; the four lines are in reverse order → reorder so line 1 = do not keep company with bad friends.
B10 · pi 84 · addition · line 2 "…a kingdom through wrongdoing" duplicates line 3's adhammena → line 2 "do not wish for children, wealth, or a kingdom;" (adhammena belongs to line 3).
B11 · pi 94 · sense · "held in esteem even by the gods" → "even the gods envy such a one" (pihayanti = long for, envy).
B12 · pi 20 vs 202/251 etc. · term · dosa "aversion" (20) vs "hatred" (6×) → one rendering (hatred is the majority).
B13 · pi 39 · style · "free of seepage" → "not soaked with lust" or "untainted" (anavassuta; commentary rāgena anavassuta). Low priority.
B14 · pi 60 · diacritics · "saṃsāra" uses ṃ while the site's Pāli and other English use ṁ → check and unify.
B15 · pi 159 · grammar · "For oneself, they say, / is hard to tame." → "For the self, they say, / is hard to tame." (current line is ungrammatical).
B16 · pi 142 · term · "a brahmin, an ascetic, a mendicant" — only "mendicant" in pi; elsewhere bhikkhu = "monastic" → "a monastic" (or keep "mendicant" deliberately for the begging sense and note it; see A3).
B17 · pi 91 vs 175 · consistency · haṁsā "wild geese" (91) vs "Swans" (175) → one rendering (most current translators: swans; ornithologically: geese). Low.
B18 · pi 184 · force · "A renunciant does not injure another" → "One who injures another is no renunciant" (definitional, parallel to line 4).
B19 · pi 225 · literalness · "always restrained in what they do" → "always restrained in body" (kāyena). Low.
B20 · pi 143 · source · English follows nindaṁ (reproach) although the displayed Pāli reads niddaṁ (sleep). Documented in the note; an expert might prefer translating the displayed text ("who rouses from sleep") and moving the nindaṁ reading into the note. Judgment call.
B21 · pi 307 · spelling · "ocher" → "ochre" (pi 9–10 and every alternate use ochre).
B22 · pi 246 vs 309–310 · consistency · paradāra "another's spouse" (246) vs "another's wife" (309, 310). Pick one. Literal = wife; the alternates all say wife(s).
B23 · pi 247 · voice · "whoever gives himself over … digs up his own roots" is masculine inside the gender-neutral pi text → "themselves … their own roots" if A2 settles on neutral (309–310 and 284 are legitimately male in the Pāli and can stay).
B24 · pi 253 · voice shift · imperative "Keep looking for the faults of others…" then "Their ending is far off" — the Pāli is third person → "For one who keeps looking for others' faults, / always finding cause to complain, / the taints only grow; / such a one is far from their ending."
B25 · pi 269 · vagueness · "One who weighs both sides of life" → "One who weighs both worlds" (ubho loke).
B26 · pi 285 · sense · "Sever the hold of self-attachment" → "Cut off your affection" (sinehamattano: one's own affection, not attachment to self). Low.
B27 · pi 295 · sense · "two learned kings" → "two brahmin kings" (sotthiya = learned brahmin; the commentary's pairing is warrior kings in 294, brahmin kings in 295).
B28 · pi 60 + pd/sa/bo · diacritics · "saṃsāra" with ṃ in pi 60, pd 1×, sa 1×, bo 3×; the site's Pāli uses ṁ and other English uses "saṁsāra" → unify on saṁsāra.
B29 · pi 337 · grammar · "Let Māra never break you again and again" (double negative/iterative clash) → "Do not let Māra break you again and again".
B30 · pi 352 · syntax · "One who bears their final body, / a great person of great wisdom, they are called." → "is called ‘one in their final body, / a great person of great wisdom.’"
B31 · pi 345 · consistency · dāresu "children and partners" — see B22 (wife/spouse/partner policy; alternates have "sons and wives").
B32 · pi 371, 396 · typography · speech in single quotes (‘This hurts!’, ‘bho.’) while pi uses double quotes for direct speech elsewhere (3–4, 17–18, 62, 74, 272, 286) → “ ”.
B33 · pi 335 vs 337 · consistency · bīraṇa "grass" (335) vs "vetiver" (337) → "like bīraṇa grass after rain" or "vetiver grass" in both. Low.
B34 · pi 355 · interpretation · "destroy themselves as well as others" (hanti aññeva attanaṁ) — Norman/Ṭhānissaro read "as if he were another / as he would another". Consider "destroy themselves as they would an enemy" or add a note. Judgment call.

## C. Patna (pd) alternates

C1 · pd 1 vs ga 1 · spelling · "draught animal's foot" (pd 1) vs "draft animal's track" (ga 1) → American "draft" (see A4).
C2 · pd 168 · lacuna placement · "one who lives the Dhamma sleeps […] at ease" — the lost word is the one meaning "at ease" (sukhaṁ, cf. 169) → "one who lives the Dhamma […] sleeps" or mark the restoration "[at ease]".
C3 · pd 155 vs pi 155 · consistency · kroñca "old herons" (pd) vs koñca "old cranes" (pi) → one bird (crane is the usual rendering).
C4 · pd 73 · sense · "The bad want esteem" for asatāṁ bhāvanam icchanti → "They want esteem they do not deserve" (asatāṁ = asantaṁ, unreal/undeserved, as Pāli 73), or note the ambiguity. Low.
C5 · pd 83 · sense · "Good people are good in every place" (sabbattha … bhavanti) — speculative; consider "Everywhere, good people remain good" or note that Patna differs from Pāli cajanti. Low.
C6 · pd 46 · consistency · "Māra's flowers" — follows pi; revisit with B6 (flower-tipped arrows).
C7 · pd 189 · contradiction · Printed Patna 217 line 3 lacks the negative (etaṁ śaraṇam āgaṁma), so the English says "having come to that refuge / one is freed from all suffering" inside a stanza that denies the refuge. Either check Cone's Patna for a negated reading, or keep the literal English and add a note that the negation of lines 1–2 is evidently meant to carry over. As it stands a reader sees the opposite of the argument.
C8 · pd 243 · sense · "ignorance is the deadly stain" for avijjā maraṇaṁ malaṁ, but the next line says "these stains" (ete male, plural) and pi's own note says Patna names ignorance and death → "ignorance and death are the stains".
C9 · pd 334 · subject · "he leaps from here to there" — Patna has feminine sā, which pi's note says makes craving the subject → "it leaps from here to there".
C10 · pd 245 · sense · alīnena "unattached" → "unshrinking" (alīna = not sluggish; pi 245 has "unshrinking").
C11 · pd 307 · consistency · kāṣāya "saffron robes" → "ochre" (ochre everywhere else for kāṣāya/kāsāva).
C12 · pd 376 · person · "Keep company with good friends … be friendly in his ways" → "in your ways" (imperative throughout).
C13 · pd 323 · style · "as the tamed one goes / by a self well tamed, tamed." → "as one tamed goes there / by means of a well-tamed self."
C14 · pd 236 · note · "the second noble ground" (bitiyaṁ) where Pāli has dibbaṁ ("heavenly") — literal but puzzling; add a short note or check Cone's reading.
C15 · pd 327 · consistency · duggā "out of the difficult road" vs pi "out of the mire" → "out of the bog/difficult place". Low.
C16 · pd 368 vs pi · term · mettā "loving-kindness" (pd) vs "goodwill" (pi) — pick one across the corpus. Low.
C17 · pd 227 vs ga 227 · names · Patna "ādhora" kept as "Ādhora", Gāndhārī "adura" normalized to "Atula" → one policy (keep each witness's form, or normalize both to Atula and note the spellings).

## D. Gāndhārī (ga) alternates

D1 · ga 7–8 · mood · "Dwell on what is attractive, … and passion will overpower you" reads as an instruction to do the harmful thing; the Gāndhārī is descriptive (viharadu, "one dwelling") → "One who dwells on what is attractive, … is overpowered by passion" (and 8 likewise).
D2 · ga 84 · sense · "One who, not for his own sake nor another's, / would commit evil deeds" reads as if he commits them → "One who would commit no evil deed / for his own sake or another's" (the negative governs the whole clause; cf. Brough).
D3 · ga 245 · sense · aliṇeṇa "unattached" → "unshrinking" (same as C10).
D4 · ga 31–32 · term · "sees danger in neglect" → "in heedlessness" (same as B3; the alternates copied pi).
D5 · ga · lacuna policy · Lacunae are handled three ways: "[…]" (most), bracketed restorations of part-words ("[Th]ough" 101, "[Very hap]pily" 199, "[Hun]ger" 203, "[but the stead]fast" 207, "By [causing] others [pain]" 291, "[the taints]" 293, "[be guarded]" 315), and a whole bracketed line ("[Not by a shaven head is one] an ascetic" 264; "[nor far-and-near shore] […]" 385). → adopt one stated policy (e.g. restore in brackets only where a parallel makes the wording certain; otherwise "[…]") and say so in Notes. 385's "[restoration] […]" double-marking should become one or the other.
D6 · ga 253 vs 292 · consistency · the same Gāndhārī stanza is translated two ways: 253 gives lines 1–2 as bare "[…]" and adds "[…]" to line 3; 292 translates the surviving words ("What is to be done is neglected […]", "[…] is done", "of the haughty and heedless"). → use the 292 rendering in both.
D7 · ga 296–299 · grammar · "these disciples of Gotama, / who by day and by night / is always mindful of the Buddha" — plural subject, singular verb → "whose mindfulness, by day and by night, / is always on the Buddha" (yeṣa … svadi), and likewise Dharma, Saṅgha, body.
D8 · ga 294 · sense · "two kings and two learned brahmins" adds two persons; rayaṇa dvayu śotria = two learned (brahmin) kings → "two learned kings" (cf. B27).
D9 · ga 390 · clarity · "Nothing is of this kind for a brahmin, / when he does not hold the mind back from what is dear" is opaque → "Nothing is gained by a brahmin / who does not hold his mind back from what is dear" (Brough's construal), keep "there, they say, is the truth" for line 4.
D10 · ga 280 · source fidelity · line 3 "sluggish" renders Patna kusīdo, but the Gāndhārī has svadima (= smṛtimā, "mindful", likely corrupt) → translate as printed with a note, or mark as uncertain. Low.
D11 · ga 396 vs pi 396 · consistency · "sir-sayer" (ga) vs "one who says ‘bho’" (pi). Either is fine; one rendering across English sources would read better. Low.

## E. Sanskrit Udānavarga (sa) alternates

E1 · sa 3–4 · sense/person · "He reviled me, he overcame me, / he might rob me." — ākrośan, avocan, ajayan are third-person plural, and avocan means "spoke (against)", not "overcame" → "They reviled me, spoke against me, / defeated me, would rob me."
E2 · sa 105 · sense · "nor Māra with the brahmins" for na māro brāhmaṇā saha — the line parallels Pāli brahmunā (with Brahmā); Bernhard's Uv 23.4 reads brahmaṇā → "nor Māra with Brahmā" (and a note on the printed long ā if retained).
E3 · pd/ga/sa 1–2 · consistency · the same Indic word dharmā is "all states" (pd), "experience" (ga, matching pi), "phenomena" (sa) → one rendering across the three Indic witnesses unless a difference is meant; pi's note can carry the interpretive range.
E4 · sa 31–32 · term · "mendicant" → match the corpus term for bhikṣu (see A3).
E5 · sa 54 · gloss · "vāhnija" is left untranslated → gloss or render (an aromatic; often taken as saffron/agaru) and keep the term in a note. Low.
E6 · sa 23 vs pd 23/368 · consistency · yogakṣema "the refuge beyond compare" (sa) vs "safety/security from bondage" (pd) → one rendering. Low.
E7 · sa 193 · sense · puruṣo jātyo "the person of noble birth" — jātya here is "thoroughbred, well-bred" (pd 193 has "thoroughbred person"); "noble birth" cuts against the chapter's point → "the thoroughbred person".
E8 · sa 218 · source · "not flowing out" translates anavasrāvī, but the displayed text reads avasrāvī → check Bernhard (Uv 2.9) and either correct the display (via the line-corrections file) or note it.
E9 · sa 263 · display · the Sanskrit line shows "caiv≈ / ≈āhiṁsā" (sandhi-split markers from the source) → render as caivāhiṁsā or document the convention. Not an English issue, but a reader sees it beside the English.
E10 · sa 296–299 · grammar · same plural/singular error as D7 ("these disciples of Gautama, / who by day and by night / is always mindful of the Buddha") → "whose mindfulness … is always on the Buddha".
E11 · sa 307 · consistency · "saffron robes" → "ochre" (as C11).
E12 · sa 359 · source · line 2 says craving (tṛṣṇādoṣā) but line 3 keeps vigatamohebhyo ("free of delusion"), and the English faithfully says delusion → check Bernhard (Uv 16.?/29.?) for vigatatṛṣṇebhyo; if the display has inherited a slip, add a line correction and change the English to "free of craving".
E13 · sa 376 · source · "Keep fitting company in moderation" renders mātraṁ bhajeta pratirūpaṁ; the parallel (Pāli mitte bhajassu, Gāndhārī mitra bhayea) points to mitraṁ → check Bernhard; likely "Keep company with fitting friends".
E14 · sa 306 · clarity · "and also one who does some other deed here" (yaś cānyad apy ācaratīha karma) → "and one who does other than he says" or keep literal with a note.
E15 · sa 315 · style · "one should guard it well guarded" → "one should guard it closely".
E16 · sa 314 · display · line 8 shows "andate" (dropped n of nandate) — a dropped-letter case the earlier Sanskrit audit did not catch → add to line corrections if Bernhard reads nandate.
D8-revision · ga 294 · note · Sanskrit 294 has rājānaṁ (sg.) dvau ca śrotriyau, "the king and two learned brahmins", which supports the current Gāndhārī English; D8 should be downgraded to "check Brough" rather than a correction.

## F. Classical Chinese (zh) alternates

F1 · zh 3 · sense · 勝我不勝 rendered as a question ("Will I win, or will I lose?") → it reports the grievance: "‘They cursed me and beat me; I did not win’ — / one who indulges such thoughts / never sees the end of enmity." (matches the Indic "defeated me" and zh 4's 彼勝我不勝).
F2 · zh 70 · sense · 於十六分，未一思法 "of sixteen parts, / not one is a thought of the Dharma" loses the comparison → "is not worth one sixteenth / of a single thought on the Dharma".
F3 · zh 21 · term · 戒為甘露道 "Discipline is the way to the deathless" — in this chapter 戒 stands for appamāda (vigilance, being on guard), as the next line's 放逸 shows → "Vigilance is the way to the deathless".
F4 · zh 21 vs 114 · consistency · 甘露 is "the deathless" (21) but "sweet dew" (114, twice) → one rendering across zh (e.g. "the deathless" everywhere, with a note that the Chinese image is sweet dew; or "sweet dew" everywhere).
F5 · zh 89 et al. · term · 漏 "outflows" (89, 2×) vs "taints" (1×) and every other tradition's "taints" → "taints".
F6 · zh 71 · sense · 如搆牛乳 "as when milking a cow" — the point is that fresh milk does not curdle at once → "as milk fresh from the cow does not turn at once".
F7 · zh 107 vs pi note 107 · consistency · 三尊 "the Three Jewels" (zh English) vs "the Three Honored Ones" (pi note) → "the Three Honored Ones" (literal) in both, or Jewels in both.
F8 · zh 69 / 119 · data · both carry the note "This source stanza is shared by Pāli 69, 119" but display different T210 stanzas (過罪未熟 / 妖𦾨見福) → fix the note or the assignment.
F9 · zh 34 · sense · 魔眾而奔馳 "rushes among the hosts of Māra" — can equally be "flees from Māra's hosts" (cf. Pāli: to escape Māra's realm). Low; consider the escape reading.
F10 · zh 266 · parse · 所謂比丘，非時乞食 "is not one who begs at the wrong time" — 非 negates the predicate, as in the parallel lines 264 (非必除髮) and 268 (非口不言) → "is not one who merely begs for food at mealtimes".
F11 · zh 203, 277, 278 · term · 行 (saṁskāra) "activity/activities" → "formations" (or "conditioned things"), matching every other tradition's rendering of the same item in the same stanza family.
F12 · zh 193 · term · 明人 "An enlightened person" — "enlighten" appears only twice in the whole corpus; the rest says "awakened" → "A person of insight" or "A clear-sighted person".
F13 · zh 243 · mood · 比丘無垢 "monks are without stain" → "monks, be without stain" (exhortation, cf. Pāli nimmalā hotha bhikkhavo). Low.
F14 · zh 204, 205, 271 · obscure lines · 厚為最友 ("trust" is borrowed from the Indic; 厚 = closeness), 解知念待味 ("the taste of mindfulness and waiting"), 戒眾不言 ("The precepts are many and need no words") read as guesses → mark as uncertain in a note, or revise after checking a modern Faju jing commentary. Low.
F15 · zh 396 · negation · 非剃為沙門，稱吉為梵志 — 非 governs both lines ("Not by shaving is one an ascetic, / nor by calling oneself auspicious a brahmin"), but line 2 currently reads "calling oneself auspicious makes a brahmin", the opposite of the stanza's point.
F16 · zh 404 · sense · 無家之畏 "without the fears of the homeless" → "with no fear of homelessness" (as zh 411; see A9).
F17 · zh 329 · sense · 廣斷王邑里 "cut off widely the king’s town and village" is unreadable → "as a king leaves his realm and towns behind" (the Indic king-abandoning-a-kingdom image).
F18 · zh 326 · sense · 本意為純行 "The mind once ran in pure conduct" contradicts the stanza (which goes on to subdue the mind); the image is the mind formerly going its own way → check T210 glosses; probably "Formerly the mind went as it pleased".
F19 · zh 389 · sense · 不放梵志 "do not let a brahmin go" → "nor should a brahmin let loose (at his attacker)", matching the Indic let-loose sense; and line 4 "shame too on letting go" → "shame too on the one who lets loose".
F20 · zh 294 · sense · 率君二臣 "leads the lord and two ministers" → "removes the lord and his two ministers" (率 here = sweep away). Low.
F21 · zh 311 · clarity · 獄錄乃自賊 "enrolls one in hell as one's own thief" → "puts one on hell's register, robbing oneself". Low.
F22 · zh 368, 381 · term · 滅行 "activity extinguished" → "formations stilled" (see F11).

## G. Tibetan (bo) alternates

G1 · bo 73 · grammar · "The base wish for gain, / wish for a following of monks, / are possessive of dwellings, / and wish for offerings…" — "The base wish" reads as a noun phrase and the verbs don't agree → "Base people want gain, / want a following of monks, / are possessive of dwellings, / and want offerings from other families."
G2 · bo 89 · syntax · "Those who, the seven factors of awakening / having well cultivated in mind," mirrors Tibetan word order and is not English → "Those who have well cultivated in mind / the seven factors of awakening,".
G3 · bo 9 · punctuation · "One who still harbors impurities / puts on the ochre robe." — the period turns the relative clause into a statement → comma: "One who still harbors impurities / and puts on the ochre robe, / without restraint or gentleness, / is unfit to wear it."
G4 · bo 93 vs sa 93 · consistency · ཕ་མཐར་རྟེན་མེད "depend on no further end" vs Sanskrit aparāntaṁ nāśritāḥ "do not depend on what lies ahead" → use the clearer sa wording in bo.
G5 · bo 44–45 · note · ཆོས་བཞི "the fourfold Dharma" is puzzling where the parallels have dharmapada; add a note (possible reading ཆོས་ཚིག, "words of Dharma") or check the Derge folio. Low.
G6 · bo 31–32 · term · "mendicant" → corpus term for dge slong (A3).
G7 · bo 123 · parse · "As one with great wealth avoids few companions, / a merchant a dangerous road" — misparse: the Tibetan describes one merchant "with great wealth and few companions" who avoids a dangerous road → "As a merchant with great wealth and few companions / avoids a dangerous road, / and one who wants to live avoids poison, / so the wise should avoid wrongdoing."
G8 · bo 179–180 · sense · འགྲོ་མེད "who goes nowhere" → "trackless" (the Buddha leaves no track; the other traditions all say trackless).
G9 · bo 184 · sense · "Patience is the supreme austerity; patience — / nirvāṇa is supreme, say the buddhas" leaves "patience —" dangling → either "patience is supreme nirvāṇa, the buddhas say" (if the Tibetan identifies them) or "patience and forbearance; / nirvāṇa is supreme, say the buddhas" (matching Uv titīkṣā). Check the Derge line.
G10 · bo 157 · style · "guard this, with protection, well" → "guard it well and closely". Low.
G11 · bo 188 · word order · "People stricken by fear / mostly to mountains and forests, / … and to trees go for refuge" — verb held to line 4 reads oddly → "People stricken by fear / mostly go for refuge / to mountains and forests, / to parks, shrines, and trees." Low.
G12 · bo 151, 153 · clarity · 151 "it makes other noble ones understand" and 153 "from now on you are driven out" are uncertain construals → mark as uncertain or revise after a second reading of the Derge lines. Low.
G13 · bo 260 · sense · "Until the head has turned gray / one has not yet reached the rank of elder" implies that gray hair confers eldership, the opposite of the stanza → "Though the head has turned gray, / one has not thereby become an elder; / that is only youth come to its end; / such a one is called an old fool."
G14 · bo 219 · typography · "crying “Ah!”," (comma after the closing quote and exclamation) → "crying out with joy, “Ah!”" or end the line without the comma.
G15 · bo 221 · style · "owning nothing, do not fall after attachments" → "owning nothing, attachments do not befall them". Low.
G16 · bo 315 · consistency · དགོན་པའི་གྲོང་ཁྱེར "a city in the wilderness" vs every other tradition's "frontier city" → "a border city". Low.
G17 · bo 309 · sense · "these four states come to mind" → "these four things befall". Low.
G18 · bo 404 · sense · "wanting little, not gone forth from home" (འདོད་ཆུང་ཁྱིམ་ནས་མ་བྱུང) says the brahmin stays at home, against the stanza (the parallels: homeless wanderer) → check the Derge line; likely "wanting little, not frequenting houses" or similar.
G19 · bo 396 · sense · "is taught to be called by the name “son”" — བུ here very probably transliterates bho (the "bho-sayer" of Pāli/Sanskrit/Gāndhārī) → "is called a ‘bho’-sayer" with a note on the spelling.
G20 · bo 321 · brackets · "whoever [bears] harsh words" supplies a verb in square brackets — the only supplied word in bo; fold into the lacuna/supplement policy (D5) and say so in Notes, or drop the brackets.
G21 · bo 334, 341 · style · "People who recollect and attach" → "People who remember and cling". Low.
G22 · bo 371, 383 · uncertain · 371 "the desire for heaps of things" (ཕུང་ཁྲོལ) and 383 "the sage alone does not attain it" are uncertain construals → mark or revise after a second reading. Low.
G23 · bo 401 vs 407 · consistency · སྨྱུང་བུ "reed" vs "needle" (see A9) → one rendering ("reed", literal; note that the Indic has an awl/needle point).

## H. Method notes for whoever applies changes

H1 · Every alternate was drafted by one translator in one pass; nothing has had a second reader. Taking them out of draft status should be paired with a short Notes paragraph saying what the English is (editorial translation of the displayed reading, line by line where possible), what it is not (not a critical edition), and the review date.
H2 · Many alternates were built by adapting the Pāli-based English and kept its wording where the witness agrees. That is efficient but it is also how B3/D4 ("neglect") and the "mendicant" strays spread. Fix the shared rendering once, then propagate.
H3 · After changes: rebuild, run tools/check.py and node --check reader.js, spot-check the changed verses in a browser, publish, verify live (per AGENTS.md).

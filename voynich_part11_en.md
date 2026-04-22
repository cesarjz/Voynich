# PART XI — Two-Tier Encoding and Structural Decoding (Chapters 35.11–36)

## **35.11 Two-tier encoding discovery (notebooks `36_silpart_structure.ipynb`, `37_distributional_clustering.ipynb`, `38_constructed_languages.ipynb`)**

The failure of 19 monoalphabetic models motivates a deeper structural analysis of the SilPart positional pools. Instead of asking "what language is encoded?", this section asks "what kind of encoding mechanism produces this structure?"

**Design:** Each of the 166 distinct glyphs is classified by its transition probability (TP) profile into two tiers:

- **Tier-1 (structural):** glyphs with high positional fidelity (TP ≥ threshold), accounting for 48.3% of tokens. These glyphs operate as structural markers — deterministic position selectors that define syllabic boundaries.
- **Tier-2 (content):** glyphs with lower positional fidelity (TP < threshold), accounting for 51.7% of tokens. These glyphs carry the variable content and show more distributional flexibility.

**Key metrics:**

- **Utilisation:** only 6.7% of the possible Tier-2 bigram combinations actually occur in the text — 93.3% of combinatorial space is forbidden.
- **Onset/coda ratio:** 1.95 — onsets are nearly twice as frequent as codas, indicating an asymmetric syllabic template.
- **Tier-1 entropy:** significantly lower than Tier-2, confirming the structural vs. content distinction.

**Distributional clustering** (notebook 37) applies hierarchical clustering to onset and coda glyph distributions. Onsets cluster into 4–6 functional groups; codas into 3–4 groups. The clusters do not correspond to any known natural language phonological categories.

**Comparison with constructed languages** (notebook 38): the Voynich two-tier metrics are compared against Esperanto, Enochian (Dee/Kelley), and Lingua Ignota (Hildegard von Bingen). No natural language in the control set (Hebrew, Latin, Arabic, Turkish, Finnish) shows a comparable two-tier separation. Esperanto is the closest match, sharing the structural regularity but not the extreme utilisation restriction. Enochian shows superficial similarities but lacks the positional consistency. **No known system — natural or constructed — reproduces the full Voynich fingerprint.**

Notebooks: `36_silpart_structure.ipynb`, `37_distributional_clustering.ipynb`, `38_constructed_languages.ipynb`
Results: `silpart_structure_resultados.json`, `distributional_clustering_resultados.json`, `constructed_languages_resultados.json`

## **35.12 Herbal section: onset clusters vs. plant categories (notebook `39_herbal_onset_analysis.ipynb`)**

If Tier-1 onsets encode a topic category (e.g., plant type in herbal pages), then herbal folios assigned to the same plant category should share onset distributions. This section tests whether the onset cluster structure correlates with botanical content.

**Design:** The 130 herbal folios are grouped by plant category (as assigned by standard Voynich botanical studies). For each folio, the onset glyph distribution is computed. A permutation test evaluates whether within-category similarity exceeds between-category similarity.

**Result:** The permutation test yields p = 0.336 — **onsets do not encode plant categories**. The onset distributions do not cluster by botanical content within the herbal section.

However, a complementary test at the **section level** (herbal vs. astronomical vs. biological vs. pharmaceutical) shows highly significant separation (p < 10^−84). The onset distributions differ dramatically across manuscript sections, confirming that **section-level encoding is real** but operates at a coarser granularity than individual plant categories.

Notebook: `39_herbal_onset_analysis.ipynb`
Results: `herbal_onset_resultados.json`

## **35.13 Medieval recipe code simulation (notebook `40_recipe_code_simulation.ipynb`)**

The 6.7% utilisation rate — meaning 93% of possible glyph combinations are forbidden — is the most distinctive structural feature uncovered by the two-tier analysis. This section asks: what kind of real-world encoding system could produce such extreme combinatorial restriction?

**Design:** A Monte Carlo simulation models a **constrained code** inspired by medieval recipe/pharmacopoeial traditions, where a fixed set of structural markers (ingredients, actions, quantities) combine with content glyphs under strict combinatorial rules. The simulation sweeps the parameter p_valid (probability that a random combination is permitted) and compares the resulting utilisation rate against the Voynich's observed 6.7%.

**Result:** A constrained code with p_valid ≈ 0.08 matches the observed utilisation. This means approximately **92% of glyph combinations are forbidden** by the encoding rules — consistent with a system where structural markers impose rigid syntactic constraints on which content elements can follow.

The simulation also reproduces the onset/coda asymmetry and the Tier-1/Tier-2 token ratio when the structural vocabulary is smaller than the content vocabulary. This does not prove the Voynich is a recipe code, but it demonstrates that the observed statistics are **compatible with a constrained combinatorial encoding** rather than a natural language or a simple substitution cipher.

Notebook: `40_recipe_code_simulation.ipynb`
Results: `recipe_simulation_resultados.json`

## **35.14 Structural decoding: code dictionary skeleton (notebook `41_structural_decoding.ipynb`)**

Given the two-tier separation, this section attempts a **structural (non-linguistic) decoding** — identifying the functional roles of Tier-1 elements without assuming a target language.

**Design:** Tier-1 glyphs are classified by their distributional behaviour into three functional categories:

- **Markers** (20 elements): high-frequency, position-fixed glyphs that appear at syllable boundaries. These likely function as structural delimiters or category indicators.
- **Section headers** (83 elements): glyphs that occur predominantly in initial positions of text blocks. Their distribution correlates with manuscript section boundaries.
- **Modifiers** (21 elements): low-frequency glyphs that attach to Tier-2 content sequences, possibly indicating variations or qualifiers.

**Total structural inventory:** 125 elements (20 + 83 + 21), with one element unclassified.

**Entry grammar:** Analysis of Tier-1/Tier-2 alternation patterns reveals a regular structure: entries consist of alternating T1-T2 sequences, with mean run lengths of 2.1 words (T1) and 2.2 words (T2). This alternation is significantly more regular than expected from a natural language (permutation test p < 0.001).

Notebook: `41_structural_decoding.ipynb`
Results: `structural_decoding_resultados.json`

## **35.15 TP threshold robustness (notebook `42_tp_threshold_robustness.ipynb`)**

The two-tier separation depends on the transition probability threshold used to classify glyphs. This section tests whether the key findings are robust across different threshold choices.

**Design:** The TP threshold is swept across 8 values from P5 (5th percentile) to P40 (40th percentile). At each threshold, the utilisation rate, onset/coda ratio, and Tier-1/Tier-2 token balance are recomputed.

**Results:**

| Metric | Range across P5–P40 | Robust? |
|--------|---------------------|---------|
| Utilisation | 6–12% | Yes |
| Onset/coda ratio | >1 at 7/8 thresholds | Yes |
| Tier-1/Tier-2 split | 35–60% | Threshold-dependent |

The utilisation rate remains in the 6–12% range regardless of threshold — the extreme combinatorial restriction is a **robust structural property**, not an artefact of a particular threshold choice. The onset/coda asymmetry (ratio > 1) holds at 7 of 8 thresholds tested. Only the exact Tier-1/Tier-2 token balance varies with the threshold, which is expected by construction.

**Conclusion:** The two-tier encoding and its key signatures (low utilisation, onset asymmetry) are robust findings that do not depend on parameter choices.

Notebook: `42_tp_threshold_robustness.ipynb`
Results: `tp_robustness_resultados.json`

# **Chapter 36\. Final Balance: SilPart and the Limits of Decryption**

## **36.1 SilPart as a generative model vs. a decryption tool**

Throughout Chapters 23–35, 16 different decryption models were tested, many of them directly motivated by the predictions of the generative SilPart model (d=0.445, best fit from Chapter 4). It is necessary to distinguish between two roles of SilPart:

1. **Generative (descriptive) model.**SilPart describes how the Voynich text is statistically organized: words composed of syllables, each syllabic position (onset/nucleus/coda) with a closed pool of glyphs. This role**it remains intact**No decryption experiment contradicts the positional structure, and 73% of position-locked glyphs are repeatedly confirmed.

2. **Guide for decryption (prescriptive).**SilPart's predictions generate hypotheses about how the glyph→character/syllable mapping should work. This role has been**systematically refuted**: every decryption strategy that attempts to exploit the positional structure produces worse results than the unique neural v2 table.

## **36.2 Hypothesis Balance SilPart-derivatives**

The following table summarizes the twelve decryption hypotheses derived from SilPart and their results:

| Hypothesis | Model | Chapter | Scorecard | Status |
| :---- | :---- | :---- | :---- | :---- |
| Position → different mapping table by position | Syl-Heb (3 tablas) | 26 | 4+/2±/0− | n-gram 14% (vs 68%) |
| Position → homophonic variant of the same character | Positional homophone | 22 | 2+/2±/2− | w\_homo inert |
| Glyphs in complementary positions \= allographs | Allograph | 28 | 4+/0±/2− | **Discarded** |
| Glyph \= Hebrew syllable, with homophonous variants | Syl-Homophonic | 29 | 3+/1±/2− | **Discarded** |
| Wrong target record (Mishnah/Zohar) | Registers | 30 | 2+/2±/1− (better) | **Discarded** |
| Voynich syllable → Hebrew syllable | Syl-to-Syl | 31 | 2+/1±/2− | **Discarded** |
| Onset/coda \= NULL estructural, solo nucleus mapea | Nucleus-only | 32 | 4+/0±/1− | **Discarded**(inflated n-gram) |
| Partial NULL with parameterized threshold θ | Partial NULL | 33 | 4+/0±/1− | **Discarded**(inflated n-gram, 1 root) |
| EVA ( | S | / | A | \=1.26, resolvable range) |
| Morphological role indexed substitution (P/R/S) | Morphological | 35 | 4+/1±/1− | **Discarded**(n-gram 16%, 0 roots) |
| Sustitución morphológica aramea (Zohar) | Morph. Zohar | 35 | 3+/0±/3− | **Discarded**(n-gram 0%, 1 root) |
| Position affects selection, not meaning (single table) | Neural v2 | 25 | **4+/0±/1−** | **Best result** |

The pattern is clear:**The more one tries to exploit SilPart's positional structure for decryption, or change the target corpus, the worse the result.**The best model (neural v2) is precisely the one that ignores position and uses a single table against Torah.

## **36.3 The SilPart Paradox**

This constitutes a genuine paradox:

- SilPart is the best generative model → the positional structure is**real**  
- But exploiting that structure worsens the decryption → the positional structure is**irrelevant**for mapping

The most parsimonious resolution is the conclusion of Chapter 26:**The position affects the glyph selection, not its meaning.**An onset glyph and a coda glyph can map to the same Hebrew character, but the writing system selects which one to use based on position. Position is a property of the**graphic system**not from**cryptographic code**.

This is analogous to cursive Arabic script, where the same letter has different forms depending on its position in the word (initial, medial, final, isolated), but the phonetic value does not change. In the Voynich Manuscript, the positional pools would be graphic variants of the same underlying alphabet, not independent substitution tables.

## **36.4 Residual hypothesis space**

Within the framework of monoalphabetic substitution \+ Hebrew LM, the combinations derived from SilPart are essentially exhausted. The remaining hypotheses fall outside this framework.

| Hypothesis | Argument against |
| :---- | :---- |
| Polyalphabetic cipher (Vigenère) | Inter-folio stability r=0.9999 — incompatible with key rotation |
| Intra-word transposition | The onset→nucleus→coda structure would be inexplicable if the glyphs were disordered. |
| Null glyphs (onset/coda do not encode) | Chapters 32-33: nucleus-only and partial NULL (θ=0.7) produce inflated n-grams (short words); 1 root maximum |
| Another target language (non-Semitic) | NW Semitic → non-Semitic gap \>3.5 pts (Chapter 5); Hebrew/Aramaic indistinguishable (gap 0.27) |
| Alternative Hebrew register (Mishnaic/Zoharic) | Chapter 30: 3 records give equivalent results; cross-scoring shows that mappings are artifacts of the LM |
| Non-linguistic content (tables, lists) | Statistical fingerprint (Part III) confirms genuine linguistic structure |

None of these alternatives has sufficient empirical support to justify a new battery of experiments within the scope of this work.

## **36.5 Synthesis: what we know and what we don't know**

### **What we know (with high confidence)**

1. **The Voynich has a genuine linguistic structure.**The U-curve, positional MI, and inter-folio stability distinguish it from all controls (random, glossolalia, simple ciphers).

2. **The positional structure is real.**SilPart (d=0.445), 73% of position-locked glyphs, onset/nucleus/coda pools with their own distributions.

3. **If the text encodes a natural language, it is compatible with Biblical Hebrew/Aramaic.**Hebrew \#1 in all rankings, Aramaic indistinguishable (gap 0.27), gap to non-Semitic languages ​​\>3.5 pts.

4. **Single-table char-level mapping is the most parsimonious representation.**Neural v2 (68% n-gram) outperforms all positional, syllabic, allographic, and homophonic models.

5. **There is a structural limit of \~2--5 roots and \~68% n-gram.**16 independent models converge on these limits, which are properties of the solution space, not of the models.

6. **The limit is independent of the transcription.**Neural v2 on EVA (|Σ|/|A|=1.26, resolvable range) produces 0% n-gram and 0 roots: the barrier is the manuscript encoding, not the alphabet size ratio.

### **What we don't know**

1. **If the Voynich really encodes a natural language.**Linguistic fingerprinting is necessary but not sufficient: complex formal systems could produce similar patterns.

2. **What is the specific coding mechanism?**No model produces legible Hebrew text. The ceiling of 3–5 roots (out of 100 possible) suggests that either the mechanism is more complex than monoalphabetic substitution, or the underlying language is not Hebrew.

3. **What does positional structure mean?**SilPart describes it but does not explain it: Is it a graphic variation (like cursive Arabic)? Morphological (prefix/root/suffix)? Or an artifact of the generation mechanism?

## **36.6 Methodological conclusion**

The main result of Chapters 23-35 is not a successful decryption but a **methodological contribution**. A complete pipeline (fingerprint → generative model → Bayesian decryption → multi-test validation) was exhaustively applied to 19 model variants, including 3 distinct target registers, syllable-by-syllable mapping, selective filtering of structural glyphs, role-indexed substitution, Aramaic morphological substitution (Zohar), replication on an alternative transcript (EVA), and three cross-linguistic experiments (Tibbonid Hebrew, Judeo-Arabic, and Ge'ez). The Ge'ez experiment (Model 19) is particularly significant: with |Σ|/|A| ≈ 0.88 — the first test at near-1:1 ratio — it demonstrates that the structural ceiling is not an artefact of alphabet-size mismatch but a property of the Voynich text itself. The robust negative result — no model produces readable text, all converge on the same limits — is itself informative: it establishes a lower bound for the complexity of the Voynich encoding mechanism and formally rules out simple substitution hypotheses (char-level, syllable-by-syllable, allographic, homophonic, multi-register, nucleus-only, morphological, cross-linguistic, and cross-script-type) against five Semitic languages spanning three writing system types (abjad, transliterated abjad, abugida).

SilPart remains the best description of the manuscript's surface structure, but that structure does not translate into a viable path to decipherment within the substitution paradigm. The Voynich Manuscript, if it encodes a language, does so with a mechanism that transcends monoalphabetic substitution—or it encodes something other than a known natural language.

# **Part IX References**

- Hochreiter, S. y Schmidhuber, J. (1997). "Long Short-Term Memory." *Neural Computation*, 9(8), pp. 1735--1780.

- Hinton, G. E. (2012). "Improving neural networks by preventing co-adaptation of feature detectors." *arXiv preprint arXiv:1207.0580*\[Dropout as a regularization\]

- Knight, K., Nair, A. y Rathod, N. (2006). "Unsupervised Analysis for Decipherment Problems." *Proceedings of the COLING/ACL 2006*, pp. 499--506.

- Ravi, S. y Knight, K. (2011). "Deciphering Foreign Language." *Proceedings of the 49th Annual Meeting of the ACL*, pp. 12--21.

- Stolfi, J. (2005). "A Tentative Partial Transliteration of the Voynich Manuscript." Technical Manuscript. \[Positional Paradigms of Prefixes and Suffixes\]

Parts I-IX are available as separate documents.


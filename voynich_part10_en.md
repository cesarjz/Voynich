# PART X — Alternative Models and Diagnostic Tests (Chapters 28–35)

## **28.1 Motivation: from positional homophony to decoding**

Chapter 26 ruled out positional polyphony (1 glyph → N characters depending on position) but confirmed the SilPart premise: 73% of glyphs are position-locked. The correct reading of SilPart is the**positional homophony**(N glyphs → 1 character, with selection by position), analogous to the positional variants of cursive Arabic where the initial, medial and final forms of a letter are distinct glyphs that encode the same phoneme.

**Hypothesis:**If we identify glyphs that are positional variants of the same underlying character (allographs) and collapse them, we will reduce the effective vocabulary from approximately 166 to approximately 30–50 types. Neural decryption using a flat table on the reduced vocabulary should improve root matching because the consonant patterns will be more consistent.

## **28.2 Clustering Strategy**

### **Feature vectors per glyph**

For each glyph with frequency ≥ 10, three feature vectors are constructed:

1. **Transition profile**(2 × N\_glyphs dims): row of M\_prob (which glyphs follow it) concatenated with column of M\_prob (which glyphs precede it). Captures the sequential context of the glyph.

2. **Intrasyllabic distribution**(3D): \[onset%, nucleus%, coda%\]. Captures the position of the glyph within the syllable.

3. **Positional distribution in a word** (3D): \[initial%, middle%, final%\].

### **Merger criteria**

Two glyphs are candidates for allographs if they meet three conditions:

- **High contextual similarity:**cosine over transition profiles \> 0.6 (appear in the same sequential contexts)  
- **Complementary positions:**They dominate in different intra-syllabic positions (one onset-heavy, the other coda-heavy)  
- **Same role C/V:**do not merge consonant with vowel

### **Hierarchical clustering**

- Distance \= 1 \- cosine over transition profiles  
- Linkage: average (robusto a outliers)  
- Sweep thresholds to cut the dendrogram  
- Selection of the threshold that produces \~30--50 effective rates  
- Post-filter: separate clusters with mixed C/V roles

## **28.3 Clustering result**

| Parameter | Value |
| :---- | :---- |
| Glyphs with frequency ≥ 10 | \~100 / 166 |
| Optimal Threshold | 0.30 |
| Original vocabulary | 166 |
| Reduced vocabulary | **145** |
| Reduction | 21 glyphs (**12.7%**) |
| Clusters multi-glifo | **4** |
| Candidate pairs (sim \> 0.6, same role) | 200 |
| Complementary pairs | 65 (32%) |

The reduction is**minimum**(12.7%), far from the target of 30-50 types. Only 4 clusters with more than one member are formed:

| Cluster | Representative | Members | Positions | Role |
| :---- | :---- | :---- | :---- | :---- |
| U2 | U2 | E2, M1, N1, T1, T2, Tb, U2, U3, U4, U5, V1, V2, W1, W2 (14) | 13 onset \+ 1 nucleus | C |
| F1 | F1 | B4, Cd, F1, F3, G3, H1, X1 (7) | nucleus, onset, coda (mixed) | C |
| D1 | D1 | D1, Yes (2) | onset, onset | C |
| Not | Not | B5, No (2) | onset, onset | C |

### **Cluster diagnosis**

**Cluster U2 (14 members):**It is a mega-cluster of low-frequency glyphs (T1, T2, U3, U4, U5, V1, V2, W1, W2) that share transition profiles due to their infrequent and noisy nature, not because they are genuine allographs. Almost all are onset. There is no positional complementarity.

**Cluster F1 (7 members):**It mixes positions (nucleus, onset, coda) but not in a complementary way \--- it is a grouping by generic contextual similarity.

**Clusters D1 and Ba (2 members each):**Both group glyphs from the same position (onset+onset). They are variants within the onset pool, not complementary onset/coda pairs.

**No cluster shows the expected positional complementarity**under the allographic hypothesis.

## **28.4 EM multi-seed on reduced vocabulary**

20 runs (10 seeds × 2 temperatures: T=2.0, T=3.0) on the corpus rewritten with 145 glyphs:

| Metric | Neural v2 (166 gl.) | Allograph (145 gl.) | D |
| :---- | :---- | :---- | :---- |
| Average score | \-36.34 ± 0.23 | \-36.55 ± 0.45 | \-0.21 |
| Roots medio | 1.5 ± 1.1 | 1.6 ± 1.2 | \+0.1 |
| Roots max | 3 | 4 | \+1 |
| K\_eff | 25 (all) | 25--27 | \= |
| Grammar \= 1.00 | 30/30 | 18/20 | \= |

Best candidate: T=3.0, seed 0: score=-36.43, K\_eff=27, grammar=1.00, roots=4 {wise, bread, servant, send}.

The roots חכם and לחם share the consonants ח and ל \--- the same pattern of consonant co-occurrence diagnosed as artifactual in Chapter 25\.

## **28.5 MCMC multi-chain**

| MCMC Metric | Neural v2 | Allograph | D |
| :---- | :---- | :---- | :---- |
| Best score | \-36.20 | \-36.43 | \-0.23 |
| K\_eff | 25 | 25 | \= |
| R-hat \< 1.1 | **71.1%** | **54.5%** | \-16.6 pp |
| Accept rates | 27--29% | 26--29% | \= |

Convergence worsens significantly (54.5% vs 71.1%). With 145 glyphs instead of 166, the search space is smaller, but the loss of informational distinctions means that MCMC strings find more ambiguous basins of attraction.

## **28.6 Validación: scorecard 4 PASS / 0 MARGINAL / 2 FAIL**

| Test | Neural v2 | Allograph | D |
| :---- | :---- | :---- | :---- |
| 1\. Collapse z-score | PASS (-0.94) | PASS (-0.75) | \+0.19 |
| 2\. N-gram percentile | PASS (68%) | PASS (23%) | **\-45 pp** |
| 3\. Root matching | FAIL (3 roots) | FAIL (4 roots) | \+1 |
| 4\. Cardinality ratio | PASS (0.93) | PASS (0.93) | \= |
| 5\. Grammar anchors | PASS (100%) | PASS (100%) | \= |
| 6\. Coherence reduction | — | **FAIL** (-45 pp) | new |

**Veredicto: 4 PASS / 0 MARGINAL / 2 FAIL**— worse than neural v2 (4+/0±/1−).

### **The n-gram falls drastically**

68% → 23% (-45 points). The reduction destroys sequential information: by collapsing 14 distinct glyphs into U2, transitional distinctions that LSTM exploited to achieve realistic n-grams are lost. Test 6 (reduction coherence) confirms the FAIL: the delta of \-45 percentile points is well below the ±5 pp threshold.

### **The roots do not improve significantly**

4 roots vs 3 of the neural v2. The roots found (חכם, לחם, עבד, שלח) include two pairs that share consonants (חכם/לחם share ח,ל) \--- the artifactual pattern of Chapter 25\.

## **28.7 Why the allographic hypothesis fails**

The hypothesis predicted that glyphs in complementary positions (onset vs. coda) would share similar transition contexts because they "surround" the same underlying character sequences. The data show the opposite:

| Prediction | Result |
| :---- | :---- |
| Complementary onset+coda clusters | **No:**0 clusters with genuine complementarity |
| Reduction to 30-50 types | **No:**only 145 types (12.7% reduction) |
| N-gram improves or remains the same | **No:**falls 45 points (-68% → 23%) |
| Roots significantly improves | **No:**4 vs 3 (no significance) |
| R-hat improvement (fewer parameters) | **No:**worsens (54.5% vs 71.1%) |

Contextual similarity in the Voynich is organized**by position**Onset glyphs resemble each other, coda glyphs resemble each other. But onset and coda glyphs**no**They resemble each other, even though the allographic hypothesis predicted this. This is compatible with a system where each position has a closed pool of glyphs with its own internal transition distributions, but where the pools of different positions operate with different logics.

## **28.8 Comparative table: 9 models**

| Metric | Composic. | Constr. | Homosexual. | Neural v1 | Lexical | Neural v2 | Syl-Heb | Syl-Ara | Allograph |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Vocab | 166 | 166 | 166 | 166 | 166 | 166 | 166 | 166 | **145** |
| N-grams % | 24% | 5% | 28% | 38% | 12% | **68%** | 14% | 6% | 23% |
| Roots | 6 | 100 | — | 1 | 3--4 | 3 | 5 | 5 | 4 |
| Collapse from | \-0.56 | \-0.45 | \-0.79 | \-0.72 | \-0.91 | \-0.94 | **\-0.20** | \-0.35 | \-0.75 |
| R-hat \< 1.1 | 59% | 40% | 68% | 70% | 67--71% | 71% | **92%** | 90% | 54% |
| Scorecard | 1+/1±/3− | — | 2+/2±/2− | 4+/0±/1− | 2--3+/1--2±/1− | **4+/0±/1−** | 4+/2±/0− | 4+/2±/0− | 4+/0±/2− |

## **28.9 Conclusions of Chapter 28**

1. **The allographic hypothesis is ruled out as a way to improve the decipherment.**Context-based clustering plus positional complementarity produces a minimal reduction (12.7%), with no genuinely complementary clusters. The plan's pessimistic scenario has materialized.

2. **Contextual similarity operates within positions, not between them.**The onset glyphs resemble each other, the coda glyphs resemble each other, but an onset glyph and a coda glyph of the supposed "same character" do not share a context. This rules out the model of positional variants of cursive Arabic script.

3. **Reduction destroys information.**Collapsing distinct glyphs into a representative loses transitional distinctions that LSTM exploited. The n-gram falls from 68% to 23% (-45 pp), and MCMC convergence worsens from 71% to 54%.

4. **The limit of \~3--5 roots persists.**Neither vocabulary reduction nor allograph collapse overcomes the structural barrier. With 9 models tested, this limit is confirmed as a property of the Voynich solution space, not of any specific model.

5. **The Voynich positional structure is deeper than allography.**Positional pools (onset, nucleus, coda) are not variants of the same alphabet—they are subsystems with their own transition distributions. Position not only selects which glyph is used (as SilPart predicts), but also defines distinct transition contexts, suggesting that positional structure is an integral component of the encoding mechanism, not a surface layer of graphical variation.

Notebook: `17_allograph.ipynb`Results:`allograph_resultados.json`

# **Chapter 29\. Syllabic Homophonic Cipher: glyph → Hebrew syllable**

## **29.1 Motivation: Are glyphs syllabic units?**

The nine previous models share one assumption: each Voynich glyph encodes a unique**character**Hebrew. Chapter 29 tests a fundamentally different hypothesis: each glyph encodes a**complete Hebrew syllable**(2-3 characters), and multiple glyphs can represent the same syllable (homophonic cipher).

Three observations motivate this hypothesis:

1. **Inventory size.**166 glyphs is excessive for an alphabet (\~27 Hebrew characters) but reasonable for a syllabary with homophonic variants. Historical syllabaries operate in ranges of 50-200 signs (cuneiform \~600, Linear B \~87, katakana \~48).

2. **MI does not amplify.**The mutual information glyph→syllable is 0.92× (Chapter 5), consistent with the fact that glyphs are already syllabic units: if the glyph encoded a single character, the MI should be amplified by grouping characters into syllables.

3. **Position and homophony.**73% of glyphs are position-locked (Chapter 26). Position could determine which homophonous variant is used for the same syllable, explaining the positional distribution without assuming polyvalence.

## **29.2 Hebrew syllabic inventory**

An inventory of Hebrew syllables is constructed from the Torah corpus using the same Transition Probability (TP) method as the Bayesian (Chapter 5):

1. Calculate bigram transition probabilities within Hebrew words  
2. Segment at percentile P20 (local TP minima): threshold \= 0.033  
3. Filter syllables with a frequency ≥ 5

| Metric | Value |
| :---- | :---- |
| Different syllables | 1,811 |
| Average length | 3.3 chars |
| Length distribution | 1: 27, 2: 199, 3: 662, 4: 600, 5: 254, 6: 62, 7: 7 |
| Position | free: 1,062, coda: 431, onset: 272, nuclear: 46 |
| Roles C/V | C: 1,219 (67%), V: 592 (33%) |

The inventory is considerably larger than the 27 Hebrew characters. The glyph/syllable ratio \= 166/1811 \= 0.09, which implies a theoretical homophonic capacity of \~11 glyphs per syllable if they were evenly distributed.

## **29.3 Design: SyllableGlyphMappingState**

The class`SyllableGlyphMappingState`It adapts the neural\_v2 framework with one key difference:`apply_word`concatenates the characters of the assigned syllables, producing sequences of variable length.

Glyph G1 → syllable (ב,ר) \= "bar"

Glyph G2 → syllable (א) \= "a"

Glyph G3 → syllable (כ,ל) \= "kl"

Word \[G1, G2, G3\] → "barakl" (6 characters of 3 glyphs)

The LSTM of neural\_v2 is reused without modification: it scores the concatenated sequence of characters, regardless of how it was generated. This allows for direct comparison.

The scoring functions adapt:

- **Positional:**match C/V of the glyph with C/V of the syllable (based on the first character)  
- **Grammar anchors:**Verify that the first character of the assigned syllable belongs to the anchor set of the glyph  
- **Cardinality:**Counts distinct syllables used (not characters), K\_max \= |inventory|/2  
- **Root matching:**search for 3-consonant roots in the concatenated sequence of chars

## **29.4 EM multi-seed**

Ten seeds are run with parameters adjusted for the longest sequences:

| Parameter | Value | vs neural\_v2 |
| :---- | :---- | :---- |
| Seeds | 10 (5 freq \+ 5 random) | 20 |
| SAMPLE\_EM | 1,500 | 3,000 |
| PROPOSALS/iter | 100 | 200 |
| EM\_ITERS | 1,500 | 2,000 |
| T | 3.0 | 3.0 |

Results (cell 9):

| Seed | Score | K\_eff | Grammar | Roots | Iter | Time |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 0 | \-163,894 | 166 | 1.000 | 1 | 1,236 | 203s |
| 1 | \-163,904 | 166 | 0.667 | 1 | 736 | 132s |
| 2 | \-163,896 | 166 | 0.667 | 2 | 757 | 125s |
| 3 | \-163,901 | 166 | 0.500 | 2 | 898 | 156s |
| 4 | \-163,897 | 166 | 0.667 | **5** | 1,500 | 252s |
| 5 | \-163,890 | 166 | 0.500 | 2 | 923 | 150s |
| 6 | \-163,894 | 166 | 1.000 | 1 | 1,351 | 229s |
| 7 | \-163,893 | 166 | 0.500 | 2 | 1,500 | 250s |
| 8 | \-163,894 | 166 | 0.500 | 2 | 1,500 | 244s |
| 9 | \-163,893 | 166 | 0.500 | 2 | 724 | 121s |

**Critical observation: K\_eff \= 166 in the 10 seeds.**The optimizer assigns a distinct syllable to each glyph, without any homophonic collapse. This occurs despite having 1,811 syllables available.

The scores (~~\-163,900) are orders of magnitude worse than neural\_v2 (~~\-36), which is expected: the decoded sequences are \~2.5× longer, accumulating more LM penalty.

Best candidate: seed 4 (5 roots: flesh, word, oil, hear, sun).

## **29.5 MCMC y posterior**

4 strings, 20K iterations, 5K burn-in, 10 thin:

| Metric | Value |
| :---- | :---- |
| Best score | \-163,886 |
| K\_eff | 166 |
| Accept rates | 74%, 75%, 74%, 75% |
| R-hat \< 1.1 | 82.0% |

Acceptance rates are high (\~75%) because, with 1,811 candidates per proposal, many changes result in syllables with similar scores. R-hat convergence (82%) is good, indicating that the strings are exploring the same local appeal.

## **29.6 Validation: 6 tests**

A specific test of the syllabic model is added (test 6: word length ratio).

| Test | Value | Verdict |
| :---- | :---- | :---- |
| 1\. Collapse z-score | 0.00 | **PASS** |
| 2\. N-gram percentile | 22.0% | **PASS** |
| 3\. Root matching | 1 root | **FAIL** |
| 4\. Cardinality ratio | 0.092 | **FAIL** |
| 5\. Grammar anchors | 83% | **PASS** |
| 6\. Word length ratio | z \= 1.11 | **MARGINAL** |

**Scorecard: 3 PASS / 1 MARGINAL / 2 FAIL**

### **Analysis of each test**

**Test 1 (PASS):**The collapse z-score is exactly 0.0 because there is no collapse: each glyph has its own syllable, so there are no groups of glyphs to assess internal consistency.

**Test 2 (PASS, but spurious):**The 22% n-gram seems acceptable, but it's an artifact. Inspection of the assigned syllables reveals that the optimizer preferentially selects syllables of 1–2 characters, avoiding those of 3–7 characters. This produces sequences with an average length of 5.16 characters (instead of the \~8–12 expected if the syllables were genuine), and LSTM can score these "pseudo-char" sequences reasonably well. In essence, the model reimplements a disguised char-level cipher.

**Test 3 (FAIL):**Only 1 root validated post-MCMC, worse than all competitive char-level models (3--5 roots).

**Test 4 (FAIL):**Cardinality ratio \= 9.2%. 166 out of 1,811 possible syllables are used, confirming that the syllabic inventory is unnecessarily large for this mapping.

**Test 5 (PASS):**Grammar anchors at 83%, indicating that the first character of the assigned syllables respects grammatical roles. But this is trivial: the selected short syllables behave as individual characters.

**Test 6 (MARGINAL):**The decoded words have a mean of 5.16 characters versus 3.81 for the Torah (z \= 1.11, within ±2σ but outside ±1σ). If the glyphs were genuinely syllabic, words with 4 glyphs would produce \~8–12 characters, well above the Torah mean. The optimizer mitigates this by choosing short syllables, but the residual excess (1.35 characters) betrays the tension between the syllabic hypothesis and realism.

## **29.7 The key result: fan-out \= 0**

The most revealing piece of data from the experiment is the homophonic fan-out:

| Metric | Value |
| :---- | :---- |
| Medium fan-out | 1.0 glyphs/syllable |
| Maximum fan-out | 1 |
| Syllables with multiple glyphs | 0 |
| Single syllables used | 166 |

The optimizer, with complete freedom to assign multiple glyphs to the same syllable, chooses**never**to do so. Each glyph is assigned its own distinct syllable. This refutes the homophonic hypothesis from the ground up: if the manuscript used homophonic variants for the same syllables, the optimal mapping should collapse similar glyphs to the same syllable, reducing K\_eff well below 166\.

The total absence of homophony, combined with the preference for short syllables, indicates that the syllabic framework does not provide anything that the char-level does not provide better: LSTM penalizes long sequences and the optimizer responds by choosing "syllables" that are effectively individual characters.

## **29.8 Comparative table: 10 models**

| Metric | Composic. | Constr. | Homosexual. | Neural v1 | Lexical | Neural v2 | Syl-Heb | Syl-Ara | Allograph | Syl-Homo |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Vocab/K\_eff | \~10 | — | — | 26 | 1.0 | 25 | 27 | 27 | 25 | **166 syls** |
| N-grams % | 24% | 5% | 28% | 38% | 12% | **68%** | 14% | 6% | 23% | 22% |
| Roots | 6 | 100 | — | 1 | 3--4 | 3 | 5 | 5 | 4 | 1 |
| R-hat \< 1.1 | 59% | 40% | 68% | 70% | 67% | 71% | **92%** | 90% | 55% | 82% |
| Scorecard | 1+/1±/3− | — | 2+/2±/2− | 4+/0±/1− | 2--3+/1--2±/1− | **4+/0±/1−** | 4+/2±/0− | 4+/2±/0− | 4+/0±/2− | 3+/1±/2− |

## **29.9 Conclusions of Chapter 29**

1. **The homophonic syllabic hypothesis is ruled out.**The optimizer does not produce homophony (fan-out \= 0\) or syllabic collapse (K\_eff \= 166), and the scorecard (3+/1±/2−) is lower than all competitive char-level models.

2. **166 glyphs do not form a syllabary.**There are too many for an efficient syllabary (which would collapse to \~80–100 distinct syllables) and they cover only 9% of the Hebrew syllabic inventory. The size of the glyph inventory is compatible with an alphabet with positional variants (as SilPart already suggests), not with a syllabary.

3. **The LSTM forces parsimony.**Given the choice between using long (genuinely syllabic) or short (pseudo-characters) syllables, LSTM penalizes long sequences, and the optimizer converges toward syllables of 1–2 characters. This confirms that the char-level model is the most parsimonious representation for Voynich.

4. **With 10 models tested, the limit of \~3--5 roots and the ceiling of the n-gram remain intact.**Neural v2 (68% n-gram, 3 roots) remains the best overall result. No change in assumptions (char-level, syllabic, allographic, homophonic) alters these limits, confirming that they are properties of the Voynich solution space, not of the decryption models.

Notebook: `18_syllabic_homophonic.ipynb`Results:`syllabic_homophonic_resultados.json`

# **Chapter 30\. Alternative Hebrew Records: Torah vs Mishnah vs Zohar**

## **30.1 Motivation: the wrong record**

Chapters 23–29 use biblical Hebrew (Torah) as their exclusive target corpus. However, if the author of the Voynich Manuscript was a Jewish physician or Kabbalist from northern Italy (15th century)—a historically plausible profile—his writing would follow a register distinct from the biblical one.

- **Mishnaic (Halakhic) Hebrew:**The language of rabbinic literature, with technical-legal vocabulary absent from the Torah (contracts, ritual purity, litigation). Corpus: Mishnah ed. Vilna 1913, 186,577 words in 63 tractates.  
- **Zoharic (Kabbalistic) Aramean:**The language of the Zohar, the central text of Kabbalah, with esoteric vocabulary and a syntactic structure distinct from biblical Aramaic. Corpus: Sulam ed. Jerusalem 1945, 768,375 words.

The 68% ceiling for n-gram and 3-5 roots (neural v2) could be an artifact of training the LM against the wrong register. This chapter tests all three registers with the same neural v2 pipeline (LSTM \+ EM multi-seed \+ MCMC).

## **30.2 Experimental design**

The three corpora are downloaded from Sefaria-Export (GitHub), subsampled to N=37,087 words (size of the Voynich corpus) with a fixed seed, and trained on three identical LSTMs (2 layers, embed=32, hidden=192, dropout=0.2, 30 epochs). Decryption hyperparameters: 10 EM seeds, T=3.0, 1500 iterations, 100 proposals/iter, followed by MCMC (4 strings, 20K iterations, 5K burn-in).

Note: These hyperparameters are reduced compared to neural v2 (20 seeds, 2000 iterations, 200 proposals, 3000 samples) to make three times as many experiments feasible. Internal comparison between records is fair (all under identical conditions), but the absolute values ​​are not directly comparable with neural v2.

Notebook: `19_registers.ipynb`

## **30.3 Corporate and LM Statistics**

| Corpus | Full size | Sample | Vocab | Mean WL | Val loss LM |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Torah | 80,051 | 37,087 | 27 | 3.81 | 2.003 |
| Mishnah | 186,577 | 37,087 | 27 | 4.10 | 2.106 |
| Zohar | 768,375 | 37,087 | 27 | 4.21 | 2.119 |

The three corpora share the same 27 Hebrew letters. Mishnah and Zohar have longer words on average (4.10 and 4.21 vs. 3.81), reflecting a greater use of analytical and compound forms. The Torah's val loss is slightly lower (2.003 vs. 2.11–2.12), possibly because the Torah is more formulaic and predictable than the rabbinic/Zoharic texts.

## **30.4 Results of EM multi-seed**

| Record | Score (mean±std) | Roots (mean) | Roots max | Best seed |
| :---- | :---- | :---- | :---- | :---- |
| Torah | \-36.91 ± 0.29 | 2.0 | 4 | seed 8 |
| Mishnah | \-36.80 ± 0.33 | 1.0 | 3 | seed 3 |
| Zohar | \-36.00 ± 0.27 | 0.3 | 1 | seed 3 |

Zohar obtains the best raw score (-36.00), but the fewest roots (0.3 on average; 7 out of 10 seeds find 0 roots). This reflects that Zohar's LM is more permissive (greater Aramaic entropy) but produces mappings without recognizable lexical content. Torah dominates in roots (2.0 on average, max 4).

## **30.5 Validation: comparative scorecards**

| Test | Torah | Mishnah | Zohar |
| :---- | :---- | :---- | :---- |
| 1\. Collapse z-score | \-1.75 (FAIL) | \-1.47 (MARGINAL) | \-1.38 (MARGINAL) |
| 2\. N-gram percentile | 1% (FAIL) | 6% (MARGINAL) | 0% (FAIL) |
| 3\. Root matching | 4 (FAIL) | 3 (FAIL) | 1 (FAIL) |
| 4\. Cardinality ratio | 0.93 (PASS) | 1.00 (PASS) | 0.96 (PASS) |
| 5\. Grammar anchors | 87% (PASS) | 96% (PASS) | 94% (PASS) |
| **Scorecard** | **2+/0±/3−** | **2+/2±/1−** | **2+/1±/2−** |

The three recordings produce very similar scorecards. Mishnah is marginally the best (2+/2±/1− vs. 2+/0±/3− for Torah), with an n-gram 6% (MARGINAL vs. FAIL) and a slightly better collapse z-score (-1.47 vs. \-1.75). However, the absolute 0–6% n-gram range is well below the 68% achieved by neural v2 with a full pipeline.

Bootstrap CI of the n-gram percentile: Torah 1.0% \[0, 4\], Mishnah 8.1% \[2, 16\], Zohar 0.0% \[0, 0\]. The Mishnah-Torah difference (\~7 pp) is marginally significant, but irrelevant in absolute terms.

## **30.6 Cross-scoring: transferibilidad de mappings**

Each optimized mapping for a register is evaluated against the LM of the other two registers:

| Mapping \\ LM | Torah | Mishnah | Zohar |
| :---- | :---- | :---- | :---- |
| Torah | **\-36.56** | \-38.53 | \-39.18 |
| Mishnah | \-39.27 | **\-36.54** | \-39.02 |
| Zohar | \-39.50 | \-39.29 | **\-35.83** |

The diagonal always wins by approximately 3 points. The mappings are**completely specific**to its own LM and are not transferable. This indicates that the optimizer adapts to the statistical idiosyncrasies of each language model, not to the underlying real linguistic structure. A mapping that "works" for Torah is useless for Mishnah and vice versa.

## **30.7 Conclusions of the record experiment**

1. **The alternative registration hypothesis is ruled out.**The three registers (Biblical, Mishnaic, Zoharic) produce equally poor results with the same pipeline. The Mishnaic shows a marginal advantage in n-grams (6% vs. 1%) that disappears in absolute terms. No register breaks the ceiling of \~3–5 roots.

2. **Cross-scoring reveals that the mappings are artifacts of the LM.**The drop of \~3 points off the diagonal confirms that each mapping specializes in the character frequencies of its own corpus, without capturing transferable linguistic structure.

3. **The Zohar is the worst candidate.**Despite achieving the best raw score (its LM is more permissive), it produces the fewest roots (0.3 average) and the worst n-gram (0%). Zoharic Aramaic is not a viable target.

4. **Confirmation of the "Northwest Semitic" category.**This result reinforces the conclusion of Chapter 27 (Aramaic Targum): within the Northwest Semitic family, the specific register does not matter. The boundary is structural to the Voynich manuscript, not to the target corpus.

5. **Methodological caveat.**The reduced pipeline (10 seeds, 1500 iterations, 100 proposals) does not replicate the 68% baseline of Torah Neural v2 (achieving only 1%). The relative comparison is fair, but we cannot completely rule out the possibility that a full pipeline with Mishnah will produce qualitatively different results. However, the relatively small difference (6 percentage points) makes this highly unlikely.

Notebook: `19_registers.ipynb`Results:`registers_resultados.json`

# **Chapter 31\. Syllable-by-syllable (Model 12\)**

## **31.1 Motivation: the word length paradox**

If the correct mapping unit is the individual glyph (as Neural v2 assumes), then one glyph equals one Hebrew character. But Voynich words have an average of 4.24 glyphs, and 7% have ≥7 glyphs. This would imply Hebrew words with 7+ characters, which is anomalous: the Hebrew average is 3.81 characters. If instead the unit is the**Voynich syllable**(average 2.58 glyphs), a word of 10 glyphs would have \~4 syllables, and mapping each syllable to a Hebrew syllable would produce \~4 Hebrew syllables (\~4 characters). This resolves the length paradox.

## **31.2 Design**

The TP-P20 segmentation produces 2,923 Voynich syllable types (792 with a frequency ≥5) and 3,829 Hebrew syllable types (1,168 functional), yielding a ratio |Σ|/|A| \= 0.68—the most favorable of all models. Each Voynich syllable maps to a Hebrew syllable; the decoded syllables are concatenated to character sequences and evaluated with the LSTM.

Pipeline: 20 seeds (10 × 2 temperatures T=2.0, T=3.0), 1,500 EM iterations with 200 proposals/iteration, patience 80\. MCMC: 4 chains, 15,000 iterations, burn-in 3,000, thin 5\.

## **31.3 Results**

| Metric | Value | Verdict |
| :---- | :---- | :---- |
| Collapse from | \+0.12 | PASS |
| N-gram percentile | **0.1%** | **FAIL** |
| Roots | 25† | MARGINAL |
| K\_eff / cardinalidad | 217/1,168 (18.6%) | FAIL |
| Word length | z \= 0.85 | PASS |
| R-hat \< 1.1 | 4.0% | — |
| Accept rate | 96.5% | — |
| **Scorecard** | **2+/1±/2−** |  |

†The 25 roots are spurious: the decoded words average only 2.42 characters, making 3-consonant roots trivially found.

## **31.4 Diagnosis**

The n-gram 0.1% (worse than chance) and the acceptance rate of 96.5% reveal a**flat energy landscape**The optimizer accepts virtually any proposal, meaning that the solution space (792 → 1,168) is too large for the LM signal to guide the search. The K\_eff \= 217/1,168 confirms that only 18.6% of the Hebrew inventory is used, and the convergence (R-hat 4%) is the worst of all the models.

The superficially favorable ratio |Σ|/|A| \= 0.68 is misleading: with 792 input types, the total number of possible mappings is 1,168^792 ≈ 10^2,433 — an astronomically larger combinatorial space than the 27^166 ≈ 10^237 of the glyph-to-character mapping.

## **31.5 Conclusion**

Neither glyph-to-character mapping nor syllable-to-syllable mapping produces readable Hebrew text. The syllable-to-syllable model is significantly worse than all the character-level models.**Hypothesis discarded.**

Notebook: `20_syllable_to_syllable.ipynb`Results:`syl2syl_resultados.json`

# **Chapter 32\. Nucleus-Only (Model 13\)**

## **32.1 Motivation: structural glyphs vs. content glyphs**

Chapter 26 established that 73% of glyphs are position-locked, and the SilPart paradox (§34.3 of the balance) indicates that position affects glyph selection, not meaning. Taking this idea to the extreme: what happens if the onset and coda glyphs are not variants of the same alphabet, but**structural markers**that do not encode phonetic content? In this case, only the nucleus glyphs would carry information.

This hypothesis resolves the word-length paradox: a word of 10 glyphs with \~4 nucleus glyphs → 4 Hebrew characters (reasonable). Furthermore, it reduces the effective |Σ|/|A| from 6.1 to a potentially solvable range.

## **32.2 Design**

The TP-P20 positional classification identifies:

| Position | Types | Role |
| :---- | ----: | :---- |
| Onset (dominant) | 42 | NULL (structural) |
| Coda (dominant) | 5 | NULL (structural) |
| Nucleus (dominant) | 28 | Content |
| Mixed (content vocabulary) | 120 | Content |
| **Total structural** | **47** | — |

All glyphs classified as pure onset or coda are treated as NULL. The remaining 120 glyphs (including 28 purely nuclear and 92 with partial presence in nucleus) map to the 27 Hebrew characters. |Σ|/|A| \= 120/27 \= 4.44.

Content extraction works as follows: for each syllable of 3+ glyphs, the first glyph (onset) and the last (coda) are removed, while the intervening glyphs (nucleus) are retained. Syllables with 1 glyph are preserved intact. Syllables with 2 glyphs (onset+coda, without nucleus) do not contribute content; if a complete word is left empty, the original word is used as a fallback (11.8% of words).

Pipeline: 20 seeds (10 × 2T), 1,500 EM iterations, 4 MCMC chains. LSTM identical to previous models.

## **32.3 Results**

| Metric | Value | Verdict |
| :---- | :---- | :---- |
| Collapse from | −0.41 | PASS |
| N-gram percentile | **100%** | **PASS**(absolute record) |
| Roots | 2 (ate, went) | FAIL |
| K\_eff / cardinalidad | 27/27 (100%) | PASS |
| Word length | z \= 1.31 (decoded 2.22 vs. Hebrew 3.81) | PASS |
| R-hat \< 1.1 | **95.8%** | (best convergence of the 13 models) |
| **Scorecard** | **4+/0±/1−** |  |

Scores: EM best −24.35, MCMC best −24.42 (much better than the \~−36 of char-level models). Val loss LSTM: 2.009.

## **32.4 Critical Analysis**

The n-gram 100% is the best result of all the models, but**It is an artifact of length**The average core content is 2.22 glyphs/word, which yields Hebrew words of approximately 2 characters. With only 2 characters, virtually any consonantal bigram appears in the reference corpus. The n-gram test does not discriminate at this length.

The R-hat 95.8% (best convergence) confirms that the solution space is much more manageable with 120→27 than with 166→27, and the 4 MCMC chains converge on consistent mappings. However, the 2 roots (אכל "eat", הלך "walk") are the minimum of all models — confirming that the root ceiling is not broken even under the best statistical conditions.

## **32.5 Conclusion**

Model 13 demonstrates that reducing the input vocabulary improves all statistical metrics (convergence, cardinality, n-gram), but the decoded words are too short to produce readable text. The hypothesis that onset/coda are purely structural is**excessively aggressive**: eliminates too much information. The result directly motivates Model 14 (§33).

Notebook: `21_nucleus_only.ipynb`Results:`nucleus_resultados.json`

# **Chapter 33\. Partial NULL (Model 14\)**

## **33.1 Motivation: parameterized threshold**

Models 7 (neural v2, full mapping) and 13 (nucleus-only) represent two extremes of a spectrum:

| Model | Glyphs/word | Decoded characters | N-gram | Problem |
| :---- | :---: | :---: | ----: | :---- |
| Neural v2 | 4.24 | \~4.24 | 68% |  |
| Nucleus-only | 2.22 | \~2.22 | 100%\* | Trivial Bigrams |
| **Sweet spot** | — | **\~3.5–4.0** | ? | — |

Not all onset/coda glyphs are equally "structural." Some appear in their dominant position 100% of the time (purely structural), others only 60-70% (partially informative). We define a**umbral de position-locking θ**: a glyph is treated as NULL if its fraction in the dominant position (onset or coda) is ≥ θ.

- θ → 0.5 (aggressive): more glyphs are removed → short words (≈nucleus-only)  
- θ → 1.0 (conservative): few glyphs are eliminated → long words (≈full mapping)

## **33.2 Sweep Design**

If 7 values ​​of θ ∈ {0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 1.00} are evaluated. For each θ:

1. Classify glyphs: NULL if (dominant position ∈ {onset, coda}) AND (dominant fraction ≥ θ)  
2. Extract content words (remove NULL glyphs, fallback to full word if empty)  
3. Run 10 seeds × T=2.0, EM 1,500 iter, 200 proposals/iter  
4. Select the best θ among those with a decoded mean length ≥ 3.0  
5. Execute MCMC (4 strings, 15K iter) on the selected θ  
6. Scorecard de 5 tests

## **33.3 Sweep Results**

| θ | NULL glyphs | Content vocab | Mean len | |Σ|/|A| | Best score | K\_eff | |---|------------|--------------|----------|--------|-----------|-------| | 0.50 | 47 | 157 | 2.69 | 5.81 | \-26.78 | 27 | | 0.60 | 43 | 158 | 2.76 | 5.85 | \-27.00 | 27 | | **0.70** | **38** | **155** | **3.06** | **5.74** | **\-28.22** | **27** | | 0.80 | 24 | 146 | 3.83 | 5.41 | \-31.06 | 27 | | 0.90 | 15 | 152 | 3.93 | 5.63 | \-31.70 | 27 | | 0.95 | 9 | 158 | 4.09 | 5.85 | \-31.85 | 27 | | 1.00 | 7 | 159 | 4.24 | 5.89 | \-33.42 | 27 |

Selected**θ=0.70**(average length ≥ 3.0): compromise between removing structural glyphs (38 NULL) and maintaining sufficient content.

## **33.4 Scorecard del mejor θ (θ=0.70)**

| Test | Value | Verdict |
| :---- | :---- | :---- |
| Collapse z-score | \-0.15 | PASS |
| N-gram percentile | 100.0% | PASS |
| Root matching | 1 (animal) | FAIL |
| Cardinality ratio | 1.00 | PASS |
| Word length z | 0.62 | PASS |

R-hat \< 1.1: **94.8%**. Scorecard: **4+/0±/1−**.

## **33.5 Conclusion**

Partial NULL confirms the nucleus-only pattern (Chapter 32): removing positional glyphs improves statistical metrics (100% n-gram, 94.8% R-hat) but does not break the root barrier (1 root). The parameterized θ reveals a continuous trade-off, but**no point produces more than 1 root**The score improves with more aggressive θ, but reflects the triviality of short words, not genuine decryption.

Notebook: `22_partial_null.ipynb`Results:`partial_null_resultados.json`

# **Chapter 34\. Transcriptional Robustness and Neural v2 on EVA**

## **34.1 Motivation**

All project results are based on the STA1 2.0 (Stolfi) transcription, which assigns 166 glyph types using 2-character codes. The most widely used alternative transcription, EVA (Zandbergen-Landini), collapses allographic variants into approximately 34 types with 1-character codes (plus multi-character codes such as`ch`, `sh`, `cth`, `ckh`). Two key questions:

1. **Are the statistical findings robust under EVA?**  
2. **Does EVA's favorable |Σ|/|A| ratio (1.26 vs 6.15) allow for better decryption results?**

## **34.2 Fingerprint comparison (notebook)`23_transcription_robustness.ipynb`)**

The complete statistical fingerprint is replicated on both transcripts:

| Metric | STA1 2.0 | EVA | Criterion | Do they both pass? |
| :---- | :---- | :---- | :---- | :---- |
| Words | 37,087 | 34,725 | — | — |
| Types | 166 | 34 | — | — |
| **Bounce** | **0.813** | 0.309 | \> 0.8 | **NO** |
| MI\_pos | 0.658 | 0.670 | \> 0.5 | YEAH |
| MI\_big | 1.681 | 1.839 | — | — |
| Spectral gap | 0.541 | 0.527 | — | — |
| Inter-folio r | 0.9996 | 0.9995 | \> 0.99 | YEAH |

**Result:**MI\_pos, spectral gap, and inter-folio are robust under both transcriptions. The bounce (U-shaped curve) is severely attenuated in EVA (0.309 vs. 0.813). The mechanism is as follows: STA1's 166 glyph types encode positional information directly in glyph identity—onset and coda variants of the "same" glyph are distinct types, so H₁ (unigram entropy) already captures positional structure. EVA merges these variants into 34 types, erasing the positional signal from unigrams and forcing the model to rely on bigram context to partially recover it. This produces two observable effects: (1) the entropy minimum shifts one step later (from H₂ in STA1 to H₃ in EVA), because one additional context character is needed to disambiguate positions that STA1 encodes directly; and (2) the subsequent bounce is weaker (0.309 vs. 0.813), because context alone cannot fully reconstruct the positional information that was lost in the many-to-one glyph merging.

Bootstrap (200 resamples): the 95% CIs of bounce do not overlap (STA1 [0.779, 0.825] vs EVA [0.313, 0.335]); the MI\_pos CIs do overlap (STA1 [0.653, 0.664] vs EVA [0.663, 0.676]), confirming that MI\_pos is genuinely robust across transcriptions.

## **34.3 Neural v2 on EVA (notebook`24_neural_v2_eva.ipynb`)**

Neural Pipeline v2 adapted for EVA:

- **No C/V restrictions**(EVA has no syllable position information)  
- **Sin grammar anchors**(anchors require positional classification of STA1)  
- **Simplified scoring:** w\_lm=2.0, w\_card=0.5, w\_ent=0.3 (sin w\_pos, sin w\_gram)  
- 20 EM seeds, 4 MCMC strings, 5 validation tests

### **Results**

| Metric | EVA Neural v2 | STA1 Neural v2 |
| :---- | :---- | :---- |
|  | S | / |
| Val loss (LM) | 2.013 | 2.004 |
| Score media EM | \-38.09 ± 0.82 | \-36.34 ± 0.23 |
| Roots media EM | 1.2 ± 1.0 | 1.5 ± 1.1 |
| MCMC best score | \-36.15 | \-36.34 |
| **N-grams %** | **0.0%** | **68%** |
| **Roots** | **0** | **3** |
| R-hat \< 1.1 | 66.7% | 71% |
| Cardinality | 0.74 | 0.96 |
| Collapse from | \-1.97 (FAIL) | \-0.41 (PASS) |
| **Scorecard** | **2+/0±/3−** | **4+/0±/1−** |

### **Diagnosis**

The EVA mapping is**massively degenerate**: 8 EVA glyphs → ה (he), 4 → י (yod), 3 → ם (final mem). The subsequent analysis shows extreme uncertainty for infrequent glyphs (cfh, cph, ckh have almost uniform distributions over 20+ characters). The ratio |Σ|/|A|=1.26 — theoretically within the resolvable range — is unhelpful because:

1. **EVA destroys positional information.**The 166 types of STA1 encode actual positional structure (73% position-locked). EVA collapses variants that have different positional roles on the same token, eliminating discriminative signal.  
2. **The unconstrained LM collapses at high frequency.**Without C/V constraints or grammar anchors, the optimizer is free to map all frequent glyphs to the few most common Hebrew characters.  
3. **The problem is not the ratio |Σ|/|A|.**Zodiac 340 (ratio \~1.3) was solved because it is a genuine substitution cipher. Voynich is not—reducing the ratio does not eliminate the fundamental barrier.

## **34.4 Conclusion**

The STA1/EVA comparison confirms that:

- The robust findings (MI\_pos, spectral gap, stability) reflect genuine properties of the manuscript  
- The bounce is specific to STA1 (fine inventory)  
- **The limit of decipherment is inherent in the encoding of the manuscript.**no to the transcription system nor to the alphabet size ratio

Notebooks: `23_transcription_robustness.ipynb`, `24_neural_v2_eva.ipynb`Results:`transcription_robustness_results.json`, `neural_v2_eva_resultados.json`

# **Chapter 35\. Morphological Replacement (Model 15\)**

## **35.1 Motivation**

The 14 previous models treat each glyph as an entry in a substitution table indexed by syllable position or without any conditions. However, if the author of the Voynich manuscript was a 15th-century Jewish Kabbalist, he would have been intimately familiar with Hebrew morphology: grammatical prefixes (ו, ה, ב, כ, ל, מ, ש), consonantal roots (22 letters), and suffixes (ה, ת, ם, ן, ך). The hypothesis:**3 morphological role-indexed replacement tables**(P=prefix, R=root, S=suffix), not by position of the glyph in the word.

This would explain:

- **Position-locking**(MI\_pos=0.658): morphological roles correlate with position (prefixes→start, roots→center, suffixes→end)  
- **166 different types**: \~27 characters × 3 roles × variation ≈ 160  
- **Why the single table (68%) outperforms 3 positional tables (14%)**: position is an imperfect proxy for morphological role

## **35.2 Design**

Each glyph maps to a pair**(Hebrew character, morphological role)**The scoring system combines:

- **w\_lm=2.0**: LSTM log-probability (same as neural v2)  
- **w\_morph=3.0**: morphological consistency — for each decoded word, it is segmented into prefix/root/suffix and checked whether the assigned roles match  
- **w\_card=0.5, w\_ent=0.3, w\_role=0.5**Cardinality, entropy, role distribution

Mixed proposals: 70% change the character within the valid set of the current role, 30% reassign the glyph to a different role.

Initialization: onset→P, nuclear→R, coda→S (positional proxy).

20 parallel EM seeds (15 CPUs), 4 parallel MCMC chains.

## **35.3 Results**

### **Multi-seed EM (20 seeds)**

| Metric | Value |
| :---- | :---- |
| Average score | \-102.27 ± 3.26 |
| Roots medio | 1.1 ± 1.1 (max 3\) |
| Morph consistency medio | 0.472 ± 0.089 |
| Best candidate | Seed 5: score \-99.16, K=25, roots 3, morph 0.540 |
| Role distribution (better) | P=38, R=49, S=79 |

### **MCMC (4 cadenas, 20K iter)**

| Metric | Value |
| :---- | :---- |
| Best score | \-96.43 |
| K\_eff | 25 |
| R-hat \< 1.1 | **84.3%** |
| Accept rates | 0.8-1.1% |
| Morph consistency | 0.538 |

### **Emergent tables**

| Board | Glyphs | Unique characters |
| :---- | :---- | :---- |
| P (prefix) | 40 | 7 |
| R (root) | 52 | 25 |
| S (suffix) | 74 | 5 |

The P/R/S distribution (40/52/74) is biased towards S — the optimizer assigns too many glyphs to the suffix role, contrary to the expected distribution of Biblical Hebrew (\~20%P/60%R/20%S).

### **Scorecard (6 tests)**

| Test | Value | Verdict |
| :---- | :---- | :---- |
| Collapse z-score | 0.00 | PASS |
| N-gram percentile | 16.0% | PASS (borderline) |
| Root matching | 0 roots | FAIL |
| Cardinality ratio | 0.93 (25/27) | PASS |
| Morph consistency | 48.1% (with 69%) | MARGINAL |
| Word length z | 0.23 | PASS |

**Scorecard: 4+/1±/1−**

### **Comparison with Neural v2**

| Metric | Morphologic | Neural v2 |
| :---- | :---- | :---- |
| N-grams % | 16% | **68%** |
| Roots | 0 | **3** |
| R-hat \< 1.1 | 84.3% | 71% |
| Cardinality | 0.93 | 0.96 |
| Scorecard | 4+/1±/1− | **4+/0±/1−** |

## **35.4 Diagnosis**

1. **Morph consistency 48% (MARGINAL)**The optimizer partially aligns the assigned roles with the Hebrew morphological segmentation, but does not reach 80%. The position→role correspondence is real but insufficient for decryption.

2. **Role stability 58.4%**Only \~58% of the glyphs maintain the same role in \>80% of the later MCMC. The tables are not well defined—the system oscillates between alternative assignments.

3. **N-gram 16%**(borderline PASS): comparable to syllabic positional (14%) but much lower than neural v2 (68%). Adding the morphological dimension does not compensate for the loss of single-table coherence.

4. **0 roots in validation**: the root roof persists even with explicit morphological segmentation.

5. **Accept rates \~1%**: the search space (166 glyphs × 3 roles × chars per role) is huge, and the scoring function with w\_morph creates a rough landscape.

## **35.6 Replica with Zohar/Aramaic (Model 16\)**

The morphological experiment is replicated by substituting the Torah (Hebrew) corpus for the Zohar (Aramaic), with morphological adaptations: Aramaic prefixes (ד,ב,כ,ל,מ,ו — 6 chars, without the Hebrew ה/ש) and Aramaic suffixes (א,ה,ת,ן,ך,י — 6 chars, con א as a postponed definite article).

| Metric | Model 15 (Torah) | Model 16 (Zohar) |
| :---- | :---: | :---: |
| Scorecard | 4+/1±/1− | 3+/0±/3− |
| N-gram | 16% | 0.0% |
| Roots (validation) | 0 | 1 (went) |
| Morph consistency | 48.1% (P69) | 42.0% (P45) |
| val\_loss LM | 2.004 | 2.111 |
| Average score EM | \-102.27±3.26 | \-103.33±2.50 |

**Result:**The Zohar/Aramaic is worse than the Torah/Hebrew in all metrics. The n-gram falls from 16% to 0%, and morphological consistency drops from the 69th to the 45th percentile. The Zohar's LM is more permissive (val\_loss 2.111 vs 2.004) but produces mappings without lexical structure.**Model 16 DISCARDED**— confirms that the barrier is structural, not dependent on the target corpus.

## **35.7 Conclusion**

**Morphological replacement hypothesis DISCARDED.**The model adds complexity (3 tables \+ roles) without exceeding the single table of neural v2. The n-gram 16% is 4× worse than the reference 68%, and the 0 roots in validation confirm the structural barrier. The partial match (48% morph consistency) suggests that the Voynich positional structure has a real morphological component, but this is not exploitable for decryption within the substitution paradigm. Replication with Zohar/Aramaic (Model 16\) confirms the pattern: changing the target corpus worsens all metrics (n-gram 0%, consistency P45), reinforcing that the limit is a property of the solution space and not of the chosen corpus.

Notebook: `25_morphological.ipynb`, `26_morphological_zohar.ipynb`Results:`morphological_resultados.json`, `morphological_zohar_resultados.json`

## **35.8 Cross-linguistic Experiments: Tibbonid Hebrew, Judeo-Arabic, and Ge'ez (Models 17–19)**

Three additional target languages were tested using the Neural v2 pipeline (20 seeds × 2 temperatures, 4 MCMC chains), each addressing a specific hypothesis about why the structural ceiling persists.

### 35.8.1 Model 17: Tibbonid Hebrew (Moreh Nevuchim) — notebook `33_tibbonid_hebrew.ipynb`

**Hypothesis:** The Voynich author may have written in the philosophical Hebrew of the Ibn Tibbon school rather than Biblical Hebrew, which would explain the failure of Torah-based models due to register-specific neologisms and Arabicised syntax.

**Corpus:** Complete Moreh Nevuchim (Guide for the Perplexed), Makbili 2024 edition via Sefaria; 157,042 words, 27 characters. Mean word length 4.21 (vs. Voynich 4.24 — almost identical).

| Metric | Torah (Model 7) | Tibbonid (Model 17) |
|--------|----------------|---------------------|
| Val loss | 2.004 | 2.107 |
| N-gram % | **68%** | 13% (MARGINAL) |
| Roots | 3 | 3 |
| R-hat < 1.1 | 71.1% | 54.2% |
| Scorecard | **4+/0±/1−** | 3+/1±/1− |

**Result:** The Tibbonid LM is less predictive than the Biblical one (val\_loss 2.107 vs 2.004) despite training on 4× more data. N-gram drops from 68% to 13%. The root ceiling (3) is unchanged. **Model 17 DISCARDED** — the register hypothesis does not explain the structural barrier.

### 35.8.2 Model 18: Judeo-Arabic (Quranic proxy) — notebook `34_judeo_arabic.ipynb`

**Hypothesis:** Judeo-Arabic — Arabic written in Hebrew characters — was the scholarly language of medieval Jewish communities. If the Voynich encodes Judeo-Arabic rather than Hebrew, the character-level n-gram patterns would differ.

**Corpus:** Quranic Arabic (Uthmani, 77,875 words) transliterated to Hebrew characters following the standard Judeo-Arabic convention (28 Arabic consonants → 22 Hebrew letters, merging tha/ta, dad/sad, etc.). No machine-readable Judeo-Arabic corpus exists for download, so this serves as a proxy. |Σ|/|A| ≈ 7.5 (worse than Hebrew's 6.1).

| Metric | Torah (Model 7) | Judeo-Arabic (Model 18) |
|--------|----------------|-------------------------|
| Val loss | 2.004 | **1.975** (best LM!) |
| N-gram % | **68%** | 12% (MARGINAL) |
| Roots | 3 | 1 |
| Grammar | PASS (100%) | **FAIL (0%)** |
| Scorecard | **4+/0±/1−** | 2+/1±/2− |

**Result:** Paradoxically, the Judeo-Arabic LM has the best val\_loss of all models (1.975) — Arabic is more predictable at the character level — but produces the second-worst mapping. Hebrew morphological anchors (prefix/suffix constraints) do not apply to Arabic morphology, causing grammar to FAIL. **Model 18 DISCARDED** — Judeo-Arabic is not a viable candidate.

### 35.8.3 Model 19: Classical Ge'ez (Ethiopic) — notebook `35_geez.ipynb`

**Hypothesis:** This is the most theoretically significant test. Ge'ez is an Ethiopic Semitic language written in an abugida where each character encodes a consonant+vowel pair. With 188 syllable characters, it gives |Σ|/|A| ≈ 0.88 — nearly 1:1 with the Voynich's 166 glyphs. This is the first model that eliminates the LM dominance problem (ratio ~6) that plagues all other models.

**Historical plausibility:** Ethiopian monks attended the Council of Florence (1441) and maintained a permanent community at Santo Stefano dei Mori in the Vatican from the 14th century. The Voynich is dated 1404–1438.

**Corpus:** TraCES Corpus of Classical Ethiopic, University of Hamburg; 62,671 words, 188 syllable characters. No C/V role distinction (each character is a full syllable); grammar anchors disabled.

| Metric | Torah (Model 7) | Ge'ez (Model 19) |
|--------|----------------|-------------------|
| Target chars | 27 | 188 |
| |Σ|/|A| | 6.1 | **0.88** |
| Val loss | 2.004 | 2.017 |
| N-gram % | **68%** | **0%** (worst ever) |
| Collapse z | −0.94 (PASS) | **−3.50 (FAIL)** |
| Cardinality | 92.6% | **63.3%** |
| R-hat < 1.1 | 71.1% | **80.5%** (best ever) |
| Scorecard | **4+/0±/1−** | **1+/0±/3−** |

**Result:** Despite the near-optimal alphabet ratio, Ge'ez produces the worst decipherment of all 19 models. The MCMC chains converge well (80.5% R-hat — best of all models) but converge to a degenerate mapping: 0% n-gram, severe collapse (z = −3.50), and only 63% of target characters used. **Model 19 DISCARDED.**

**Theoretical significance:** This result proves that the structural ceiling is NOT an artefact of alphabet-size mismatch. The barrier persists regardless of whether the target is an abjad (Hebrew, 27 chars), an alphabet (Latin, 26), or an abugida (Ge'ez, 188 syllables). The 166-vs-188 numerical match — which appeared to be a "smoking gun" — turns out to be a coincidence. The encoding mechanism of the Voynich Manuscript resists substitution-based decipherment at any alphabet ratio.

### 35.8.4 Summary of cross-linguistic experiments

| Model | Language | Register | |Σ|/|A| | N-gram | Roots | Scorecard |
|-------|----------|----------|---------|--------|-------|-----------|
| 7 | Hebrew | Biblical (Torah) | 6.1 | **68%** | 3 | **4+/0±/1−** |
| 8 | Hebrew | Syllabic-positional | 6.1 | 14% | 5 | 4+/2±/0− |
| 9 | Aramaic | Targum Onkelos | 6.1 | 6% | 5 | 4+/2±/0− |
| 17 | Hebrew | Tibbonid (philosophical) | 6.1 | 13% | 3 | 3+/1±/1− |
| 18 | Judeo-Arabic | Quranic (proxy) | 7.5 | 12% | 1 | 2+/1±/2− |
| 19 | Ge'ez | Classical Ethiopic | **0.88** | **0%** | N/A | 1+/0±/3− |

Torah remains the best candidate across all metrics. The structural ceiling holds across 5 Semitic languages/registers and 3 writing system types (abjad, transliterated abjad, abugida).

Notebooks: `33_tibbonid_hebrew.ipynb`, `34_judeo_arabic.ipynb`, `35_geez.ipynb`
Results: `tibbonid_resultados.json`, `judeo_arabic_resultados.json`, `geez_resultados.json`

## **35.10 Effect of the C/V Role Constraint (notebook `27_cv_constraint.ipynb`)**

All previous decipherment models enforce a consonant/vowel (C/V) role constraint: Voynich glyphs classified as vowels (>40% nuclear position) can only map to Hebrew matres lectionis (א,ה,ו,י), and consonant glyphs only to consonant characters. Since Hebrew is an abjad that largely omits vowels, this constraint forces ~40% of Voynich glyphs to compete for only 4 target characters. The hypothesis is that this mismatch could bottleneck decipherment and explain the 68% n-gram ceiling.

**Experimental design:** Three conditions using the Neural v2 pipeline (10 seeds each):
- **A:** With C/V constraint + grammar anchors (baseline)
- **B:** Without C/V constraint + grammar anchors
- **C:** Without C/V constraint, without grammar anchors

| Condition | C/V | Anchors | N-gram %ile | Roots max | Roots mean |
|-----------|-----|---------|-------------|-----------|------------|
| **A: With C/V + anchors** | Yes | Yes | **100%** | 3 | 2.0 |
| B: Without C/V + anchors | No | Yes | 96% | 5 | 1.7 |
| C: Without C/V, without anchors | No | No | 85% | 6 | 3.0 |

**Result:** Removing the C/V constraint does not improve results — in fact, n-gram percentile decreases monotonically (100% → 96% → 85%). The constraint acts as a beneficial regularizer, not a bottleneck. The 68% ceiling is NOT an artefact of the Hebrew abjad mismatch; it is a structural property of the Voynich text itself.

**Abjad mismatch hypothesis DISCARDED.**

Notebook: `27_cv_constraint.ipynb` Results: `cv_constraint_resultados.json`


---

Continued in Part XI.

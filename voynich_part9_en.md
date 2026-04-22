# PART IX — Neural and Syllabic Decipherment Models (Chapters 23–27)

# **PART IX**

# **Neural LM and lexical-radicular scoring**

Part VIII concluded with a convergent diagnosis from three models (compositional, constrained, homophonic): the dominance of the CharLM trigram with Witten-Bell smoothing is the fundamental problem. The LM collapses the mapping to a few high-frequency characters (especially \*shin\*), and no combination of additional constraints resolves the conflict between plausibility and linguistic validity. Part IX directly attacks this root cause by replacing the CharLM trigram with a Neural CharLM (LSTM) with controllable temperature (Chapter 23), and then assesses whether a lexical-radicular scoring component can add lexical specificity without destroying the diversity gained (Chapter 24).

# **Chapter 23\. Neural CharLM with Grammar and Cardinality**

## **23.1 Motivation: to overcome the dominance of the CharLM trigram**

The diagnosis of Parts V–VIII identifies the CharLM trigram as the root cause of the degenerate mapping. The problem has two facets:

1. **Collapse due to plausibility.**Witten-Bell smoothing assigns disproportionate probabilities to frequent Hebrew bigrams and trigrams, creating a gradient that pushes all glyphs towards shin (ש), the most frequent consonant in the Torah corpus.

2. **Fixed temperature.**The CharLM implicitly operates at T=1.0, without any mechanism to control the "hardness" of the probability distribution. There is no way to smooth the LM to allow for greater diversity.

A Neural CharLM (LSTM) solves both problems: it learns distributed representations that generalize better than counts \+ smoothing, and it supports adjustable temperature T that controls the trade-off between concentration (low T → peaky) and diversity (high T → flat).

## **23.2 Architecture and training**

A 2-layer LSTM is implemented as the character-level language model (cell 4 of the notebook).`12_neural_lm.ipynb`):

| Parameter | Value |
| :---- | :---- |
| Embedding | 32 dims |
| Hidden | 192 dims |
| Capas LSTM | 2 |
| Dropout | 0.2 |
| Total parameters | 476,991 |
| Context | Bigram (2 characters) |

The model is trained on the Hebrew corpus (Torah, subsampled to 37K words to match the Voynich) with split 80/20, AdamW, cosine annealing, early stopping with patience=5.

| Metric | Value |
| :---- | :---- |
| Trained eras | 30 |
| Better value loss | 2.004 |
| PPX baseline (trigrama) | 7.37 |
| PPX neural (T=1.0) | 7.48 |

The neural perplexity at T=1.0 is virtually identical to that of the trigram (7.48 vs 7.37), confirming that the LSTM learns a comparable distribution. The advantage of the neural system is not in absolute PPX but in the**controllability via temperature**.

The grammar anchors (12 glyphs with prefix/root/suffix roles anchored to subsets of the Hebrew alphabet) and the positional C/V classification of the previous parts are maintained.

## **23.3 Temperature Analysis**

The effect of T on the entropy and PPX of the LM (cell 6\) is evaluated:

| T | H media | PPX |
| :---- | :---- | :---- |
| 0.3 | 1.18 | 30.1 |
| 0.5 | 1.88 | 11.5 |
| 0.8 | 2.62 | 8.1 |
| 1.0 | 2.98 | 7.7 |
| 1.5 | 3.58 | 8.2 |
| 2.0 | 3.92 | 9.2 |
| 3.0 | 4.31 | 11.4 |
| 5.0 | 4.64 | 15.0 |

T controls a continuum between concentration (T=0.3, H=1.18) and uniformity (T=5, H=4.64). At T≥2, the entropy exceeds 3.9 bits, enough to support 27 active characters without collapse.

## **23.4 Composite scoring and sweep**

Neural scoring has 5 components (cell 7):

| Component | Weight | Function |
| :---- | :---- | :---- |
| S\_LM | w\_lm \= 2.0 | Low LSTM log-prob with temperature T |
| S\_pos | w\_pos \= 0.5 | Positional C/V compatibility |
| S\_card | w\_card \= 0.5 | Quadratic penalty if K \< K\_max |
| S\_ent | w\_ent \= 0.3 | Normalized entropy of the mapping |
| S\_gram | w\_gram \= 2.0 | Grammar anchors (12 glifos) |

Incremental scoring is implemented: when changing a glyph, only the words that contain it are re-evaluated (GPU batch), reducing the cost per proposal from O(N) to O(k) where k is the average number of words per glyph.

The sweep explores T × w\_gram × w\_card × K\_max (90 configurations, 200 short EM iterations, 500 words). The result is clear:**T=3.0, w\_gram=2.0, w\_card=0.5, K\_max=20**dominates the ranking. T=3 is the optimal point where entropy is sufficient for diversity (H=4.3) without completely destroying the n-grammatic structure.

## **23.5 EM complete and MCMC**

With the best sweep configuration, full EM is executed (3000 words, 2000 iterations, patience=100) followed by multi-chain MCMC:

**IN:**

| Config | Score | K\_eff | Grammar | Convergence |
| :---- | :---- | :---- | :---- | :---- |
| T=3, K\_max=20 | \-36.23 | 27 | 1.00 | iter 268 |
| T=3, K\_max=23 | \-36.23 | 27 | 1.00 | iter 261 |
| T=3, K\_max=27 | \-36.23 | 27 | 1.00 | iter 210 |
| Baseline trigrama | \-40.66 | 27 | 0.00 | iter 243 |

**Key result:**The neural network with T=3 achieves K\_eff=27/27 (all Hebrew characters active) and grammar=1.00 (12/12 anchors correct). The score (-36.23) far exceeds the baseline trigram (-40.66).

**MCMC (4 strings × 20K iterations):**

| Metric | Value |
| :---- | :---- |
| Best score | \-36.23 |
| K\_eff | 26 |
| R-hat \< 1.1 | **69.9%** |
| Accept rates | 29--32% |

The MCMC convergence (69.9%) is the best of all the models tested.

## **23.6 Validación: scorecard 4 PASS / 0 MARGINAL / 1 FAIL**

| Test | Value | Criterion | Result |
| :---- | :---- | :---- | :---- |
| 1\. Collapse z-score | \-0.72 | with \> \-1.0 | **PASS** |
| 2\. N-gram percentile | 38.0% | \>15% | **PASS** |
| 3\. Root matching | 1 root | \>10 roots | **FAIL** |
| 4\. Cardinality ratio | 0.96 (26/27) | \>0.6 | **PASS** |
| 5\. Grammar anchors | 100% (12/12) | \>60% | **PASS** |

**Veredicto: 4 PASS / 0 MARGINAL / 1 FAIL.**

The neural solves the problems of Parts V-VIII:

- **Collapse:**z=-0.72 (PASS), compared to the shin degeneracy of the previous models.  
- **N-grams:**38th percentile (PASS), the best of all models. T=3 preserves sufficient sequential structure.  
- **Cardinality:**26/27 active characters (PASS), compared to \~10 for the compositional.  
- **Grammar:**100% correct anchors (PASS).

He **sole FAIL**It is root matching: only 1 recognizable Hebrew root (vs 6 in compositional, 100 in constrained). T=3 breaks the degeneration of the LM but destroys lexical specificity: the mapping is diverse and grammatically correct but does not produce consonant trigrams that match biblical roots.

## **23.7 Comparison with previous models**

| Metric | Compositional | Constrained | Homophonic | Neural |
| :---- | :---- | :---- | :---- | :---- |
| Characters used | \~10 | — | — | **26** |
| N-grams % | 24% | 5% | 28% | **38%** |
| Roots matched | 6 | 100 | — | 1 |
| Collapse from | \-0.56 | \-0.45 | \-0.79 | **\-0.72** |
| R-hat \< 1.1 | 59% | 40% | 68% | **70%** |
| Scorecard | 1+/1±/3− | — | 2+/2±/2− | **4+/0±/1−** |

The neural language dominates in 4 out of 5 tests. The trade-off is clear: the diversity gained by T=3 comes at the cost of lost lexical roots.

Notebook: `12_neural_lm.ipynb`Results:`neural_results.json`

# **Chapter 24\. Lexical-root scoring (S\_root)**

## **24.1 Hypothesis: combining neural diversity with lexical specificity**

Chapter 23 states that the neural LM with T=3 achieves 4 PASS scores but fails at root matching (1 root). The constrained version (Part VII) achieves 100 roots but with 5% n-grams and degenerate mapping. The question is: can a 6th scoring component, S\_root, that rewards recognizable Hebrew roots, combine the diversity of the neural version with the lexical coherence of the constrained version?

**Hypothesis:**The combination of temperature T≥2 (diversity) \+ S\_root (lexical specificity) should maintain high cardinality, reasonable n-grams (\>15%) and significantly improve root matching.

## **24.2 S\_root Design**

Three key design decisions are implemented (cell 6 of the notebook)`13_lexical_scoring.ipynb`):

**1\. IDF-weighted distinct roots.**S\_root counts roots*distinct*(not total matches) weighted by inverse document frequency. Rare roots in the Hebrew corpus are valued higher, avoiding overfitting to common roots.

| Root | IDF (top-5, rare) | Root | IDF (bottom-5, comunes) |
| :---- | :---- | :---- | :---- |
| Read | 0.0139 | thing | 0.0062 |
| unclean | 0.0139 | water | 0.0064 |
| full | 0.0139 | was | 0.0066 |
| Carried | 0.0139 | Put | 0.0067 |
| stone | 0.0139 | day | 0.0068 |

**2\. Deterministic skeleton during optimization.**Only consonants are extracted (strip matres lectionis), without wildcards. This is stricter than validation (which uses confidences), to avoid the artificial inflation observed in the constrained method (100 roots, many due to wildcards in low-confidence skeletons).

**3\. Scoring incremental.**When a glyph is changed, only the roots of the words containing it are re-evaluated. Root matching is pure string operations, with no GPU overhead.

**Null distribution of S\_root:**

| Metric | Value |
| :---- | :---- |
| Mean (50 random mappings) | 0.011 |
| Std | 0.011 |
| Threshold significativo (mean \+ 2σ) | 0.034 |

## **24.3 Composite scoring: 6 components**

The neural scoring is extended with a 6th component (cell 7):

| Component | Fixed weight | Function |
| :---- | :---- | :---- |
| S\_LM | w\_lm \= 2.0 | LSTM con temperatura T |
| S\_pos | w\_pos \= 0.5 | C/V Compatibility |
| S\_card | w\_card \= 0.5 | Cardinality penalty |
| S\_ent | w\_ent \= 0.3 | Entropy of mapping |
| S\_gram | w\_gram \= 2.0 | Grammar anchors |
| **S\_root** | **w\_root ∈ {0..5}** | **IDF-weighted distinct roots** |

The 5 original weights are fixed to the optimal values ​​of Chapter 23\. Only w\_root × T are swept.

## **24.4 Sweep w\_root × T**

Grid: w\_root ∈ {0, 0.3, 0.5, 1, 2, 3, 5} × T ∈ {2, 3, 5} \= 21 configurations. Short EM: 200 iterations, patience=20, 500 words (cell 8):

| w\_root | T=2 | T=3 | T=5 |
| :---- | :---- | :---- | :---- |
| 0 | 4 | 4 | 2 |
| 0.3 | 5 | 5 | 5 |
| 0.5 | 5 | 5 | 4 |
| 1 | 6 | 5 | 4 |
| 2 | 8 | 5 | 6 |
| 3 | 8 | 5 | 6 |
| 5 | 9 | 8 | **11** |

*(Table: number of distinct roots found by short EM with deterministic skeleton)*

**S\_root generates a real monotonic effect.**At w\_root=0, the baseline finds 2-4 roots. At w\_root=5, 9-11 roots are found. The cardinality K\_eff=27 is maintained in all configurations. The JSDs are similar (\~0.76) in the short sweep.

## **24.5 EM complete: 5 to 15 roots**

A full EM is executed (3000 words, 2000 iterations, patience=100) with the top-3 sweep configurations plus the baseline w\_root=0 (cell 9):

| Config | Score | K\_eff | Grammar | Roots | Roots found |
| :---- | :---- | :---- | :---- | :---- | :---- |
| T=5, wr=5 | \-37.87 | 27 | 1.00 | **15** | Bless flesh man word blood path written bread king past bone womb tremble hear keep |
| T=2, wr=5 | \-36.48 | 27 | 1.00 | 13 | — |
| T=2, wr=2 | \-36.65 | 27 | 1.00 | 11 | Bless the word of blood, through a wise male, written past, bone, womb, trembling. |
| T=2, wr=0 | \-36.71 | 27 | 1.00 | 5 | — |

**S\_root triples the roots during EM:**from 5 (baseline) to 15 (T=5/wr=5) or 11 (T=2/wr=2). The 15 roots of the best config include semantically coherent roots: דבר (speak), שמע (listen), כתב (write), מלך (king), דרך (way), לחם (bread), בשר (meat).

## **24.6 MCMC and validation: two tested configurations**

Two configurations were tested in full MCMC (4 strings × 20K iter, burn-in=5000) to evaluate the effect of temperature:

### **Config 1: T=5, w\_root=5 (maximiza roots)**

| MCMC Metric | Value |
| :---- | :---- |
| Best score | \-37.82 |
| K\_eff | 25 |
| R-hat \< 1.1 | 70.6% |
| Accept rates | 29--30% |

| Test | Value | Result |
| :---- | :---- | :---- |
| 1\. Collapse z-score | \-0.91 | **PASS** |
| 2\. N-gram percentile | 12.0% | **MARGINAL** |
| 3\. Root matching | 4 roots | **FAIL** |
| 4\. Cardinality ratio | 0.93 | **PASS** |
| 5\. Grammar anchors | 100% | **PASS** |

**Scorecard: 3 PASS / 1 MARGINAL / 1 FAIL.** Validated roots: ברך (bless), דרך (way), מלך (king), עצם (bone/essence).

### **Config 2: T=2, w\_root=2 (preserves n-grams — hypotheses)**

| MCMC Metric | Value |
| :---- | :---- |
| Best score | \-36.65 |
| K\_eff | 27 |
| R-hat \< 1.1 | 67.3% |
| Accept rates | 30--33% |

| Test | Value | Result |
| :---- | :---- | :---- |
| 1\. Collapse z-score | \-1.07 | **MARGINAL** |
| 2\. N-gram percentile | 12.0% | **MARGINAL** |
| 3\. Root matching | 3 roots | **FAIL** |
| 4\. Cardinality ratio | 1.00 | **PASS** |
| 5\. Grammar anchors | 100% | **PASS** |

**Scorecard: 2 PASS / 2 MARGINAL / 1 FAIL.** Validated roots: ברך (bless), דבר (speak), דרך (way).

### **Comparison between the two configurations**

| Metric | T=5/wr=5 | T=2/wr=2 | Observation |
| :---- | :---- | :---- | :---- |
| N-grams % | 12% | 12% | Identical — T is not the factor |
| validated roots | 4 | 3 | Similar |
| Collapse from | \-0.91 | \-1.07 | T=2 worsens collapse |
| K\_eff | 25 | 27 | Both different |
| Scorecard | 3+/1±/1− | 2+/2±/1− | T=5 slightly better |

**Unexpected discovery:**lower T from 5 to 2**It does not recover n-grams**(12% in both cases). The hypothesis that "high T degrades n-grams" was incorrect: the degradation comes from S\_root itself, not from T. Furthermore, T=2 worsens the collapse (z=-1.07, 11 DEGENERATE groups) because without the high entropy of T=5, the LM pushes towards higher concentration.

The roots are partially unstable between configurations: only ברך and דרך appear in both. מלך and עצם disappear with T=2; דבר appears.

## **24.7 Test of statistical significance**

To determine whether the 3-4 validated roots are signal or noise, a null test is run: how many roots does a random mapping with K=25 find on the top 200 words?

| Statistical | Null (500 random mappings) | Lexical |
| :---- | :---- | :---- |
| Mean roots | 0.5 | — |
| Std | 0.8 | — |
| Max | 5 | — |
| Lexical T=5/wr=5 | — | **4 roots** |
| Percentile | — | **99.2%** |
| p-value | — | **0.008** |

The 4 roots of the lexical (T=5/wr=5) are in the 99.2% percentile of the null distribution (p=0.008).**The signal is statistically significant**A random mapping with the same cardinality would find 0-1 roots; finding 4 is improbable by chance.

For the EM (3000 words, K=27, top-500 words):

| Statistical | Null (200 mappings) | Lexical EM |
| :---- | :---- | :---- |
| Mean roots | 0.9 | — |
| P(≥10) | 0.0% | — |
| P(≥15) | 0.0% | — |
| Lexical EM | — | **15 roots** |

The 15 EM roots are also highly significant vs null.

## **24.8 Diagnosis: the trade-off is intrinsic to multi-objective**

The lexical experiment yields three findings:

### **S\_root effectively guides the optimizer**

The effect is monotonic, significant, and reproduces semantically coherent roots. From 2–5 roots (baseline) to 11–15 (with S\_root), with p≈0 vs null. The deterministic IDF-weighting \+ skeleton mechanism works as designed.

### **The roots do not survive strict validation**

Of the 15 roots during the EM, only 3-4 passed the validation with confidences (threshold 0.70). The gap indicates that most of the roots in the EM are artifactual: low-confidence glyphs that the optimizer adjusts to "manufacture" consonant trigrams of roots, without sufficient statistical evidence in the subsequent MCMC.

### **The trade-off is intrinsic to multi-targeting, not to temperature.**

The original hypothesis was that high T degrades n-grams and lowering T would recover them. The data refute this: the n-gram percentile is 12% with both T=5 and T=2. The culprit is not T but**S\_root itself**Any w\_root \> 0 shifts the mapping of the optimal LM solution towards a region of the space that favors root trigrams at the expense of n-grammatical structure. The mapping space does not contain a region where high n-grammatical quality (\>15%) and high root density (\>10) coexist.

## **24.9 Final comparative table: 5 models**

| Metric | Compositional | Constrained | Homophonic | Neural | Lexical |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Characters used | \~10 | — | — | 26 | 25--27 |
| N-grams % | 24% | 5% | 28% | **38%** | 12% |
| Roots matched | 6 | 100 | — | 1 | 3--4 |
| Collapse from | \-0.56 | \-0.45 | \-0.79 | \-0.72 | \-0.91 a \-1.07 |
| R-hat \< 1.1 | 59% | 40% | 68% | **70%** | 67--71% |
| Scorecard | 1+/1±/3− | — | 2+/2±/2− | **4+/0±/1−** | 2--3+/1--2±/1− |

The pure neural model (Chapter 23\) remains the best overall model with 4 PASS. The lexical model provides 2-3 additional statistically significant roots, but at a substantial cost in n-grams and collapse.

## **24.10 Conclusions of Chapter 24**

1. **S\_root functions as an optimization mechanism.**The IDF-weighted component triples the roots during the EM (from 5 to 15), with statistical significance vs null (p≈0 for EM, p=0.008 for validation).

2. **The roots do not survive strict validation.**Of 15 EM roots, only 3-4 pass the confidence test. The gap is diagnostic: the optimizer can "manufacture" roots by adjusting low-confidence glyphs, but these are not supported in the subsequent MCMC.

3. **The diversity/lexicon trade-off is intrinsic, not configurable.**Neither temperature nor the weighting of w\_root allows for negotiation: any S\_root \> 0 degrades the n-grams from \~38% to \~12%, regardless of T. The mapping space does not have a Pareto-optimal region where both properties coexist.

4. **The 3-4 validated roots are statistically significant**(p=0.008), which suggests that the mapping contains real lexical signal, although too weak to support a complete decryption.

5. **The pure neural model (T=3, without S\_root) remains the best model**with scorecard 4+/0±/1−. The value of the lexical experiment is to demonstrate quantitatively*because*Root matching is the most difficult test of all those evaluated: it requires simultaneous mapping diversity, n-grammatical quality, and lexical specificity, three objectives that compete in the solution space.

6. **The 100 roots of the constrained (Part VII) were partially artifactual.**The constrained method yielded 100 roots with 154× enrichment but n-grams at 5%, and its skeleton used wildcards for low-confidence glyphs. The lexical method, with a deterministic skeleton (without wildcards), demonstrates that most of these roots disappear when consistency is required in the mapping. The actual number of sustainable roots is 3–4 with p=0.008, an order of magnitude lower but statistically more robust.

Notebooks: `12_neural_lm.ipynb`, `13_lexical_scoring.ipynb`Results:`neural_results.json`, `lexical_results.json`

# **Capítulo 25\. Neural v2: Multi-Seed EM \+ Hard-K Constraint**

## **25.1 Motivation: Is root matching sensitive to the local optimum?**

Chapters 23–24 present a seemingly paradoxical result: the neural (T=3) approach achieves the best overall scorecard (4+/0±/1−) with only 1 root, while the degenerate compositional approach found 6 and the constrained approach 100 (partially artifactual). Chapter 24 demonstrates that adding a lexical component (S\_root) degrades n-grams from 38% to 12%, confirming that the trade-off is intrinsic to multi-objective n-grams.

However, one question remains unanswered:**How much does the root count depend on the local optimum to which the EM converges?**The objective function has multiple local minima of similar quality (\~-36.2), and different initializations could converge to solutions with different roots. If the variance of root matching between seeds is high, the result of 1 root of the neural v1 could be bad luck.

This chapter explores the solutions space with**two orthogonal strategies**that do not modify the objective function:

1. **Multi-seed (Strategy A):**20 independent EMs with T=3 and the same optimal configuration, varying only the initialization. Seeds 0-9 use frequency mapping \+ random partial scramble (\~30% of glyphs); seeds 10-19 use completely random mapping (respecting C/V roles).

2. **Hard-K \+ T termination (Strategy B):**Rejection constraint that prevents proposals with K \< 20, allowing temperatures T=1.5 and T=2.0 which would give a greater LM signal. 5 seeds per T (10 runs total).

## **25.2 Results of Strategy A: 20 seeds with T=3**

A complete EM (3000 words, 2000 iterations, patience=100, 200 proposals/iter) is executed for each seed (cell 7 of the notebook).`14_neural_v2.ipynb`):

| Seed | Heat | Score | K\_eff | Grammar | Roots | Roots found |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 0 | freq | \-36.65 | 27 | 1.00 | 2 | Knee, road |
| 1 | freq | \-36.49 | 27 | 1.00 | 0 | — |
| 2 | freq | \-37.04 | 27 | 0.83 | 0 | — |
| 3 | freq | \-36.20 | 27 | 1.00 | 1 | thing |
| 4 | freq | \-36.25 | 27 | 1.00 | 3 | Smart, Bread, Send |
| 5 | freq | \-36.18 | 26 | 1.00 | 3 | Smart, Bread, Send |
| 6 | freq | \-36.30 | 27 | 1.00 | 3 | Bread, work, send |
| 7 | freq | \-36.10 | 27 | 1.00 | 1 | slave |
| 8 | freq | \-36.20 | 27 | 1.00 | 1 | thing |
| 9 | freq | \-36.61 | 27 | 1.00 | 0 | — |
| 10 | rand | \-36.24 | 27 | 1.00 | 1 | past |
| 11 | rand | \-36.20 | 27 | 0.83 | 1 | thing |
| 12 | rand | \-36.25 | 27 | 1.00 | 3 | Smart, Bread, Send |
| 13 | rand | \-36.23 | 27 | 1.00 | 3 | Word, servant, past |
| 14 | rand | \-36.25 | 27 | 1.00 | 0 | — |
| 15 | rand | \-36.42 | 27 | 1.00 | 2 | Oil, listen. |
| 16 | rand | \-36.10 | 27 | 1.00 | 1 | slave |
| 17 | rand | \-36.22 | 27 | 1.00 | 0 | — |
| 18 | rand | \-36.20 | 27 | 0.83 | 1 | thing |
| 19 | rand | \-36.63 | 27 | 0.83 | 1 | slave |

**Aggregate statistics:**

| Metric | Value |
| :---- | :---- |
| Score medio ± std | \-36.34 ± 0.23 |
| Roots media ± std | 1.4 ± 1.1 |
| Rango roots | 0--3 |
| Seeds con 0 roots | 5/20 (25%) |
| Seeds con 3 roots | 5/20 (25%) |
| K\_eff constant | 26-27 in all |
| Grammar ≥ 0.83 | 20/20 (100%) |

**Key findings:**

1. **Stable scores.**The standard deviation of 0.23 on a mean score of \-36.34 confirms a well-defined basin of attraction. All seeds converge to solutions of equivalent quality.

2. **Low and limited root count.**No seed exceeds 3 roots. The neural v1 with 1 root was not atypical: it is within 1σ of the mean (1.4 ± 1.1).

3. **Recurrent root clusters.**The roots are not random: they appear in two clusters that share consonants:  
   - Cluster A: Send/Bread/Wise (comparten ח y ל)  
   - Cluster B: Abaab/Abaar/Dab (comparten ب y ر)

   This suggests that the roots emerge from the same cluster of consonant mapping, not from genuine lexical matching.

4. **Initialization doesn't matter.**Seeds freq and rand produce identical root distributions (mean 1.5 vs 1.3, p\>0.5). The initialization type does not influence the final quality.

## **25.3 Results of Strategy B: Hard-K \+ Low T**

EM is executed with hard-K constraint (K\_min=20 due to proposal rejection) at T=1.5 and T=2.0, 5 seeds each (cell 8):

| T | Seed | Score | K\_eff | Grammar | Roots | Roots | Reject% |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 1.5 | 0 | \-36.52 | 27 | 0.67 | 3 | Bread, King, Send | 0.0% |
| 1.5 | 1 | \-36.75 | 26 | 0.67 | 0 | — | 0.0% |
| 1.5 | 2 | \-37.74 | 27 | 0.67 | 3 | Word, servant, past | 0.0% |
| 1.5 | 3 | \-37.63 | 27 | 1.00 | 2 | King, slave | 0.0% |
| 1.5 | 4 | \-36.46 | 27 | 1.00 | 0 | — | 0.0% |
| 2.0 | 0 | \-36.16 | 27 | 1.00 | 3 | Smart, Bread, Send | 0.0% |
| 2.0 | 1 | \-35.34 | 27 | 0.50 | 0 | — | 0.0% |
| 2.0 | 2 | \-37.74 | 27 | 0.67 | 1 | slave | 0.0% |
| 2.0 | 3 | \-36.07 | 27 | 0.67 | 3 | Bread, King, Send | 0.0% |
| 2.0 | 4 | \-37.65 | 27 | 1.00 | 1 | foot | 0.0% |

**Findings:**

1. **Hard-K never activates.**Reject% \= 0.0% in the 10 runs. With the cardinality penalty (w\_card=0.5, K\_max=20) in the objective function, the EM already maintains K\_eff ≥ 26 on its own. The constraint was redundant.

2. **T=1.5 degrades grammar.**Grammar drops to 0.67 in 3/5 seeds (vs. 1.00 typical with T=3). The low temperature concentrates the LM distribution, making it difficult for the grammar anchors to be maintained.

3. **T=2.0 comparable a T=3.**Roots mean \= 1.6 (vs 1.4 in strategy A), similar scores. There is no significant advantage.

4. **Same root clusters.** The roots שלח/לחם/מלך and עבד/עבר/דבר reappear, confirming that they emerge from the same consonant mapping pattern.

## **25.4 Selection of the best candidate and MCMC**

Of the 30 total runs, candidates with K\_eff ≥ 20, grammar ≥ 0.8, and score ≥ median are filtered out. Among these, the one with the most roots is selected.

**Selected:** B\_T2.0\_s0 (estrategia B, T=2.0, seed 0\)

| Property | Value |
| :---- | :---- |
| Score | \-36.16 |
| K\_eff | 27 |
| Grammar | 1.00 |
| Quick roots | 3 (wise, bread, send) |

MCMC multi-chain (4 cadenas × 20K iteraciones, burn-in=5000, thin=10) con propose\_change\_hard\_k:

| MCMC Metric | Value |
| :---- | :---- |
| Best score | \-36.16 |
| K\_eff | 25 |
| R-hat \< 1.1 | **71.1%** |
| Accept rates | 27--28% |

MCMC convergence (71.1%) is the best recorded in all models of the study.

## **25.5 Validación: scorecard 4 PASS / 0 MARGINAL / 1 FAIL**

| Test | Value | Criterion | Result | Neural v1 |
| :---- | :---- | :---- | :---- | :---- |
| 1\. Collapse z-score | \-0.94 | with \> \-1.0 | **PASS** | \-0.72 |
| 2\. N-gram percentile | **68.0%** | \>15% | **PASS** | 38.0% |
| 3\. Root matching | 3 roots | \>10 roots | **FAIL** | 1 root |
| 4\. Cardinality ratio | 0.93 (25/27) | \>0.6 | **PASS** | 0.96 |
| 5\. Grammar anchors | 100% (12/12) | \>60% | **PASS** | 100% |

**Veredicto: 4 PASS / 0 MARGINAL / 1 FAIL**— identical to neural v1.

**Changes compared to v1:**

- **N-gram improves significantly**(68% vs 38%). The selected candidate uses T=2.0, which gives a better LM signal than T=3.0.  
- **Roots go from 1 to 3**but they are still far from the PASS threshold (\>10).  
- **Collapse worsens slightly**(-0.94 vs \-0.72) but it still passes.  
- **MCMC convergence improves** (71.1% vs 69.9%).

## **25.6 Comparative table: 6 models**

| Metric | Compositional | Constrained | Homophonic | Neural v1 | Lexical | Neural v2 |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Characters used | \~10 | — | — | 26 | 25--27 | **25** |
| N-grams % | 24% | 5% | 28% | 38% | 12% | **68%** |
| Roots matched | 6 | 100 | — | 1 | 3--4 | **3** |
| Collapse from | \-0.56 | \-0.45 | \-0.79 | \-0.72 | \-0.91 | **\-0.94** |
| R-hat \< 1.1 | 59% | 40% | 68% | 70% | 67--71% | **71%** |
| Scorecard | 1+/1±/3− | — | 2+/2±/2− | 4+/0±/1− | 2--3+/1--2±/1− | **4+/0±/1−** |

The neural v2 sets the new record in n-grams (68%) and MCMC convergence (71.1%), confirming the neural as the best model family.

## **25.7 Diagnosis: confirmed structural limit**

### **The variance of root matching is low**

The root distribution across 30 runs is: mean \= 1.5, standard \= 1.1, maximum \= 3\. The neural v1 with 1 root was within 1σ. Exploring 30 distinct initializations does not break the barrier.**The limit of \~3 roots is structural, not stochastic.**.

### **The roots form consonant clusters**

The roots found are not lexically independent. They appear in two clusters that share consonants:

- Smart/bread/send share H and L  
- Slave/past/talk comparten in y r

This indicates that the "roots" emerge because the mapping assigns certain frequent glyphs to ח, ל, ב, ר, and the resulting combinations match actual roots by co-occurrence, not by genuine lexical matching.

### **Hard-K is unnecessary with the current objective function**

The rejection constraint never triggers (0% rejections in 10 runs). The cardinality penalty in the objective function already maintains K\_eff ≥ 26\. This confirms that the scoring design in Chapter 23 was sufficient to prevent collapse.

### **T=2.0 improves n-grams without sacrificing structure**

The selected candidate (T=2.0) achieves a 68th percentile n-gram vs. 38% for neural v1 (T=3.0). The lower temperature concentrates the LM distribution, producing more "natural" Hebrew sequences. However, this improvement in n-grams does not translate into more roots, confirming the independence between the two metrics within the stable solution region.

## **25.8 Conclusions of Chapter 25**

1. **The limit of \~3 roots is structural.**30 runs with different initializations and temperatures produce a maximum of 3 roots (mean 1.5 ± 1.1). The root matching FAIL of the neural network is not sensitive to the local optimum: it is a limit of the solution space.

2. **The scores converge to a stable basin**(-36.34 ± 0.23). The objective function defines a landscape with multiple local minima of equivalent quality, differing only in mapping details.

3. **Roots are artifacts of consonant clusters**, no lexical cue. The two recurrent clusters (חכם/לחם/שלח and עבד/עבר/דבר) share consonants, indicating positional co-occurrence rather than matching of biblical roots.

4. **Hard-K is redundant**with the current objective function (0% rejections). The quadratic cardinality penalty already prevents collapse.

5. **T=2.0 offers an interesting compromise**: better n-grams (68% vs 38%) with equivalent scorecard (4+/0±/1−). If the root FAIL is accepted as a structural limit, T=2.0 is preferable to T=3.0.

6. **The neural v2 reinforces the study's conclusions.**: root matching is the most resilient test against all proven decryption methods, and its FAIL reflects a fundamental limitation of the many-to-one pipeline on a manuscript whose statistical structure is compatible with a Semitic language but whose lexical specificity escapes current methods.

Notebook: `14_neural_v2.ipynb`Results:`neural_v2_results.json`

# **Chapter 26\. Syllabic-positional mapping: 3 tables onset/nucleus/coda**

## **26.1 Motivation: Does intra-syllabic position unlock decoding?**

The SilPart model (d=0.445, the closest to the Voynich model among the 11 generative models in Chapter 14\) predicts that 90% of the glyphs are*position-locked*Its selection depends on the position within the syllable (onset, nucleus, coda), with minimal overlap between positions (glyph\_overlap=0.1, pos\_bias=3.0). However, the decryption models in Chapters 23–25 use a planar mapping`{glyph → character}`ignoring this positional structure.

**Hypothesis:**A mapping conditioned by intra-syllabic position—three independent tables, one per position—unlocks Hebrew roots that the single mapping obscured, by allowing "polyvalent" glyphs to map to different consonants according to their syllabic role.

## **26.2 Design of the positional model**

### **Assignment of intra-syllabic positions**

The syllabic segmentation by transition point (20th percentile) of cell 2 is reused. Each glyph within a syllable is assigned to a position according to deterministic rules:

| Syllable length | Assignment |
| :---- | :---- |
| 1 glyph | → nucleus |
| 2 glyphs | → first=onset, second=coda |
| 3+ glyphs | → first=onset, last=coda, middle=nucleus |

### **Active positions per glyph**

A glyph is considered "active" in a position if it appears ≥5 times in that position (MIN\_POS\_FREQ=5). If no position reaches the threshold, the most frequent position is assigned as the fallback. This results in:

| Category | Glyphs | Percentage |
| :---- | :---- | :---- |
| Assets in 1 position | 122 | **73.5%** |
| Assets in 2 positions | 29 | 17.5% |
| Assets in 3 positions | 15 | 9.0% |
| Total mapping entries | 225 | (vs 166 in flat model) |

**The SilPart premise is confirmed:**73.5% of the glyphs are locked to a single intra-syllabic position, consistent with the prediction of glyph\_overlap=0.1.

### **PositionalGlyphMappingState**

A class with three independent tables is implemented (`mapping_onset`, `mapping_nucleus`, `mapping_coda`The initialization starts with three identical tables (frequency mapping), and the EM diverges them. The proposed changes randomly select a glyph and one of its active positions.

The scoring is analogous to that of Chapter 23 (5 components) but adapted:`apply_word_positional()`Consult the table corresponding to the position of each glyph within its syllable. Incremental scoring indexes by`(glyph, position)`to re-evaluate only the affected words.

## **26.3 Positional distribution: the 15 most frequent glyphs**

The high-frequency glyphs show very disparate positional distributions, validating SilPart's premise:

| Glyph | Freq | Onset | Nucleus | Coda | Active positions |
| :---- | :---- | :---- | :---- | :---- | :---- |
| A1 | 25,106 | 8,011 | 12,053 | 5,042 | onset/nucleus/coda |
| A2 | 17,464 | 1,528 | 2,465 | 13,471 | onset/nucleus/coda |
| A3 | 14,545 | 2,862 | 9,930 | 1,753 | onset/nucleus/coda |
| K1 | 11,066 | 4,770 | 5,182 | 1,114 | onset/nucleus/coda |
| B2 | 10,668 | 1,077 | 3,035 | 6,556 | onset/nucleus/coda |
| B1 | 10,492 | 4,992 | 5,019 | 481 | onset/nucleus/coda |
| J1 | 10,257 | 133 | 8,552 | 1,572 | coda/nucleus/onset |
| D1 | 5,425 | 5,292 | 133 | 0 | nucleus/onset |
| L1 | 4,174 | 3,280 | 892 | 2 | nucleus/onset |
| G1 | 4,162 | 4 | 325 | 3,833 | coda/nucleus |

D1 and L1 are almost exclusively onset (97–79%), G1 is almost exclusively coda (92%). These glyphs are exactly the "paradigms" of prefixes and suffixes documented by Stolfi.

## **26.4 Multi-Seed EM positional**

20 EM runs are executed (10 seeds × 2 temperatures T=2.0 and T=3.0). Parameters: SAMPLE\_EM=3000 words, 2000 iteration, patience=100, 200 proposals/iteration. Seeds 0-4: frequency \+ scramble, seeds 5-9: random C/V.

### **Results by temperature**

| T | Score medio ± std | Roots medio ± std | Diverge mean ± std. |
| :---- | :---- | :---- | :---- |
| 2.0 | \-34.34 ± 0.75 | 1.8 ± 1.6 | 38.0 ± 2.5 / 44 |
| 3.0 | \-34.68 ± 0.50 | 2.1 ± 1.9 | 38.5 ± 1.8 / 44 |

### **EM Findings**

1. **K\_eff \= 27 in all runs.**The three tablets together cover 100% of the Hebrew alphabet.

2. **Grammar \= 1.00 a 17/20 runs.**The grammatical structure is perfectly maintained.

3. **Massive divergence: 38/44 multi-position glyphs diverge**(86.4%). The EM effectively differentiates the three tables \--- glyphs that appear in multiple positions receive characters*distinct*in each one. The tables do not collapse to identical.

4. **Roots: media 1.8--2.1, max 7\.**Slight improvement over neural v2 (mean 1.5 ± 1.1) but far from the PASS threshold of 10 roots.

5. **Scores better than v2.**\-34.3 to \-34.7 vs \-36.3 in neural v2. The positional space has more degrees of freedom (225 vs 166 entries), which allows for a better fit to the objective function.

### **Best selected candidate**

T=2.0, seed 1: score=-34.28, K\_eff=27, grammar=1.00, roots=5, divergent=38/44.

## **26.5 MCMC multi-chain**

4 strings × 20K iterations, burn-in=5000, thin=10, with positional proposals:

| MCMC Metric | Value |
| :---- | :---- |
| Best score | \-34.28 |
| K\_eff | 27 |
| Divergent | 38/44 |
| R-hat \< 1.1 | **92.2%** |
| Accept rates | 27--29% |

The MCMC convergence (**92.2%**) is the best of all the models in the study, far surpassing neural v2 (71.1%). All 4 chains converge to the same point, indicating a robust optimum.

## **26.6 Validación: scorecard 4 PASS / 2 MARGINAL / 0 FAIL**

| Test | Value | Criterion | Result | Neural v2 |
| :---- | :---- | :---- | :---- | :---- |
| 1\. Collapse z-score | \-0.20 | with \> \-1.0 | **PASS** | \-0.94 |
| 2\. N-gram percentile | 14.0% | \>15% | **MARGINAL** | 68.0% |
| 3\. Root matching | 5 roots | \>10 roots | **MARGINAL** | 3 roots |
| 4\. Cardinality ratio | 1.00 (27/27) | \>0.6 | **PASS** | 0.93 |
| 5\. Grammar anchors | 100% (12/12) | \>60% | **PASS** | 100% |
| 6\. Positional divergence | 86.4% | \>20% | **PASS** | — |

**Veredicto: 4 PASS / 2 MARGINAL / 0 FAIL.**

Test 6 is new and specific to the positional model: it measures the fraction of multi-position glyphs whose tables diverge. PASS \> 20% indicates genuine divergence; FAIL \< 5% would indicate collapse to a single table (position is irrelevant). The result of 86.4% confirms that the three tables are genuinely distinct.

### **Detailed comparison with neural v2**

| Metric | Neural v2 | Syllabic | Change |
| :---- | :---- | :---- | :---- |
| Collapse from | \-0.94 | **\-0.20** | Noticeable improvement |
| N-grams % | **68.0%** | 14.0% | Severely degraded |
| Roots | 3 | **5** | Modest improvement |
| K\_eff | 25 | **27** | Improvement |
| R-hat \< 1.1 | 71.1% | **92.2%** | Noticeable improvement |
| Scorecard | 4+/0±/1− | 4+/2±/0− | Trade-off |

The positional model wins in collapse (-0.20, the best in the entire study), cardinality (27/27), convergence (92.2%), and roots (5 vs. 3). However, it loses drastically in n-grams (14% vs. 68%). The scorecard replaces the root matching FAIL with two MARGINAL errors, eliminating absolute failures but at the cost of n-grams.

## **26.7 Diagnosis: positional divergence vs. sequential coherence**

### **The divergence is real but not lexical**

The three tables diverge in 86.4% of the multi-position glyphs. This is not artifactual: the EM has 225 degrees of freedom (vs. 166 in the flat model) and exploits them. However, this divergence does not produce significantly more roots (5 vs. 3, a marginal improvement).

### **The n-gram collapses because divergence breaks sequential coherence**

A glyph that in onset position maps to`on`and in coda maps to`to`It generates character sequences that do not respect the bigram/trigram patterns of Hebrew. LSTM is trained on consistent Hebrew, where the identity of a character does not change according to its syllabic position. All three tables introduce discontinuities that LM penalizes.

### **The improvement in collapse is an artifact of greater freedom**

The better collapse z-score (-0.20, compared to \-0.94 in v2) is explained by the additional degrees of freedom: with 225 mapping entries, the optimizer can distribute glyphs among collapse groups more homogeneously, not because the underlying structure is more coherent.

## **26.8 Interpretation: SilPart as a production mechanism vs. decryption**

This result requires a crucial distinction between two readings of SilPart:

### **Encoding direction (SilPart models this)**

SilPart describes the**glyph selection**Given a character in the onset position, the scribe chooses a glyph from the onset pool; given the same character in the coda position, it chooses a glyph from the coda pool. The address is**many glyphs → one character**(positional homophony). The glyph changes, but the meaning does not.

### **Decryption address (our notebook tests this)**

The 3-table model tests the opposite direction:**one glyph → many characters**according to position (positional polyphony). The glyph is the same, but its meaning changes.

### **Empirical evidence and its correct interpretation**

| Evidence | Does it support SilPart (homophony)? | Does it support 3 tables (polyphony)? |
| :---- | :---- | :---- |
| 73% glifos position-locked | **Yeah**— almost disjoint pools | Neutral — compatible with both |
| D1 onset only, G1 coda only | **Yeah**— specialized glyphs | Neutral — does not require polyphony |
| Neural v2 (1 tabla) n-gram=68% | **Yeah**— each glyph has 1 meaning | No — 1 table is enough |
| 3 tables degrade n-gram to 14% | **Yeah**— forcing polyphony breaks coherence | **No**— polyphony damages |
| 3 tables diverge at 86% | Neutral | Partial — they diverge but do not improve roots |

**Conclusion:**The data supports the reading of SilPart as**positional homophony**(many glyphs → one character, with position-dependent selection) and discard the reading of**positional polyphony**(one glyph → many characters depending on position). Positional dependency operates in the*selection*of the glyph, not in its*meaning*.

This is analogous to positional variants in Arabic, where the initial, medial, and final forms of a letter are distinct glyphs that encode the same phoneme. In the Voynich, D1 (onset) and G1 (coda) could be "positional allographs" of the same underlying character, not distinct characters that change meaning.

## **26.9 Comparative table: 7 models**

| Metric | Compositional | Constrained | Homophonic | Neural v1 | Lexical | Neural v2 | Syllabic |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Characters used | \~10 | — | — | 26 | 25--27 | 25 | **27** |
| N-grams % | 24% | 5% | 28% | 38% | 12% | **68%** | 14% |
| Roots matched | 6 | 100 | — | 1 | 3--4 | 3 | **5** |
| Collapse from | \-0.56 | \-0.45 | \-0.79 | \-0.72 | \-0.91 | \-0.94 | **\-0.20** |
| R-hat \< 1.1 | 59% | 40% | 68% | 70% | 67--71% | 71% | **92%** |
| Scorecard | 1+/1±/3− | — | 2+/2±/2− | 4+/0±/1− | 2--3+/1--2±/1− | 4+/0±/1− | **4+/2±/0−** |

The positional model has the best collapse, cardinality, and MCMC convergence in the study, but the worst n-gram after the constrained model. The neural v2 (Table 1\) continues to dominate in the most diagnostic metric (n-grammatical realism).

## **26.10 Conclusions of Chapter 26**

1. **The SilPart premise is empirically confirmed.**73.5% of the Voynich glyphs are position-locked (active in a single intra-syllabic position), consistent with the prediction of the generative model (glyph\_overlap=0.1).

2. **Positional polyphony is ruled out.**The three tables diverge (86.4%), but the divergence degrades the n-grams from 68% to 14% and only adds 2 marginal roots (5 vs. 3). The Voynich Manuscript does not use position-conditioned mapping where a glyph means different things depending on its syllabic role.

3. **Positional homophony remains viable.**SilPart as a mechanism of*production*(Many glyphs → one character, with selection by position) is compatible with all data. Glyphs such as D1 (onset-only) and G1 (coda-only) are best interpreted as positional allographs of the same underlying character.

4. **The limit of \~3--5 roots remains.**Neither additional parameters (3 tables, 225 entries) nor S\_root (Chapter 24\) overcome the barrier. Root matching is a structural limitation of the solution space, independent of the number of mapping tables.

5. **The best MCMC convergence in the study (92.2%)**It indicates that positional space has a wider and better-defined basin of attraction than the plane, although this does not translate into better deciphering.

6. **Implications for future work:**A decryption model that takes advantage of SilPart's positional homophony should operate in the reverse direction: identifying clusters of glyphs that are positional variants of the same character (collapse glyphs, do not expand mappings), reducing the effective vocabulary before applying decryption.

Notebook: `15_syllabic_positional.ipynb`Results:`syllabic_resultados.json`

# **Chapter 27\. Syllabic-positional decipherment with Aramaic (Targum Onkelos)**

## **27.1 Motivation: Hebrew vs. Aramaic as a source language**

The Bayesian analysis in Chapter 18 showed that Hebrew and Aramaic are the two best candidates at the syllabic level, with a gap of only 0.27 nats (Hebrew \-35.64, Aramaic \-35.91). At the compositional level, the gap widens to 3.87 nats, but the validation in Chapter 19 ruled out the compositional mapping as degenerate. The remaining question is: does the Hebrew/Aramaic equivalence hold when the full syllabic-positional model (3 tables \+ LSTM) is applied?

To answer it, Chapter 26 is replicated, substituting the Torah with the**Targum Onkelos**(traducción aramea de la Torah) como corpus de lengua target.

## **27.2 Aramaic corpus: Targum Onkelos**

The corpus is obtained from Sefaria (same source as the Hebrew), by downloading the five books of the Pentateuch in their Aramaic version:

| Parameter | Value |
| :---- | :---- |
| Fountain | Sefaria / Targum Onkelos |
| Books | Genesis, Exodus, Leviticus, Numbers, Deuteronomy |
| Total words | \~82,842 |
| Subsampled to | 37,087 (= Voynich size) |
| Distinct characters | 27 |
| Alphabet | Identical to biblical Hebrew (22-letter alephbet \+ 5 sofit) |

The Aramaic alphabet is formally identical to Biblical Hebrew: the same 27 graphic forms. The difference lies in the vocabulary, verbal morphology (different paradigms), and grammatical particles (Aramaic uses ד- as a relative pronoun where Hebrew uses ש-/אשר).

## **27.3 Neural LM Aramaic**

The LSTM is trained with the same architecture as Hebrew (2 layers, embed=32, hidden=192, dropout=0.2, 476,991 parameters):

| Metric | Hebrew (Torah) | Aramaic (Onkelos) |
| :---- | :---- | :---- |
| Trained eras | 30 | 30 |
| Better value loss | 2.004 | 2.005 |

The value loss is virtually identical (Δ \= 0.001). Both corpora are biblical legal/narrative texts with nearly identical character distributions; the LSTM cannot discriminate between them at the language model level.

## **27.4 EM multi-seed**

20 runs are executed (10 seeds × 2 temperatures: T=2.0, T=3.0), with the same configuration as in Chapter 26:

| Metric | Hebrew (Chapter 26\) | Aramaic |
| :---- | :---- | :---- |
| Score medio (T=2.0) | \-34.48 ± 0.47 | \-34.99 ± 0.61 |
| Score medio (T=3.0) | \-34.68 ± 0.50 | \-35.10 ± 0.56 |
| Roots medio | 1.9 | 1.8 |
| Roots max | 7 | 5 |
| K\_eff | 27 (all) | 27 (all) |
| Grammar \= 1.00 | 17/20 | 18/20 |

The Aramaic scores are \~0.5 points worse than the Hebrew scores, consistent with the Bayesian gap in Chapter 18\. The root distribution is statistically indistinguishable (mean 1.8 vs 1.9).

### **Best candidate**

T=2.0, seed 7: score=-34.89, K\_eff=27, grammar=1.00, roots=5 {bend, man, slave, past, past}, divergent=37/44.

## **27.5 MCMC and convergence**

| MCMC Metric | Hebrew | Aramaic |
| :---- | :---- | :---- |
| Best score | \-34.28 | \-34.89 |
| K\_eff | 27 | 27 |
| Divergent | 38/44 | 37/44 |
| R-hat \< 1.1 | **92.2%** | **90.4%** |
| Accept rates | 27--29% | 28--28% |

Aramaic convergence (90.4%) is slightly lower than Hebrew convergence (92.2%) but is still the second best in the study, well above the flat neural v2 (71.1%).

## **27.6 Validación: scorecard 4 PASS / 2 MARGINAL / 0 FAIL**

| Test | Hebrew | Aramaic | D |
| :---- | :---- | :---- | :---- |
| 1\. Collapse z-score | PASS (-0.20) | PASS (-0.35) | \-0.15 |
| 2\. N-gram percentile | MARGINAL (14.0%) | MARGINAL (6.0%) | \-8.0 pp |
| 3\. Root matching | MARGINAL (5 roots) | MARGINAL (5 roots) | \= |
| 4\. Cardinality ratio | PASS (1.00) | PASS (1.00) | \= |
| 5\. Grammar anchors | PASS (100%) | PASS (100%) | \= |
| 6\. Positional divergence | PASS (86.4%) | PASS (84.1%) | \-2.3 pp |

**Veredicto: 4 PASS / 2 MARGINAL / 0 FAIL**— identical to the Hebrew test for test.

### **Analysis of the differences**

The only quantitatively notable difference is the**n-gram percentile**6% Aramaic vs. 14% Hebrew (both MARGINAL). The trigrams of the Targum Onkelos fit the mapped Voynich corpus less well than those of the Torah, but the difference is not enough to change the verdicts. The roots found are the same five in both cases: ברך, עבד, and עבר appear in both, while the remaining two differ (Hebrew: דרך, מלך; Aramaic: גבר, רבב). All belong to the shared biblical vocabulary.

## **27.7 Shared roots: generic biblical sign, not specific to language**

The roots found by both models belong to the most basic lexicon of the biblical text:

| Root | Meaning | Shared? |
| :---- | :---- | :---- |
| knee | bless | Yeah |
| slave | serve/work | Yeah |
| past | cross/pass | Yeah |
| king | reign | Hebrew only |
| way | path | Hebrew only |
| man | be strong | Aramaic only |
| stain | to be many | Aramaic only |

All of these are high-frequency roots in both corpora. Their appearance reflects the biblical vocabulary shared between the Torah and the Targum (which is a near-literal translation), not a discriminatory signal between languages.

## **27.8 Comparative table: 8 models**

| Metric | Composic. | Constr. | Homosexual. | Neural v1 | Lexical | Neural v2 | Syl-Heb | Syl-Ara |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Characters used | \~10 | — | — | 26 | 25--27 | 25 | 27 | **27** |
| N-grams % | 24% | 5% | 28% | 38% | 12% | **68%** | 14% | 6% |
| Roots | 6 | 100 | — | 1 | 3--4 | 3 | 5 | **5** |
| Collapse from | \-0.56 | \-0.45 | \-0.79 | \-0.72 | \-0.91 | \-0.94 | **\-0.20** | \-0.35 |
| R-hat \< 1.1 | 59% | 40% | 68% | 70% | 67--71% | 71% | **92%** | 90% |
| Scorecard | 1+/1±/3− | — | 2+/2±/2− | 4+/0±/1− | 2--3+/1--2±/1− | 4+/0±/1− | 4+/2±/0− | **4+/2±/0−** |

## **27.9 Conclusions of Chapter 27**

1. **Hebrew and Aramaic are indistinguishable with the syllabic-positional model.**The scorecard is identical (4+/2±/0−), the metrics differ by less than 1σ, and the roots found come from the shared biblical lexicon. This confirms and extends the conclusion of the syllabic Bayesian (Chapter 18): the gap of 0.27 nats is not operationally significant.

2. **The Aramaic n-gram (6%) is worse than the Hebrew n-gram (14%), but both are MARGINAL.**The degradation is explained by differences in trigrammatic frequencies between Torah and Targum, not by a fundamental incompatibility. The Aramaic verbal paradigms (pa'el, af'el, itpa'al) generate character transitions slightly different from the Hebrew ones (pi'el, hif'il, hitpa'el).

3. **Equivalence is expected and constitutes a positive result.**Torah and Targum Onkelos share: (a) an identical alphabet (27 forms), (b) triliteral consonantal morphology, (c) biblical vocabulary (\~70% shared roots), and (d) similar syntactic structure (the Targum is a near-literal translation). Any language model-based decipherment method will be unable to distinguish between the two as source languages.

4. **Implication for the Semitic hypothesis.**If the Voynich manuscript encodes a Northwest Semitic language, the "Hebrew vs. Aramaic" distinction is likely anachronistic for the manuscript. The Biblical Hebrew-Aramaic continuum (5th century BCE–2nd century CE) shares too much structure to be separable by statistical decipherment methods. The correct hypothesis would be "Biblical Northwest Semitic" as a single category.

5. **The limit of \~3--5 roots is maintained in both languages.**Neither the change of target corpus nor the 225 positional degrees of freedom overcome the barrier. Root matching is a structural limitation of the solution space, confirming the diagnosis of Chapter 25 (neural v2).

Notebook: `16_syllabic_aramaic.ipynb`Results:`syllabic_arameo_resultados.json`

# **Chapter 28\. Collapse of positional allographs**


---

Continued in Part X.

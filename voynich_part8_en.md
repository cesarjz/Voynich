# **PART VIII**

# **Positional homophonic cipher**

Part VII concluded with a clear diagnosis: compositional mapping is degenerate (scorecard 1+/1±/3−), and constrained EM improves morphological structure (100 biblical roots, enrichment 154×) but worsens sequential fluency (n-graph percentile 5%). The tension between roots and n-grams, along with the persistent morphology-phonotaxis asymmetry, points to a fundamental problem: LM dominates scoring and collapses mapping. Part VIII addresses this issue from a different angle: if the SilPart model (d=0.445) correctly describes Voynich generation as a syllabary with positional variants, then there should be a homophonic cipher pattern in which different glyphs represent the same character depending on their position (onset vs. coda) within the syllable. A model is designed and evaluated that searches for precisely this signal.

# **Chapter 22\. Positional Homophonic Cipher**

## **22.1 Hypothesis and design**

The generative model SilPart (Part IV, d=0.445) outperforms the other 10 candidate models because it reproduces the positional distribution of Voynichese glyphs: each glyph tends to appear preferentially in onset or coda position within segmented syllables. If this positional preference is a feature of the actual writing system—not an artifact of the generative model—then it should manifest as a positional homophonic cipher: two distinct glyphs can represent the same character in the underlying language, but one appears preferentially at the beginning of a syllable (onset) and the other at the end (coda).

To test this hypothesis, a five-component pipeline is designed (cells 4-8 of the notebook).`11_homophonic.ipynb`):

1. **Positional clustering.**Each glyph is classified as onset-specialist, coda-specialist, or mixed based on its ratio of occurrence in the onset vs. coda position, with a configurable threshold. A glyph with a ratio ≥ threshold is onset; ≤ (1 − threshold) is coda; intermediate is mixed.

2. **HomophonicMappingState.**The MappingState from Part VI is extended to penalize pairs of glyphs that map to the same character but share the same position (same-position) and to reward pairs that differ in position (cross-position). This incentivizes homophonic variants to be positionally complementary.

3. **Composite scoring (6 components):**

| Component | Weight | Function |
| :---- | :---- | :---- |
| S\_LM | w\_lm \= 2.0 | Verisimilitude under Hebrew CharLM |
| S\_pos | w\_pos \= 0.5 | Positional consonant/vowel compatibility |
| S\_homo | w\_homo \= 0.3 | Cross-position bonus, same-position penalty |
| S\_ent | w\_ent \= 0.3 | Entropy of glyph/character distribution |
| S\_card | w\_card \= 0.2 | Penalty for exceeding k\_max glyphs per character |
| S\_gram | w\_gram \= 0.5 | Grammar anchors (12 anchored glyphs) |

4. **Positional-aware initialization.**The initial mapping assigns glyphs to characters respecting the onset/coda classification, distributing homophonic variants between complementary positions.

5. **EM \+ MCMC.**Two-phase optimization: greedy EM followed by multi-chain MCMC to explore the later.

## **22.2 Hyperparameter Sweep**

A sweep is performed on the three central hyperparameters of the homophonic model (cell 9 of the notebook):

### **Homophonic weight (w\_homo)**

| w\_homo | Score |
| :---- | :---- |
| 0.3 | \-41.84 |
| 0.5 | \-41.84 |
| 1.0 | \-41.84 |
| 1.5 | \-41.84 |
| 2.0 | \-41.84 |

**Diagnosis: inert component.**The score is identical (-41.84) for all values ​​of w\_homo, from 0.3 to 2.0. This means that the homophonic term does not contribute to the scoring: the positional onset/coda signal does not generate a gradient useful for distinguishing between mappings.

### **Maximum cardinality per position (k\_max)**

| k\_max | Score |
| :---- | :---- |
| 1 | \-41.91 |
| 2 | \-41.84 |
| 3 | \-42.09 |

**Result:**k\_max \= 2 is marginally better (-41.84 vs \-41.91 with k=1 and \-42.09 with k=3). The difference is minimal (0.07-0.25 points), consistent with the inertia of the homophonic component.

### **Positional ranking threshold**

| Threshold | Score | Onset | Coda | Mixed |
| :---- | :---- | :---- | :---- | :---- |
| 0.55 | \-43.53 | — | — | — |
| 0.65 | \-41.84 | — | — | — |
| 0.75 | **\-41.56** | **0** | **10** | **42** |
| 0.85 | \-42.65 | — | — | — |

**Result:**Threshold 0.75 produces the best score (-41.56), but with a radical asymmetry:**0 onset-specialists**10 coda-specialists and 42 mixed. No Voynich glyph is sufficiently specialized in onset position to be classified as an onset-specialist at the optimum threshold. The 10 coda-specialists are: Ab, B3, B4, E2, F3, G3, H1, V2, W1, W2.

This onset/coda asymmetry is unexpected and problematic: if a positional homophonic cipher existed, we would expect glyphs specialized in*both*positions. The total absence of onset specialists invalidates the central premise of the model.

## **22.3 EM y MCMC**

With the best sweep hyperparameters (w\_homo \= 0.3, k\_max \= 2, threshold \= 0.75), the two optimization phases are executed:

### **EM greedy**

| Metric | Value |
| :---- | :---- |
| Score EM | **\-40.94** |

### **MCMC multi-chain**

| Parameter | Value |
| :---- | :---- |
| Chains | 4 |
| Iterations/string | 15,000 |
| Burn-in | 5,000 |
| Thinning | 5 |

| Chain | Acceptance rate |
| :---- | :---- |
| 1 | 43.7% |
| 2 | 42.9% |
| 3 | 42.2% |
| 4 | 45.5% |

(cells 10-13 of the notebook)

| Metric | Value |
| :---- | :---- |
| Best score MCMC | **\-40.33** |
| Average acceptance | 43.6% |
| R-hat \< 1.1 | **68.1%** |

The MCMC convergence (68.1% of glyphs with R-hat \< 1.1) is notably better than that of the compositional (57.1%) and constrained (39.9%) models. This does not indicate a better model overall, but rather a more concentrated posterior: with 0 onset-specialists and an inert homophonic component, the MCMC converges more readily because the effective space is simpler.

## **22.4 3-way comparison and validation**

The three decryption models—compositional (Part VI), constrained (Part VII, Chapter 20), and homophonic (this chapter)—are compared over 7 common metrics plus 2 specific to the homophonic model (cells 14-19 of the notebook):

| Metric | Compositional | Constrained | Homophonic |
| :---- | :---- | :---- | :---- |
| Score | \-39.71 | \-40.69 | \-40.33 |
| PPX mapped | 15.15 | 19.24 | 16.60 |
| Max glifos/char | 17 | 11 | **7** |
| R-hat \< 1.1 | 57% | 40% | **68%** |
| N-gram percentile | 24% | 5% | **28%** |
| Collapse z-score | \-0.56 | \-0.45 | \-0.79 |
| Root enrichment | 84× | 154× | 48× |
| Cross-position links | N/A | N/A | **0** |
| Max same-pos/char | N/A | N/A | **2** |

**Reading by metrics:**

- **Score:**The compositional remains the best (-39.71). The homophonic (-40.33) improves on the constrained (-40.69) but not on the baseline.  
- **Cardinality:**The homophonic achieves the most controlled collapse (max 7 glyphs/char), equal to or better than the explicit restrictions of the constrained (max 11).  
- **Convergence:**R-hat 68% is the best convergence of the three models, but it reflects the simplicity of the later model, not the quality of the mapping.  
- **N-grams:**The homophonic sequence achieves the highest percentile (28%), surpassing both the compositional (24%) and constrained (5%) sequences. Cardinality+entropy restrictions produce more diverse sequences.  
- **Collapse:**The z-score for the homophonic (-0.79) is the worst of the three. Glyphs grouped under the same character are less distributionally similar than in the other models.  
- **Roots:**The enrichment (48×) is the lowest of the three, a consequence of the restricted cardinality (max 7\) which limits the probability of finding consonant trigrams.  
- **Cross-position links \= 0:**The specific test for the homophonic model fails completely. No Hebrew character receives onset and coda glyphs simultaneously.  
- **Max same-pos/char \= 2:**It meets the criterion (≤2), but it is a trivial result when there are no onset-specialists.

### **Homophonic scorecard**

| Test | Value | Criterion | Result |
| :---- | :---- | :---- | :---- |
| Collapse coherence (z-score) | \-0.79 | z \> \-0.3 \= PASS | **MARGINAL** |
| N-gram realism (percentil) | 28.0% | \>15% \= PASS | **PASS** |
| Root enrichment | 47.6× | \>50× \= PASS | **MARGINAL** |
| Max glifos/char | 7 | ≤7 \= PASS | **PASS** |
| Cross-position links | 0 | ≥10 \= PASS | **FAIL** |
| Max same-pos/char | 2 | ≤2 \= PASS | **PASS** |

**Veredicto global: 3 PASS, 2 MARGINAL, 1 FAIL.**The homophonic model does not confirm the positional cipher hypothesis. PASS metrics (cardinality, same-pos) reflect imposed constraints, not a discovered signal. The FAIL on cross-position links is the diagnostic result: the model's core mechanism is not functioning.

## **22.5 Diagnosis: why the hypothesis fails**

### **0 onset-specialists at any reasonable threshold**

The clearest result is the complete absence of onset-specialist glyphs. Within the explored threshold range (0.55–0.85), no Voynichese glyph appears in onset position with sufficient exclusivity to be classified as a specialist. The 10 coda-specialists (Ab, B3, B4, E2, F3, G3, H1, V2, W1, W2) exist because some glyphs appear preferentially at the end of a word/syllable, but there is no symmetric complement in onset. This is incompatible with a positional homophonic cipher, which requires onset-coda pairs mapping to the same character.

### **w\_homo inert (flat signal on sweep)**

The homophonic scoring component does not generate a useful gradient. Varying w\_homo from 0.3 to 2.0 does not change the score at all (-41.84 in all cases). This confirms that the positional distribution of Voynichese glyphs does not contain the onset/coda signal that the model is looking for: rewarding cross-position and penalizing same-position has no effect because the glyphs are not positionally specialized.

### **What DOES work: cardinality \+ entropy**

Despite the failure of the central mechanism, the homophonic model produces the most controlled collapse (max glyphs/char \= 7\) and the best n-graph percentile (28%). These benefits come from the cardinality and entropy components inherited from the constrained term, not from the homophonic term itself. The model works.*although*its central component, no*thanks to* he.

### **What DOESN'T work: the central positional mechanism**

The cross-position links \= 0 is definitive. Even after MCMC with 4×15K iterations and healthy acceptance rates (42-45%), the posterior does not produce any pair of glyphs that map to the same character from complementary positions. The positional homophonic cipher hypothesis is incompatible with the data.

### **Three models, three failure profiles → LM dominance is the fundamental problem**

| Model | Strength | Weakness | Diagnosis |
| :---- | :---- | :---- | :---- |
| Compositional | Best score (-39.71) | Collapse shoes (17 g/c) | Unrestricted LM → collapse |
| Constrained | 100 roots (154×) | N-grams 5% | Anchors help with morphology, not phonotaxis |
| Homophonic | Cardinality (7 g/c), n-grams (28%) | 0 cross-pos links | Non-existent positional mechanism |

All three models share the same underlying problem: the Hebrew LM (CharLM trigram, weight 2.0) dominates the scoring. Each model attempts to counteract this dominance with different constraints (grammatical anchors, cardinality penalty, positional bonus), but none resolves the fundamental conflict between maximizing likelihood under the LM and producing a linguistically valid mapping.

## **22.6 Conclusions and next steps**

### **Conclusions from Chapter 22**

1. **The positional homophonic cipher hypothesis is not confirmed.**The central diagnostic test \---cross-position links--- gives 0\. No Hebrew character receives onset and coda glyphs simultaneously, invalidating the premise of complementary positional variants.

2. **The homophonic component is inert.**The w\_homo weight does not affect the score (identical from 0.3 to 2.0). The positional distribution of the Voynichese glyphs does not contain the signal the model is looking for.

3. **0 onset-specialists.**The onset/coda asymmetry (0 vs 10\) is incompatible with a symmetric positional cipher system. The Voynich glyphs do not specialize in onset position as clearly as they do in coda position.

4. **The benefits of the model are indirect.**The controlled cardinality (max 7\) and the best n-graph percentile (28%) come from the entropy and cardinality components, not from the homophonic mechanism.

5. **Three models, one convergent diagnosis.**Compositional, constrained, and homophonic exhibit complementary failure profiles that point to the same fundamental problem: the dominance of the LM in Bayesian scoring. No combination of additional constraints resolves the conflict between plausibility and linguistic validity as long as the CharLM trigram is the dominant component.

### **Implications for the study**

The failure of the homophonic model reinforces the study's central narrative: the decryption pipeline produces informative rankings (Hebrew/Aramaic \#1-\#2) but degenerate mappings. The Voynich statistical signal (U-curve, positional MI, Semitic compatibility) is genuine, but current automatic decryption methods—limited by CharLM trigrams and MCMC search in high-dimensional spaces—are insufficient to convert that signal into readable text.

Notebook: `11_homophonic.ipynb`Results:`homophonic_results.json`

# **Part VIII References**

- Weir, M. et al. (2009). "Password Cracking Using Probabilistic Context-Free Grammars." *Proceedings of the 30th IEEE Symposium on Security and Privacy*pp. 391-405. \[Context on homophonic models in cryptanalysis\]

- Knight, K., Nair, A. y Rathod, N. (2006). "Unsupervised Analysis for Decipherment Problems." *Proceedings of the COLING/ACL 2006*, pp. 499--506.

- Ravi, S. y Knight, K. (2011). "Deciphering Foreign Language." *Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics* (ACL 2011), pp. 12--21.

Notebooks: `11_homophonic.ipynb`Results:`homophonic_results.json`

Parts I-VIII are available as separate documents.


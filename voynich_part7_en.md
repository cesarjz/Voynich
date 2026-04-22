# **PART VII**

# **Decryption validation and grammatical restrictions**

Part VI produced a glyph→character compositional mapping that places Hebrew first with a gap of 11.7 points over non-Semitic languages, an MCMC convergence of 59%, and a many-to-one collapse consistent with the SilPart hypothesis. However, the ranking alone does not prove the mapping correct: a sufficiently powerful optimizer will find*always*a mapping that maximizes verisimilitude under the LM, even if the underlying text is not actually Hebrew. Part VII subjects the compositional mapping to five scoring-independent validation tests (Chapter 19\) and, upon diagnosing degeneration, implements a constrained EM with grammar anchors that attempts to correct the collapse (Chapter 20).

# **Chapter 19\. Validation of the compositional mapping**

## **19.1 Five independent tests**

The validation principle is simple: if compositional mapping captures the actual structure of the Voynich manuscript, the mapped text should exhibit properties that were not directly optimized by the scoring. Five tests are designed, each measuring a different aspect (cells 4-13 of the notebook).`08_validation.ipynb`):

| \# | Test | Ask | Success criteria |
| :---- | :---- | :---- | :---- |
| 1 | Collapse coherence | Do glyphs that collapse into the same character share a positional distribution? | z-score medio \> 0 |
| 2 | N-gram realism | Do the trigrams in the mapped text look more like actual Hebrew than a random shuffle? | Percentile \> 50% |
| 3 | Hebrew roots | Do actual Hebrew triconsonantal roots appear in the mapped text? | Enrichment \> 1.0 con p \< 0.05 |
| 4 | Cardinality | Does the mapping degrade significantly if the cardinality is limited? | Drop \< 5% with reasonable K\_max |
| 5 | Label analysis | Do the labels (short words next to illustrations) behave as expected? | Penalty \< baseline |

## **19.2 Results by test**

### **Test 1: Collapse coherence**

It is evaluated whether the glyphs that collapse into the same Hebrew character share distributional characteristics (frequency, position), or whether the collapse is an artifact of the optimizer (cells 4-5).

| Metric | Value |
| :---- | :---- |
| z-score medio | **\-0.562** |
| Degenerate characters (z \< \-1) | 5 |
| Structured characters (z \> 1\) | 3 |
| Ambiguous characters | 14 |

The three worst characters:

| Character | z-score | N glyphs |
| :---- | :---- | :---- |
| ש (Shin) | \-5.14 | 17 |
| ר (Rain) | \-3.52 | 15 |
| To (Lamed) | \-3.43 | — |

**Verdict: DEGENERATE.**A negative z-score indicates that glyphs grouped under the same character are*less*similar to each other as random glyphs. Shin (z=-5.14) is the worst case: its 17 glyphs do not share a distributional profile, suggesting that the collapse is artificial.

### **Test 2: N-gram realism**

The Jensen-Shannon divergence between the trigrams of the mapped text and those of the native Hebrew is compared against a null distribution of 100 random shuffles from the mapping (cells 6-7).

| Metric | Value |
| :---- | :---- |
| JSD real | 0.753 |
| null JSD(media) | 0.767 |
| Percentile | **24%** |
| Real Entropy | 6.01 bits |
| Zero entropy | 7.86 bits |

**Verdict: FAIL.**The actual mapping has a 24th percentile: worse than 76% of the random shuffles. The entropy of the mapped text (6.01 bits) is lower than that expected under shuffle (7.86 bits), indicating that the mapping collapses the distribution instead of producing text with the n-grammatical diversity of actual Hebrew.

### **Test 3: Hebrew roots**

Actual Hebrew triconsonantal roots (from a reference list) are searched for in the mapped text, and the occurrence rate is compared against random shuffles to calculate the enrichment (cells 8-9).

| Metric | Value |
| :---- | :---- |
| Matches found | 84 |
| Different roots | 6 |
| Enrichment | **84.0×** |

The six roots detected:

| Root | Meaning | Matches |
| :---- | :---- | :---- |
| clay | material/clay | — |
| Did | do | — |
| Send | to send | — |
| audio | listen | — |
| Preserved | keep | — |
| sun | sun/serve | — |

**Verdict: PROMISING but BIASED.**The 84× enrichment is impressive, but 4 of the 6 roots contain ש (shin), the character that attracts 17 glyphs. With 17 glyphs mapped to shin, sequences containing shin are statistically abundant, artificially inflating the detection of roots containing it. The test is contaminated by the degenerate collapse of Test 1\.

### **Test 4: Cardinality restriction**

We assess how much the score worsens if the maximum number of glyphs per character (K\_max) is limited. If the mapping is genuine, the restriction should cause little harm; if it is degenerate, the score will drop significantly (cells 10-11).

| K\_max | Drop and score |
| :---- | :---- |
| 6 | 13.06% |
| 8 | 11.33% |
| 12 | 9.46% |
| **Media** | **11.28%** |

**Verdict: MODERATE.**An 11.3% drop is substantial but not catastrophic. The mapping relies partially on the high-cardinality collapse, but not entirely—there is residual signal even with restriction.

### **Test 5: Label analysis**

The Voynich labels (short words alongside botanical and astronomical illustrations) should behave as a special subsystem: a more limited vocabulary, possibly proper names or classifications. The distribution of the mapped labels is compared against the main text (cells 12-13).

| Metric | Value |
| :---- | :---- |
| N labels | 591 |
| Penalty media | **\-5.717 bits** |
| Average length of labels | 5.22 tokens |
| Average text length | 4.21 tokens |

**Verdict: DIVERGENT.**The mapped tags have a \-5.7 bit penalty compared to the main text, indicating that mapping treats them worse than the main text. Furthermore, the mapped tags are longer (5.22 vs. 4.21 tokens), the opposite of what would be expected if they were short names or classifications.

## **19.3 Consolidated Scorecard**

| \# | Test | Verdict | Interpretation |
| :---- | :---- | :---- | :---- |
| 1 | Collapse coherence | **DEGENERATE** | Artificial, non-distributional collapse |
| 2 | N-gram realism | **FAIL** | Worse than 76% of shuffles |
| 3 | Hebrew roots | **PROMISING**\*\* | High enrichment but contaminated by shin |
| 4 | Cardinality | **MODERATE** | 11.3% drop: partially degenerate |
| 5 | Labels | **DIVERGENCES** | Mapping damages labels |

**Overall verdict: DEGENERATE**(1 positive, 2 marginal, 2 negative).

\*\* The root test result is the only positive one, but it is skewed by shin collapse. If roots containing shin are excluded, the enrichment drops drastically.

## **19.4 Diagnosis: LM dominates, EM collapses**

The five tests converge on a clear diagnosis: the compositional scoring of Part VI, dominated by S\_LM (weight 2.0), allows the optimizer to find a mapping that maximizes likelihood under the CharLM*collapsing*Multiple glyphs within a few high-frequency characters. This collapse improves the score because:

1. The most frequent Hebrew characters (shin, resh, vav) have trigrams well modeled by the CharLM  
2. By channeling many glyphs into these characters, the mapped text is "simplified" into sequences that CharLM scores highly.  
3. But this simplification destroys the real structure: the collapsing glyphs do not share a positional distribution, the resulting n-grams are less diverse than those of actual Hebrew, and the labels get worse.

The problem isn't with the ranking itself—which is informative and robust—but with the specific mapping, which is corrupted. The solution requires additional constraints to prevent uncontrolled collapse.

# **Chapter 20\. EM constrained con grammar anchors**

## **20.1 Three corrections**

Based on the diagnosis in Chapter 19, three corrections to the compositional EM are implemented, each targeting an aspect of the collapse (cells 4-7 of the notebook).`09_constrained_em.ipynb`):

### **Correction 1: K\_max (maximum cardinality)**

The maximum number of glyphs that can map to a single character is limited to K\_max \= 7\. This prevents shin from attracting 17 glyphs and forces the optimizer to distribute the glyphs across more characters. The value K\_max \= 7 is chosen based on Test 4 of the validation: with K\_max between 6 and 8, the drop in score is \~11-13%, a compromise between restriction and quality.

### **Correction 2: Entropy bonus**

A bonus term is added that rewards mappings with a more uniform distribution across the target characters:

**S\_entropy \= w\_entropy × H(glyph distribution per character)**

where H is the Shannon entropy of the distribution of how many glyphs map to each character. High values ​​of H correspond to more uniform distributions (less collapse). Three weights are explored: w\_entropy ∈ {0.1, 0.2, 0.5}.

### **Correction 3: Grammar anchors**

Specific Voynich glyphs are anchored to specific Hebrew characters based on positional knowledge from Parts III-IV. The logic is: if D1 appears in initial position 98.7% of the time, and in Hebrew the prepositional particles (ב be, כ ke, ל le, מ me) and the article (ה ha) almost always appear at the beginning of a word, then D1 should map to one of these characters (cells 4-5).

## **20.2 Grammar Rules STA → Hebrew anchors**

Rules are defined based on the Voynich positional grammar, assigning 12 glyphs to grammatical roles that restrict their set of allowed Hebrew characters:

| Glyph | Rol gramatical | Justification |
| :---- | :---- | :---- |
| D1 | prefix | 98.7% in initial position → Hebrew prepositions/article |
| L1 | prefix | frequent glyph-prefix |
| K1 | classifier | 89.4% in initial position → classifying particles |
| Q1 | root | Most frequent nuclear root |
| Q2 | root | Second most frequent nucleus |
| E1 | root | Nuclear position |
| P2 | root | Nuclear position |
| Z1 | root | Nuclear position |
| Qa | root | Nuclear position |
| F2 | root | Nuclear position |
| A2 | suffix | 83.8% in final position → Hebrew nominal/verbal suffixes |
| C1 | suffix | Frequent final position |

In total, 12 glyphs remain anchored (7.2% of the inventory of 166). The baseline (unconstrained mapping of Part VI) respects only 33% of these rules: 67% of the anchored glyphs map to characters outside their allowed set.

### **Scoring constrained**

The total score is extended with two terms:

**S\_total \= 2.0 × S\_LM \+ 0.5 × S\_pos \+ 0.3 × S\_card \+ w\_entropy × S\_entropy \+ w\_grammar × S\_grammar**

where:

- **S\_card**(weight 0.3): penalty for exceeding K\_max \= 7 glyphs per character  
- **S\_entropy**(w\_entropy variable): bonus for uniform distribution  
- **S\_grammar**(w\_grammar variable): bonus for respecting grammar anchors

## **20.3 Weight sweep (9 configs) \+ MCMC refinamiento**

A sweep is performed on 9 weight configurations (w\_entropy × w\_grammar), combining 3 values ​​from each (cells 9-10):

| w\_entropy | w\_grammar | Score EM | S\_LM | Characters used | Entropy | Grammar |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 0.1 | 0.5 | \-41.48 | \-20.84 | 27 | 0.999 | 0.50 |
| 0.1 | 1.0 | \-43.23 | \-22.15 | 27 | 0.999 | 1.00 |
| 0.1 | 1.5 | \-39.63 | \-20.45 | 27 | 1.000 | 0.67 |
| 0.2 | 0.5 | \-41.38 | \-20.84 | 27 | 0.999 | 0.50 |
| 0.2 | 1.0 | \-42.04 | \-21.75 | 27 | 0.999 | 1.00 |
| 0.2 | 1.5 | \-39.55 | \-20.51 | 27 | 0.999 | 0.67 |
| 0.5 | 0.5 | \-42.63 | \-21.88 | 27 | 0.999 | 1.00 |
| 0.5 | 1.0 | \-42.23 | \-21.91 | 27 | 0.999 | 1.00 |
| **0.5** | **1.5** | **\-39.32** | **\-20.50** | **27** | **1.000** | **0.67** |

The best configuration is**w\_entropy \= 0.5, w\_grammar \= 1.5**with an EM score of \-39.32. All configurations use the 27 Hebrew characters and respect K\_max \= 7\. The entropy of the glyph distribution per character is consistently \~1.0 (close to the maximum), indicating that the three corrections effectively prevent concentrated collapse. Grammar compliance ranges from 0.50 to 1.00, with the w\_grammar \= 1.5 configurations reaching 0.67 (2 out of 3 conditions).

The best EM configuration is refined with MCMC multi-chain (cells 11-13):

| Parameter | Value |
| :---- | :---- |
| Chains | 4 |
| Iterations/string | 10,000 |
| Burn-in | 5,000 |
| Later samples | 4,004 |
| Pesos | w\_lm \= 2.0, w\_pos \= 0.5, w\_card \= 0.3, w\_ent \= 0.5, w\_gram \= 1.5 |
| K\_max | 7 |

## **20.4 Comparison of constrained vs unconstrained**

| Metric | Unconstrained (Parte VI) | Constrained |
| :---- | :---- | :---- |
| Score final | \-39.90 | **\-40.69** |
| Score LM | \-20.10 | \-20.50 |
| PPX mapped | 16.25 | 19.24 |
| Native PPX (Hebrew) | 7.60 | 7.60 |
| Ratio PPX | 2.14 | **2.53** |
| K\_max effective | 17 (shin) | **11** |
| R-hat \< 1.1 | 57.1% | **39.9%** |
| Grammar compliance | 33% | **67%** |

The constrained approach sacrifices LM score and perplexity (CharLM cannot collapse as much) in exchange for a mapping with controlled cardinality (K\_max 17 → 11\) and greater adherence to grammatical constraints (33% → 67%). MCMC convergence worsens (57.1% → 39.9%) because anchors create barriers in the probability space that hinder exploration.

### **High-confidence mappings**

The constrained MCMC produces a set of mappings with posterior confidence 1.0 that are linguistically consistent:

| Glyph | STA function | → Hebrew | Trust | Interpretation |
| :---- | :---- | :---- | :---- | :---- |
| D1 | Prefix (98.7% initial) | (he) | 1.0 | Hebrew definite article |
| J1 | — | To (lamed) | 1.0 | Preposition "a/para" |
| A1 | — | (mem) | 1.0 | Preposition "de/desde" |
| A3 | — | (mem) | 1.0 | Preposition "de/desde" |
| Q1 | Nuclear root | ש (shin) | 1.0 | Frequent root consonant |
| Q2 | Nuclear root | ש (shin) | 1.0 | Frequent root consonant |
| C1 | Suffix (final) | (he) | 1.0 | Feminine/directional suffix |
| C2 | — | (he) | 1.0 | Morphological function |
| B2 | — | (he) | 1.0 | Morphological function |
| G1 | — | ר (cloud) | 0.75 | Frequent consonant |
| K1 | Classifier (89.4% initial) | In (bet) | 0.66 | Preposition "in" |

The cluster D1→ה, J1→ל, A1→מ, K1→ב exactly reproduces the proclitic preposition system of Biblical Hebrew (ב, כ, ל, מ plus the article ה). That this pattern emerges from the MCMC with anchors—without having been directly imposed—is remarkable: the Voynich prefix glyphs map to the most frequent grammatical particles in Hebrew.

The glyphs classified as roots (E1, P2, Z1, Qa, F2) show a bimodal posterior distribution between י (yod) and א (aleph), with a preference for yod (58–83%). This ambiguity may reflect the consonant/vowel duality of the*mothers of reading*in Hebrew.

## **20.5 Re-validation (3 tests)**

Three of the five validation tests from Chapter 19 on constrained mapping (cells 16-18) are re-executed. The results reveal a fundamental tension between morphological structure and sequential fluidity.

### **Revised Test 1: Collapse coherence**

| Metric | Unconstrained | Constrained | Address |
| :---- | :---- | :---- | :---- |
| z-score medio | \-0.562 | **\-0.448** | Partial improvement |
| Degenerate characters (z \< \-1) | 5 | **7** | Regression |
| Structured characters (z \> 1\) | 3 | 1 | Regression |

**Mixed result.**The average z-score improves slightly (-0.562 → \-0.448), indicating that the most extreme collapse (shin with 17 glyphs) has attenuated. However, the number of degenerate characters*increases*From 5 to 7, and the structured ones drop from 3 to 1\. The constraints redistribute the collapse—they prevent extreme concentration but create more areas of moderate degeneration. The constrained mapping is less extreme but not more structured.

### **Revised Test 2: N-gram realism**

| Metric | Unconstrained | Constrained | Address |
| :---- | :---- | :---- | :---- |
| JSD | 0.753 | **0.723** | JSD Improvement |
| Percentile vs. shuffles | 24% | **5%** | **Severe regression** |

**Unexpected negative result.**Although the absolute JSD improves slightly (0.753 → 0.723), the percentile drops drastically from 24% to 5%: the constraint-mapped text looks like*less*real Hebrew at the sequence level is more similar to unrestricted baseline Hebrew. Grammar anchors, by forcing certain glyphs to certain characters, produce trigram sequences that do not occur in natural Hebrew. 95% of random shuffles produce trigrams more similar to Hebrew.

### **Test 3 revised: Hebrew roots — the star result**

| Metric | Unconstrained | Constrained | Address |
| :---- | :---- | :---- | :---- |
| Different roots | 6 | **100** | **Great improvement** |
| Enrichment | 84× | **154×** | **Great improvement** |

**A resounding positive result.**The constrained mapping detects**100 Biblical Hebrew Triconsonantal Roots**compared to only 6 in the baseline, with an enrichment of 154× (compared to 84×). The 100 roots include core vocabulary of Biblical Hebrew:

| Category | Example roots |
| :---- | :---- |
| Existence | To be (ser), to live (vivir), to die (morir) |
| Motion | walked (caminar), came (venir), went out (salir), went down (bajar), went up (subir) |
| Knowledge | Know (conocer), hear (escuchar), see (ver) |
| Action | do (hacer), give (dar), take (tomar), write (escribir) |
| Communication | say (decir), speak (hablar), send (enviar), call (llamar) |
| Natural world | Earth (tierra), water (agua), field (campo), bird (ave), fruit (fruto) |
| Society | King (reinar), priest (sacerdote), house (casa), city (ciudad) |
| Religion | Holy (santo), bless (bendecir), sacrifice (sacrificar), justice (justicia) |

Unlike the unconstrained result, where 4 of the 6 roots contained shin (collapse bias), the 100 roots in the constrained result cover 20+ distinct consonants—the shin bias has been significantly diluted. This result cannot be explained by statistical chance alone: ​​the probability of finding 100 real roots with 154× enrichment in a random mapping is negligible.

## **20.6 The roots vs n-grams paradox**

The three tests reviewed reveal a fundamental tension that deserves analysis:

| Dimension | Unconstrained | Constrained | Interpretation |
| :---- | :---- | :---- | :---- |
| Hebrew roots | 6 (biased) | **100**(various) | Genuine morphological structure |
| N-gram realism | 24th percentile | Percentile**5%** | Fonotaxis doesn't add up |
| Collapse | z \= \-0.56 | z \= \-0.45 | Marginal improvement |
| PPX ratio | 2.14 | 2.53 | Less fluid text |

**The constrained finds more real Hebrew (100 biblical roots) but produces less fluent Hebrew text (5th percentile in n-grams).**This paradox has several possible interpretations:

1. **Non-Hebrew Semitic language.**The underlying language may share Semitic roots with Hebrew (like Aramaic, which has approximately 70% cognate roots) but with different phonotaxis. An Aramaic text mapped through a Hebrew CharLM would produce exactly this pattern: recognizable roots but non-native character sequences.

2. **Additional layer of complexity.**The Voynich writing system may have a layer that the simple compositional model does not capture: transposition, nulls, or contextual encoding that distorts n-grams without destroying the roots.

3. **Unanchored glyphs pollute.**Only 12 of the 166 glyphs are anchored. The remaining \~154 are still optimized by the LM, which tends toward collapse. The resulting text mixes anchored fragments (which produce roots) with free fragments (which produce non-Hebrew n-grams).

## **20.7 Scorecard constrained**

| \# | Dimension | Unconstrained → Constrained | Verdict |
| :---- | :---- | :---- | :---- |
| 1 | Hebrew roots | 6 → 100 roots, 84× → 154× | **IMPROVEMENT** |
| 2 | Cardinality | K\_max 17 → 11 | **IMPROVEMENT** |
| 3 | Grammar compliance | 33% → 67% | **IMPROVEMENT** |
| 4 | Grammatical mappings | Incoherent → D1→ה, J1→ל, A1→מ | **IMPROVEMENT** |
| 5 | N-gram realism | 24th percentile → 5% | **REGRESSION** |

**Overall verdict: IMPROVED**(4 improvements, 1 regression).

The improvement is predominantly morphological: the constrained language finds plausible root structures and grammatical paradigms. The regression is phonotactic: the resulting character sequences are not fluent in Hebrew. This asymmetry—correct morphology, incorrect phonotaxis—is diagnostically valuable because it narrows down the type of system: it is compatible with a Semitic language that shares vocabulary with Hebrew but not necessarily its exact phonotaxis.

## **20.8 Conclusions and next steps**

### **Chapter 20 Conclusions**

1. **Grammar anchors work.**The detection of 100 biblical Hebrew roots (154x enrichment) is the strongest result of the entire decryption pipeline. Grammatical constraints transform a degenerate mapping (6 roots skewed by shin) into a morphologically rich one.

2. **The morphology vs phonotaxis trade-off is real and informative.**Constrained mapping improves in morphological structure (roots, paradigms, prepositions) but worsens in sequential fluency (n-grams, perplexity). This tension suggests that (a) the CharLM trigram is insufficient to capture the actual phonotaxis, (b) the underlying language is not Standard Hebrew but a related Semitic language, or (c) there is an additional encoding layer.

3. **The system of proclitic prepositions emerges spontaneously.**The mappings D1→ה, J1→ל, A1→מ, K1→ב reproduce the most basic grammatical system of Biblical Hebrew without having directly imposed it. This constitutes independent evidence of Semitic compatibility.

4. **MCMC convergence worsens with constraints**(57% → 40%), indicating that the space following anchors is more multimodal. This is to be expected: anchors create barriers that fragment the search space.

5. **The Voynich manuscript has not been deciphered.**The mapped text is not legible Hebrew. The 100 roots and prepositions are promising signs, but the perplexity (2.53× the native level) and the n-graph percentile (5%) indicate that the mapping is far from correct at the sequence level.

### **Next steps**

1. **Arameo as a candidate.**Since mapping produces recognizable Semitic roots but non-Hebrew phonotaxis, Biblical Aramaic and Judeo-Aramaic are natural candidates: they share most of the lexicon with Hebrew but have their own phonotaxis and morphology.

2. **Neural LM.**Replace the CharLM trigram with a neural model (character-level LSTM or Transformer) that captures long dependencies and richer phonotaxis.

3. **Expand linguistic coverage.**Add Romance languages ​​(Italian, Catalan, Occitan) \---historical candidates due to the origin of the manuscript--- and Aramaic.

4. **Visual cribs.**Use the Voynich illustrations to identify anchor words (plant names, astronomical symbols) that restrict mapping beyond positional grammar.

5. **Cross-validation.**Train the mapping on half of the corpus and validate on the other half to detect overfitting.

6. **Alternative transcripts.**Repeat the full analysis with EVA and Currier to verify that the results do not depend on the STA1 2.0 transcript.

# **Chapter 21\. Semantic Analysis by Section and Morphological Reconstruction**

Chapter 20 demonstrated that constrained mapping yields 100 Hebrew roots (154× enrichment) but n-grams worse than the baseline (5th percentile). Before concluding Part VII, we address two complementary questions: (1) Do the detected roots correlate with the thematic content of each section of the Voynich? and (2) Does the mapping produce recognizable Hebrew words with a prefix-root-suffix morphological structure?

## **21.1 Roots per section**

Constrained mapping root matching (with conf\_threshold=0.30, given that the median confidence is 0.155) was applied to each section of the manuscript separately. Results:

| Section | Words | Different roots | Total matches | Top 3 roots |
| :---- | :---- | :---- | :---- | :---- |
| Herbal | 13,777 | 53 | 1,514 | Shemer(650), Shema(386), Emad(113) |
| Astronomical | 1,307 | 100 | 247 | Listen (39), Stand (24), Keep (18) |
| Zodiac | 1,558 | 17 | 159 | Shema(47), Shemer(46), Hamer(14) |
| Biological | 6,661 | 15 | 660 | Shema(385), Shemer(204), Ele(22) |
| Pharmaceutical | 2,444 | 22 | 166 | Shemer(39), Shema(38), Emad(26) |
| Recipes | 10,448 | 28 | 1,469 | Shemer(628), Shema(584), Emad(71) |

Key observation: the same 2-3 roots (שמר, שמע, עמד) dominate in*all*the sections. The astronomical section is anomalous: it matches all 100 roots in only 1,307 words, suggesting greater glyph diversity but not semantic specificity.

## **21.2 Semantic correlation: category × section**

Five semantic categories were defined a priori with manually assigned HEBREW\_ROOTS roots:

- **Botany/Nature**(10 roots): fruit, field, chicken, sheep, leaf, camel, horse, bird, oil, wine  
- **Astronomy/Time**(6): Day, Sun, Night, New Year, Year, Wind  
- **Body/biology**(9): soul, flesh, bone, foot, head, eye, womb, animal, blood  
- **Religion/ritual**(7): Holy, priest, sacrifice, pure, impure, blessed, righteous  
- **Society/material**(8): King, house, city, money, gold, stone, tool, book

The enrichment (freq\_section / freq\_global) was calculated for each category × section pair, and a global chi-square test was performed.

**Chi² \= 64.21, p \= 1.56×10⁻⁶, dof \= 20**— significant association.

Expected correspondences (section ↔ semantic category):

| Section | Expected category | Enrichment | It fulfills |
| :---- | :---- | :---- | :---- |
| Herbal | Botany/Nature | 1.073 | ✓ (marginal) |
| Astronomical | Astronomy/Time | 3.635 | ✓ |
| Zodiac | Astronomy/Time | 2.033 | ✓ |
| Biological | Body/biology | 0.209 | ✗ |
| Pharmaceutical | Religion/ritual | 0.000 | ✗ |
| Recipes | Society/material | 1.130 | ✓ (marginal) |

**Result: 4/6 matches are met**, but the chi² signal comes mainly from the asymmetry in root diversity (the astronomical section matches the 100 roots with enrichment \>3 in*all*the categories). The biological and pharmaceutical sections do not show the expected thematic specificity.

## **21.3 Morphological Reconstruction**

The 200 most frequent words (47.1% of the corpus) were analyzed by breaking each one down into proclitic prefix \+ triconsonantal root \+ suffix:

| Category | Number of words | % |
| :---- | :---- | :---- |
| Morphology only (prefix/suffix without root) | 171 | 85.5% |
| Complete (prefix \+ root \+ suffix) | 15 | 7.5% |
| Not recognizable | 9 | 4.5% |
| Partial root (root without affixes) | 5 | 2.5% |

85.5% of "morphology only" is explained by the many-to-one degeneration of the mapping: 7 glyphs map to מ and 6 to ה, so almost every word "starts with a prefix" or "ends with a suffix" by construction, without this reflecting actual morphology.

## **21.4 Frequency of grammatical particles**

The frequency of grammatical particles as prefixes (word-initial position) was compared with the frequencies in actual biblical Hebrew:

| Particle | Voynich mapped | Biblical Hebrew | Within the range |
| :---- | :---- | :---- | :---- |
| ה (article) | 22.7% | 15-18% | ✗ |
| (a/para) | 1.0% | 5-7% | ✗ |
| In (en) | 23.7% | 4-6% | ✗ |
| From (de) | 28.1% | 3-5% | ✗ |
| (like) | 0.2% | 1-2% | ✗ |

**Result: 0/5 particles within range.**The frequencies of ב (23.7%) and מ (28.1%) are 4-6× higher than expected, a direct consequence of degeneration: multiple frequent glyphs map to the same consonant.

## **21.5 Chapter 21 Conclusions**

1. **The semantic correlation exists but is weak.**The chi² value is significant (p \< 10⁻⁶), and 4/6 section-theme correspondences are met. However, the signal comes from the uneven distribution of root diversity among sections, not from genuine thematic specificity.

2. **The morphology is not consistent with biblical Hebrew.**85.5% of the words show "morphology" only due to many-to-one collapse, not due to actual linguistic structure. The frequencies of grammatical particles are completely out of range (0/5).

3. **The diagnosis of degeneration is confirmed in a third dimension.**The validation of Chapter 19 (scorecard 1+/1±/3−), the re-validation of Chapter 20 (roots++ but n-grams−−), and now the semantic-morphological analysis all point to the same conclusion: mapping captures superficial correlations (roots, chi²) but does not produce actual Hebrew text at the morphosyntactic level.

4. **Implication for Aramaic.**The results do not rule out a Semitic language: the emerging roots are genuinely Semitic, but the phonotaxis and morphology do not correspond to Hebrew. This reinforces the hypothesis that the underlying language could be Aramaic or another Semitic language with cognate vocabulary but a different distribution.

Notebook: `10_semantic.ipynb`Results:`semantic_results.json`

# **Part VII References**

- Gelman, A. y Rubin, D. B. (1992). "Inference from Iterative Simulation Using Multiple Sequences." *Statistical Science* 7(4): 457--472.

- Ravi, S. y Knight, K. (2011). "Deciphering Foreign Language." *Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics* (ACL 2011), pp. 12--21.

Notebooks: `08_validation.ipynb` · `09_constrained_em.ipynb` · `10_semantic.ipynb`Results:`validation_results.json` · `constrained_results.json` · `semantic_results.json`

Parts I-VII are available as separate documents.


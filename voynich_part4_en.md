# **PART IV**

# **From forward modeling to decipherment: syllabic segmentation of the Voynich**

Part III established, through eleven generative models, that the SilPart model (probabilistic syllabary with glyph partitioning, d=0.445) best reproduces the statistical footprint of the Voynich script. This result identifies the*type*of the system, but it doesn't say how to read it. Part IV takes the next step: under the syllabic hypothesis, segmenting the Voynich words into syllables, classifying them functionally, detecting internal morphological patterns, and validating the results against real agglutinative languages. The analysis implements the first four computational phases of syllabic decipherment.

# **Chapter 16\. Segmentation and syllabic analysis**

## **16.1 Phase 1: Syllabic segmentation**

### **Method**

Two complementary segmentation methods are implemented, both operating on the intra-word transition matrix (which only counts bigrams within each word, without crossing boundaries):

**Method A — Transition Probability (TP).**It marks a syllable boundary where P(g\_{i+1} | g\_i) falls below a corpus percentile. Inspired by Saffran et al. (1996), who showed that humans use transitional probability drops to segment continuous speech into words. Here, the principle is adapted to syllable boundaries within words. Three thresholds are evaluated: the 10th, 20th, and 30th percentiles.

**Method B — Forward entropy.**It marks a boundary where the entropy H(g\_{i+1} | g\_i) is high—that is, where the current glyph has many possible successors with similar probability. Inspired by Harris (1955), who proposed that points of maximum uncertainty in a sequence correspond to morphological boundaries, three thresholds are evaluated: the top 60%, 70%, and 80% of the entropy distribution.

### **Parameter sweep results**

| Method | Parameter | Syllable types | Syl/word |
| :---- | :---- | :---- | :---- |
| A (TP) | P10 | 5,511 | 1.32 |
| A (TP) | P20 | 2,923 | 1.64 |
| A (TP) | P30 | 1,473 | 1.97 |
| B (Entropy) | Top-60% | 462 | 3.66 |
| B (Entropy) | Top-70% | 623 | 3.51 |
| B (Entropy) | Top-80% | 996 | 3.29 |

The two methods capture different levels of structure. Method A produces longer and fewer syllables per word (1.64 syl/word with P20): it segments into morpheme-like units, grouping roots and affixes into blocks. Method B produces shorter and more abundant syllables (3.51 syl/word with Top-70%): it segments more finely, into units closer to phonological syllables.

The one selected**Method A with P20 as canonical**producing an inventory of 2,923 syllabic types.

### **Inventory interpretation**

The raw number of 2,923 types is far greater than any known syllabary (kana=46, Linear B=87, Cherokee=85). However, the frequency distribution is extremely concentrated:

- **40 types**They cover 50% of the tokens  
- **201 types**They cover 80%  
- **794 types**They cover 95%

He *functional core*The inventory has approximately 200 syllables, comparable to an Aksharic system (Devanagari has approximately 300+). The remaining approximately 2,100 types are rare combinations or hapax legomena—exactly as expected in an agglutinative language where infrequent roots generate unique combinations. The Zipf distribution of syllables follows a power law with a slope of α \= \-1.47, consistent with actual linguistic units.

### **Agreement between methods**

The Spearman correlation between the number of boundaries per word for both methods is ρ=0.228 (p≈0), with an exact agreement of 13.6%. This divergence is not a flaw: it reflects that they capture different levels of structure. However, 23 of the 50 most frequent syllables for each method coincide, indicating that the core of the inventory is robust.

The 10 most frequent types of canonical inventory are:

| Range | Syllable | Freq | % |
| :---- | :---- | :---- | :---- |
| 1 | A2 | 2,027 | 3.3% |
| 2 | K1 | 2,010 | 3.3% |
| 3 | B1-A2 | 1,933 | 3.2% |
| 4 | A1 | 1,885 | 3.1% |
| 5 | C2 | 1,556 | 2.6% |
| 6 | B1 | 1,528 | 2.5% |
| 7 | A1-B2 | 1,269 | 2.1% |
| 8 | B1-A3-G1 | 1,047 | 1.7% |
| 9 | B3 | 957 | 1.6% |
| 10 | L1 | 892 | 1.5% |

\!\[Figure 16.1. Zipf distribution and comparison of syllabic inventories. syllables\_zipf\_inventory.png)

*Figure 16.1. Top panel: Zipf distribution for the three thresholds of each method. Bottom left panel: distribution of syllable lengths. Bottom right panel: comparative table with actual syllabaries.*

## **16.2 Phase 2: Functional classification of syllables**

### **Method**

Each syllable type with a frequency ≥ 5 is classified according to its positional distribution within the word:

- **Onset**(prefix): occurrence ratio in initial position ≥ 0.60, with final ratio \< 0.30  
- **Coda**(suffix): occurrence ratio in final position ≥ 0.60, with initial ratio \< 0.30  
- **Nuclear**(root): mid-position occurrence ratio ≥ 0.40  
- **Free**: without dominant positional preference

### **Results**

Of the 2,923 types in the inventory, 792 exceed the minimum frequency threshold (5 tokens) and receive a classification:

| Class | Types | Tokens | Interpretation |
| :---- | :---- | :---- | :---- |
| Onset | 171 | 14,368 | Syllabic prefixes |
| Nuclear | 54 | 3,781 | Roots |
| Coda | 90 | 12,555 | Syllabic suffixes |
| Free | 477 | 27,099 | No positional preference |

The category*free*It dominates in types (477), which is to be expected: many combinations do not show a clear positional preference, especially those that appear in one- or two-syllable words where the beginning/end positions are confused.

### **Validation: glyph → syllable connection**

If the segmentation is correct, onset syllables should begin with known prefix glyphs (D1, K1, L1) and codas should end with known suffix glyphs (G1, A2, C1). The results partially confirm this prediction:

| Class | Criterion | Coincidence | Dominant glyph |
| :---- | :---- | :---- | :---- |
| Coda | It ends in a glyph-suffix | **64.4%** (58/90) | A2 (41 types) |
| Nuclear | It contains a glyph-core | 31.5% (17/54) | A3 (13 types) |
| Onset | It begins with a glyph-prefix | 26.3% (45/171) | A1 (40 types) |

The connection is stronger for codas: 64.4% end in suffix glyphs, with A2 overwhelmingly dominating. This is consistent with the prior knowledge that A2 appears in final position in 83.8% of its occurrences. On the onset side, although the overall percentage is lower (26.3%), the individual cases are compelling: the D1-A1 type appears in initial position in 98.6% of its occurrences, K1 in 89.4%, and D1-A1-Q1 in 98.8%.

The class × section heatmap shows stable onset/nuclear/coda ratios between thematic sections, suggesting that morphological structure is shared between sections of the manuscript—thematic differences lie in the lexicon (which roots are used), not in the grammar (how words are constructed).

\!\[Figure 16.2. Zipf distribution by functional class. syllables\_zipf\_by\_class.png)

*Figure 16.2. Zipf distribution for each functional class. The four classes follow power laws with different slopes, consistent with real linguistic distributions.*

\!\[Figure 16.3. Syllable class proportion per section. syllables\_class\_per\_section.png)

*Figure 16.3. Heatmap of syllable class proportions by thematic section. The morphological structure is shared between sections.*

## **16.3 Phase 3: Morphological patterns**

### **16.3.1 Vocal Harmony**

If Voynich has internal phonological restrictions analogous to the vowel harmony of Turkish or Finnish, there should be a preferential association between nuclear syllables and codas within the same word. To test this, all co-occurring (nuclear, coda) pairs within each word are extracted, a top-20 × top-20 contingency table is constructed, and a chi-square test with permutation validation (500 coda shuffles between words) is applied.

**Results:**

| Statistical | Value |
| :---- | :---- |
| Pairs analyzed | 2,062 |
| χ² observed | 3,170.7 |
| p-value (χ²) | ≈ 0 |
| p-value (permutation) | 0.000 (0/500 shuffles ≥ observed) |
| V de Cramer | 0.284 |

The nuclear-coda association is highly significant: none of the 500 permutations produces a χ² value comparable to the observed one. Cramér's V of 0.284 indicates a moderate effect—not as strong as full Turkish vowel harmony, but clearly not random. This suggests internal restrictions on which suffixes can follow which roots, consistent with partial vowel harmony, phonotactic restrictions, or some other type of morphophonological dependence.

\!\[Figure 16.4. Nuclear contingency table × coda. nuclear\_harmony\_coda.png)

*Figure 16.4. Heatmap of the contingency table between the 15 most frequent nuclear syllables and the 15 most frequent coda syllables. The co-occurrence peaks (dark cells) indicate preferred associations that are not explained by the marginal frequencies.*

### **16.3.2 Suffix paradigms**

For each nuclear root with frequency ≥ 10, all co-occurring coda suffixes (frequency ≥ 5\) are cataloged. Regularity is measured by the mean Gini index (1.0 \= a single dominant suffix, 0.0 \= equally likely).

**Results:**

| Metric | Value |
| :---- | :---- |
| Paradigms found | 27 |
| Average paradigm size | 3.4 suffixes |
| Maximum size | 8 suffixes |
| Average regularity (Gini) | 0.490 |

The Gini coefficient of 0.49 is somewhere in between: neither completely regular (a single suffix per root) nor equiprobable. This is consistent with an agglutinative system where a few endings are very frequent but there is real variety.

The three most productive roots are:

| Root | N suffixes | Total tokens | Dominant suffix |
| :---- | :---- | :---- | :---- |
| Q1 | 8 | 290 | A2 (70.3%) |
| K2 | 8 | 214 | C2 (47.7%) |
| Q2 | 6 | 128 | A2 (75.0%) |

The root Q1—which coincides with one of the most frequent core glyphs in Voynich—admits 8 different suffixes, with A2 as the dominant ending (204/290 \= 70.3%). This is analogous to a Turkish nominal root that admits multiple case suffixes but with the nominative (without suffix/null suffix) as the base form.

\!\[Figure 16.5. Bipartite graph root → suffixes. paradigms\_suffixes\_graph.png)

*Figure 16.5. Bipartite network of the 20 most productive roots (green) and their coda suffixes (yellow). The thickness of the edges is proportional to the frequency of co-occurrence.*

### **16.3.3 Vocabulary by section**

The specificity of nuclear syllables per section is measured as freq\_in\_section / (freq\_in\_section \+ mean\_freq\_others). If the Voynich manuscript contains actual thematic content, the sections should exhibit specific root syllables.

The results show differentiated core vocabulary: the biological section has specific syllables such as Q2 (specificity=0.617) and Ba (0.613), while the pharmaceutical section has Z1 (0.814) and J1-A1 (0.769). Each section presents a distinct core profile, consistent with thematic content.

### **16.3.4 Divergence between sections**

The average Jensen-Shannon (JSD) divergence between sections at the syllabic level is**0.204**, lower than the JSD at the glyph level (0.301). The syllable/glyph ratio is 0.68×.

This result—counterintuitive at first glance—has a coherent interpretation: by grouping glyphs into syllables, glyph-to-glyph variation that was "positional noise" is absorbed, and the syllabic distribution is partially homogenized. The sections share more syllabic vocabulary than vocabulary of individual glyphs. This does not contradict the thematic content hypothesis: the variation between sections lies in which root words are used (lexicon), but the morphology (onset \+ coda) is shared. In fact, this pattern is exactly what would be expected in a real language: grammar is universal within the text, variation is lexical.

\!\[Figure 16.6. JSD between sections at the syllabic level. jsd\_syllabic\_sections.png)

*Figure 16.6. Pairwise JSD heatmap between thematic sections at the syllabic level.*

## **16.4 Phase 4: Interlinguistic comparison**

### **Method**

The same TP segmentation with P20 is applied to character corpora of Turkish (Leipzig Wikipedia, subsampled to 37,087 words) and Finnish (Kalevala, subsampled to 37,087 words), treating each character as a "glyph" to obtain comparable metrics.

### **Comparative syllabic metrics**

| Language | Types | Syl/word | Zipf a | Distance to the Voynich |
| :---- | :---- | :---- | :---- | :---- |
| Voynich | 2,923 | 1.64 | \-1.47 | — |
| Turkish | 8,328 | 2.05 | \-1.14 | 1.060 |
| Finnish | 7,173 | 2.11 | \-1.21 | 0.995 |

Voynich has fewer word types and fewer syllables per word than both languages, but the Zipf slope is steeper (-1.47 vs. \-1.14/-1.21), indicating a distribution more concentrated in a few dominant syllables. Syllable distance is comparable for both languages, with Finnish slightly closer (0.995 vs. 1.060).

The difference in the number of characters (2,923 vs. 7,000-8,000) reflects that Voynich uses 166 base glyphs compared to the 29-30 characters of the Turkish and Finnish alphabets. With a smaller alphabet but with glyphs that already encode syllabic information, the effective combinatorial space is different.

### **Mutual positional information: the most revealing result**

| Language | MY glyph | MY syllable | Amplification |
| :---- | :---- | :---- | :---- |
| Voynich | 0.658 | 0.608 | 0.92× |
| Turkish | 0.164 | 0.752 | 4.59× |
| Finnish | 0.197 | 0.830 | 4.20× |

In Turkish and Finnish, positional MI is amplified approximately 4× when moving from individual characters to syllables. Individual letters have little positional preference, but syllables do—as expected in any language with morphology.

In the Voynich,**there is no amplification**(0.92× ratio). Glyphs already encode as much positional information as the resulting syllables. This has a profound implication:**The Voynich glyphs are already high-level functional units, not simple letters that are added together in syllables.**Glyph D1, with 98.7% in the initial position, already functions as an onset marker. Glyph G1, with 96.9% in the final position, already functions as a coda marker. TP segmentation is grouping these glyphs into larger (morpheme-like) units, but the positional information was already encoded at the individual glyph level.

This result connects directly with the deficit in positional MI of the SilPart model (MI\_pos=0.477 vs. 0.658 of the Voynich model, noted in Chapter 14): the actual Voynich mechanism has more rigid glyph-position dependencies than those produced by the SilPart model, possibly because the glyphs do not represent phonemes that are aggregated into syllables, but rather each glyph already*is*a syllabic or morphosyllabic unit.

\!\[Figure 16.7. Multilingual syllable comparison. multilingual\_syllable\_comparison.png)

*Figure 16.7. Syllabic comparison between Voynich, Turkish, and Finnish. Left: Zipf distribution. Center: comparative metrics. Right: summary table with distances.*

## **16.5 Synthesis and implications**

The four analyses converge on a coherent diagnosis:

**1\. Plausible syllabic inventory.**The Voynich script has a functional core of approximately 200 syllable types, with 40 types covering 50% of the tokens. This is compatible with a large Aksharic-type syllabary, not with a phonemic alphabet or a simple kana-type syllabary.

**2\. Morphological structure onset-nuclear-coda.**Positional classification produces three distinct functional classes, with a direct and verifiable connection between known prefix glyphs (D1, K1) → onset syllables, and known suffix glyphs (A2, C1, G1) → coda syllables. Morphology is shared between sections; thematic variation is lexical.

**3\. Internal morphophonological restrictions.**The nuclear-coda association (V=0.284, p≈0) demonstrates that root-suffix combinations are not free: there are internal restrictions compatible with partial vowel harmony or phonotaxis. The suffix paradigms (27 productive roots, Gini=0.49) show a system with real variety but a dominance of a few endings.

**4\. Glyphs are already syllabic units.**The absence of positional MI amplification (0.92×) when moving from glyphs to syllables—compared to \~4× in Turkish and Finnish—indicates that the Voynich glyphs already encode syllabic-level information. This does not mean that segmentation is useless: on the contrary, segmented syllables reveal morphological paradigms that individual glyphs do not exhibit. But it does mean that the basic unit of the system is the glyph-syllable, not the glyph-phoneme.

### **Implications for decryption**

These results narrow down the possibilities for future decryption attempts:

- Any proposal must be compatible with an effective inventory of \~200 functional units  
- The positional dependencies of glyphs are not an artifact: they are an intrinsic property of the system  
- The underlying language (if any) should have vowel harmony or other morphophonological constraint that produces V ≈ 0.28 in root-suffix combinations  
- The most promising attack vector is the identification of suffix paradigms: with 27 productive roots and their cataloged suffixes, there is a system of constraints exploitable by Bayesian decryption methods (like Ravi and Knight, 2011\) operating at the syllable level instead of the character level

**Note (outcome of Part V)**Bayesian decryption at the syllable level (1-to-1 substitution) produces a robust ranking (Hebrew \#1, Arabic \#2) but very low subsequent confidence (R-hat \< 1.1 only in 7% of syllables), suggesting that the Voynich encoding is not substitutional but compositional.

**Note (result of compositional decipherment)**Glyph-to-character decryption independently confirms the syllabic ranking (Hebrew \#1, Arabic \#2) with even greater discrimination: a Semitic-to-non-Semitic gap of 11.7 points (vs. 2.9 in the syllabic approach). MCMC convergence improves dramatically (R-hat \< 1.1 in 59% of glyphs vs. 7% of syllables), with 18 glyphs mapped with 100% post-hoc confidence. The mapped/native PPX ratio drops from 4.23 to 2.07 for Hebrew. The results suggest that multiple glyphs encode the same Hebrew consonant in different positional contexts (e.g., ש attracts 17 glyphs, ר 15), consistent with the SilPart hypothesis of compositional slot encoding.

### **Limitations**

1. **Segmentation without phonological awareness**The TP and entropy methods are purely statistical; they do not incorporate knowledge about the phonetic properties of the glyphs  
2. **arbitrary P20 percentile**The choice of threshold significantly affects the inventory size; the results should be interpreted as conditional on this choice, although the parameter sweep shows that the qualitative conclusions are robust.  
3. **Limited Corpus**\~37K words is sufficient for robust statistics at the frequency level, but it limits the analysis of rare combinations and low-frequency paradigms.  
4. **Simplified positional classification**The 0.60 threshold for onset/coda is heuristic; a Bayesian approach with informative priors would be more rigorous.

## **16.6 Future work**

1. **~~SilPart-aware compositional decryption~~**Completed. Glyph-to-character mapping (many-to-one, 166 glyphs → \~27-28 characters) using CharLM trigram and MCMC multi-chain. Confirms syllabic ranking (Hebrew \#1, Arabic \#2) with greater discrimination (gap 11.7 pts) and better convergence (59% R-hat \< 1.1). 18 glyphs with 100% post-hoc confidence  
2. **Phonemic Monte Carlo**: explore random assignments of phonemes to glyphs and evaluate which ones produce plausible phonologies according to the detected morphophonological constraints  
3. **~~Bayesian decryption at the syllable level~~**Completed in Part V. The ranking (Hebrew \#1) is robust but confidence is low, motivating the compositional approach of point 1  
4. **Cross with images**: correlate section-specific syllabic vocabulary with the visual content of the illustrations to identify potential cribs  
5. **Cross-validation**: repeat the analysis with alternative transcripts (EVA, Currier) to verify the robustness of the results

# **Part IV References**

- Harris, Z. S. (1955). "From Phoneme to Morpheme." *Language* 31(2): 190--222.

- Ravi, S. y Knight, K. (2011). "Deciphering Foreign Language." *Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics* (ACL 2011), pp. 12--21.

- Saffran, J. R., Aslin, R. N. and Newport, E. L. (1996). "Statistical Learning by 8-Month-Old Infants." *Science* 274(5294): 1926--1928.

Parts I, II, III and IV are available as separate documents.


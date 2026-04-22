# **PART VI**

# **Compositional decipherment of the Voynich**

Part V attempted to decipher Voynich using bijective substitution at the syllable level: each Voynich syllable is mapped to exactly one syllable of the candidate language. The resulting ranking—Hebrew \#1, Arabic \#2, with a gap of 2.9 points to the non-Semitic languages—is informative, but MCMC convergence is extremely limited (R-hat \< 1.1 in only 7% of the syllables). This result suggests that the 1-to-1 substitution assumption is incorrect: if the SilPart model from Part III is correct, each Voynich glyph encodes an independent phonological component (onset, nucleus, or coda), and the correct unit of decipherment is not the syllable but the glyph. Part VI implements this level shift: a compositional decipherment where each glyph maps to a character of the candidate language, allowing many-to-one mappings (multiple glyphs → same character).

# **Chapter 18\. Compositional Deciphering**

## **18.1 Motivation: from syllable to glyph**

The Voynich script has 166 distinct glyphs that combine into 2,923 syllable types. If the encoding is compositional—as predicted by SilPart—then the 166 glyphs map to a target alphabet of \~27–30 characters, producing a many-to-one mapping where multiple glyphs can encode the same character in different positional contexts.

The computational advantage is dramatic: the search space shrinks from \~800\! bijective permutations (syllabic) to 166 × 30 independent assignments (compositional). This not only makes the search more efficient but also allows the MCMC to converge because the space is navigable. Furthermore, the many-to-one mapping directly captures SilPart's core prediction: that the same phoneme is encoded with different glyphs depending on its position in the syllable (cell 0 of the notebook).`07_compositional.ipynb`).

## **18.2 Model: CharLM trigram, GlyphMappingState, C/V classification**

### **Character Language Model (CharLM)**

Unlike the SyllableLM bigram in Part V, here a character-level language model with trigram order and Witten-Bell smoothing is used (cell 4):

P(c\_i | c\_{i-2}, c\_{i-1}) \= λ₃ × P\_trigram \+ (1-λ₃) × \[λ₂ × P\_bigram \+ (1-λ₂) × P\_unigram\]

where each level of backoff has its own Witten-Bell calibrated λ. The trigram captures richer dependencies than the syllabic bigram: not only which character follows which, but three-character patterns that reflect the phonotaxis of the language.

### **Mapping state (GlyphMappingState)**

The class`GlyphMappingState`manages a many-to-one mapping of glyphs to characters (cell 4):

- `apply_word()`: given a mapping μ, transforms a word \[g₁, g₂, ..., g\_n\] → \[c₁, c₂, ..., c\_n\] where c\_i \= μ(g\_i)  
- `propose_change()`: Changes a random glyph to a random character, respecting C/V constraints  
- It does not require bijection: multiple glyphs can map to the same target character

### **Consonant/Vowel Classification (C/V)**

Each glyph is classified as a consonant (C) or vowel (V) according to its positional distribution in the syllables of Part IV (cell 7):

- **V (vocal)**: glyphs with a ratio in the nuclear position \> 0.40  
- **C (consonant)**: remaining classifiable glyphs

Qualifying results:

| Class | N glyphs |
| :---- | :---- |
| Consonant (C) | 21 |
| Vocal (V) | 5 |
| Unclassified | 91 |
| **Total classified** | **117 of 166** |

The V/(C+V) ratio is 19.2%, consistent with the vowel/consonant ratio of Hebrew (5/22 \= 22.7%) and Arabic (6/28 \= 21.4%), where the writing systems are predominantly consonantal.

### **Compositional scoring**

The score combines two components (cell 4):

**S\_total \= 2.0 × S\_LM \+ 0.5 × S\_positional**

where:

- **S\_LM**(weight 2.0): average log-likelihood of the corpus mapped under the CharLM trigram of the candidate language  
- **S\_positional**(weight 0.5): consistency between the C/V role of the glyph and the C/V role of the target character

## **18.3 Initialization by frequency within class C/V**

Unlike the Hungarian initialization of the syllabic approach (which requires distributional vectors and bijective assignment), a more direct frequency-based initialization is used here (cell 9):

1. Calculate the frequency of each glyph in the Voynich corpus  
2. Calculate the frequency of each character in the corpus of the candidate language  
3. For each class (C, V, unclassified):  
   - Order glyphs by descending frequency  
   - Sort target characters by descending frequency  
   - Assign the most frequent glyph to the most frequent character of the same class  
4. Cyclic assignment: glyph\_i → char\_(i % n\_chars) to ensure coverage

Initial scores after initialization:

| Language | Initial score | S\_LM |
| :---- | :---- | :---- |
| Arabic | \-65.31 | \-32.90 |
| Hebrew | \-74.06 | \-37.28 |
| Turkish | \-86.28 | \-43.39 |
| Latin | \-96.09 | \-48.29 |
| Finnish | \-111.06 | \-55.78 |

## **18.4 EM compositional \+ MCMC multi-chain**

### **Phase EM**

Up to 100 EM iterations are performed per language (cell 11):

| Parameter | Value |
| :---- | :---- |
| Maximum iterations | 100 |
| Early stopping | 10 iterations with no improvement |
| Changes per iteration | 200 |
| Subsample by iteration | 3,000 words |
| Proposal | Change a glyph to another character (respecting C/V) |
| Acceptance | Metropolis: always if it improves, probabilistic if it worsens |

### **Fase MCMC**

For the top-2 EM languages, MCMC Metropolis-Hastings is run with adaptive annealing (cell 12):

| Parameter | Value |
| :---- | :---- |
| Chains | 4 (seeds: 42, 137, 256, 999\) |
| Iterations/string | 15,000 |
| Burn-in | 3,000 |
| Thinning | Every 5th sample |
| Target acceptance rate | 35% |
| Subsample/iter | 3,000 words |
| Pesos | w\_lm \= 2.0, w\_pos \= 0.5 |
| Temperature | Adaptive annealing: calibrated T₀, exponential decay |

The temperature is empirically calibrated by measuring the distribution of negative scores and adjusting T₀ to obtain \~35% initial acceptance. Exponential annealing gradually reduces T, focusing the scan towards the end.

## **18.5 Results: ranking confirms Hebrew \#1**

The final ranking (cell 16), now with six candidate languages ​​including Aramaic (Targum Onkelos):

| \# | Language | Family | Score total | Score LM | PPX mapped | Native PPX | Ratio PPX |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 1 | **Hebrew** | Semitic | **\-39.71** | \-20.10 | 15.1 | 7.3 | **2.07** |
| 2 | **Arabic** | Semitic | **\-40.95** | \-20.73 | 16.5 | 7.3 | **2.26** |
| 3 | **Aramaic** | Semitic | \-43.58 | \-22.04 | 19.4 | 7.4 | 2.63 |
| 4 | Latin | Indo-European | \-52.65 | \-26.58 | 36.3 | 5.7 | 6.42 |
| 5 | Turkish | Binder | \-61.99 | \-31.24 | 67.4 | 7.9 | 8.50 |
| 6 | Finnish | Binder | \-75.88 | \-38.19 | 173.4 | 7.4 | 23.50 |

Note: MCMC was only run on the top two (Hebrew and Arabic). The Aramaic score is post-EM, not refined by MCMC.

### **Interpretation**

The compositional ranking independently confirms the syllabic result of Part V:**Hebrew \#1, Arabic \#2, Aramaic \#3**But the discrimination is radically greater and reveals an important difference with respect to the syllabic level:

- **Semitic → non-Semitic gap:**11.7 points (Hebrew \-39.71 vs Latin \-52.65), compared to only 3.5 points in the syllabic model. The compositional model separates the Semitic languages ​​from the rest much more clearly.

- **Aramaic text from \#3:**At the syllabic level, Aramaic and Hebrew were virtually indistinguishable (gap 0.27). At the compositional level, the gap widens to 3.87 points. The Hebrew trigram CharLM fits the Voynich character sequences significantly better than Aramaic. This suggests that, at the level of character phonotaxis (not syllable phonotaxis), Voynich is more similar to Hebrew than to Aramaic.

- **Ratio PPX:**For Hebrew, the mapped corpus has 2.07 times the perplexity of native Hebrew, compared to 2.63 times for Aramaic and 4.00 times for syllabic. Compositional mapping produces text closer to actual Hebrew.

- **Reordering of non-Semitic languages:**Latin rises from \#5 (syllabic) to \#4 (compositional), and Finnish falls from \#4 to \#6. The compositional model, by operating at the character level, discriminates differently between lower-level languages—but the top 2 remains stable.

## **18.6 Convergence: drastic improvement compared to the syllabic**

MCMC diagnostics show a dramatic improvement in convergence (cells 13-14):

### **Hebrew**

| Metric | Syllabic (Part V) | Compositional |
| :---- | :---- | :---- |
| R-hat \< 1.1 | 45/676 (6.65%) | **98/165 (59.4%)** |
| R-hat mediana | 1.521 | **1.041** |
| Average acceptance | 30.8% | **69.0%** |

### **Arabic**

| Metric | Syllabic (Part V) | Compositional |
| :---- | :---- | :---- |
| R-hat \< 1.1 | 44/715 (6.15%) | **94/163 (57.7%)** |
| R-hat mediana | 1.511 | **1.056** |
| Average acceptance | 31.7% | **68.1%** |

The proportion of converged glyphs (R-hat \< 1.1) increases from \~7% to \~59%: a \~9× improvement that directly reflects the reduction in search space. The median R-hat value decreases from \~1.52 to \~1.04, approaching the ideal (1.0). Acceptance rates (\~69%) are higher than in syllabic language (\~31%), indicating that strings efficiently explore the backspace.

### **High-confidence mappings**

For Hebrew, 75 glyphs have 100% back C/V consistency (the assigned character always has the same C/V role across all four strings). Of these, 18 glyphs have back confidence 1.0—all four strings converge to exactly the same Hebrew character—constituting strong anchors for the mapping.

## **18.7 Analysis of the many-to-one collapse**

A central prediction of the SilPart model is that multiple Voynich glyphs encode the same phoneme in different positional contexts. Compositional mapping confirms this prediction: the most frequent Hebrew characters attract multiple glyphs (cell 18).

### **Top 10 Hebrew Attractors**

| Character | Name | N glyphs mapped | % of total |
| :---- | :---- | :---- | :---- |
| that | Shin | 17 | 10.2% |
| R | Resh | 15 | 9.0% |
| and | Vav | 13 | 7.8% |
| A | Ayin | 10 | 6.0% |
| from | Mem | 9 | 5.4% |
| T | Side | 9 | 5.4% |
| H | It | 9 | 5.4% |
| A | Aleph | 8 | 4.8% |
| Property | Now finally | 7 | 4.2% |
| about | Purchase | 7 | 4.2% |

The three main attractors (Shin, Resh, Vav) account for 45/166 \= 27.1% of all glyphs. This is consistent with SilPart: frequent consonants like ש and ר appear in many positional contexts (onset, coda, with different adjacent vowels), and each positional context has its own glyph.*mothers of reading*(ו vav, א alef) \---consonants that also function as vowel indicators in Hebrew--- attract many glyphs, reflecting their dual consonant/vowel role.

### **Linguistic interpretation**

The many-to-one collapse is qualitatively compatible with a system where:

- Each Hebrew consonant has graphic variants depending on its position in the syllable (onset vs coda)  
- Las vowes se codifican combinatoriamente mediante la elección de varia consonántica, no mediante signos diacríticos separar (como los nikkud del hebreo estandar)  
- The result is an Aksharic-type system where the glyph simultaneously encodes the consonant and the adjacent vowel

## **18.8 Syllabic vs compositional comparison**

| Metric | Syllabic (Part V) | Compositional (Part VI) |
| :---- | :---- | :---- |
| Ranking top-3 | Hebrew, Aramaic, Arabic | Hebrew, Arabic, Aramaic |
| Gap Hebrew-Aramaic | 0.27 pts | **3.87 pts** |
| Semitic gap → rest | 3.5 pts | **11.7 pts** |
| R-hat \< 1.1 (Hebrew) | 6% | **59%** |
| Mappings 100% reliable | 12 syllables | **18 glyphs** |
| Ratio PPX (Hebrew) | 4.00 | **2.07** |
| Search space | \~800\! | \~166 × 30 |
| Mapping unit | syllable → syllable (1-to-1) | glyph → character (many-to-one) |

The compositional model outperforms the syllabic model in all mapping quality metrics. The top-1 ranking is consistent (Hebrew), confirming that the Semitic signal is robust and independent of the level of analysis. The improvement in convergence (6% → 59%) and PPX ratio (4.00 → 2.07) indicates that the compositional assumption is more compatible with the actual structure of the Voynich Manuscript than the substitution assumption.

One notable result is the divergence of Aramaic between the two levels: at the syllabic level, Hebrew and Aramaic are indistinguishable (gap 0.27), but at the compositional level the gap widens to 3.87 points. This indicates that the character sequences of the mapped Voynich script are more similar to Hebrew than to Aramaic, although at the level of syllabic structure both languages ​​are equally compatible.

### **Limitations of the compositional approach**

1. **CharLM limited trigram.**It does not capture long dependencies. A character-level neural LM (LSTM/Transformer) could improve the scoring.

2. **C/V heuristic classification.**Based on the nuclear position of the syllables in Part IV, not on phonological knowledge. Ambiguous glyphs (semivowels,*mothers of reading*) may be misclassified.

3. **Mothers of reading.**In Hebrew and Arabic, certain consonants (aleph, he, vav, yod) function as vowel indicators. Binary C/V classification does not capture this duality, which can introduce inconsistencies in the mapping.

4. **Without cardinality restriction.**Mapping does not limit how many glyphs can collapse into a single character. Shin, with 17 glyphs, may be an artifact where the optimizer "parks" rare glyphs in the most frequent character instead of searching for their actual mapping.

5. **Without external validation.**The ranking is internally consistent (syllabic confirms compositional), but it has not been validated with independent tests: does the mapping produce coherent Hebrew text? Do the resulting triconsonantal roots exist in the lexicon? These questions are addressed in Part VII.

# **Part VI References**

- Ravi, S. y Knight, K. (2011). "Deciphering Foreign Language." *Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics* (ACL 2011), pp. 12--21.

Notebook: `07_compositional.ipynb`Results:`compositional_results.json`

Parts I-VII are available as separate documents.


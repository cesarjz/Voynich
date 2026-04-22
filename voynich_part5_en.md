# **PART V**

# **Syllabic Bayesian decipherment of the Voynich**

Part IV segmented the Voynich words into syllables, classified each syllable type by its positional function (onset, nuclear, coda), and detected internal morphophonological constraints—nucleus-coda harmony (V=0.284) and 27 productive suffix paradigms. The analysis concluded that the most promising attack vector for decryption is the exploitation of these paradigms using Bayesian methods operating at the syllable level (Ravi and Knight type, 2011). Part V implements precisely that approach: a Bayesian decryption that attempts to replace each Voynich syllable with a syllable from a candidate language, evaluating the plausibility of the result using a syllabic language model combined with morphological criteria.

# **Chapter 17\. Syllabic Bayesian Deciphering**

## **17.1 Motivation: from segmentation to decryption**

The segmentation of Part IV yielded a canonical inventory of 2,923 syllable types (792 with frequency ≥ 5). The Zipf distribution of this inventory, its suffix paradigms, and its nuclear-coda harmony are compatible with a real agglutinative language. The natural question is: a*that*Which language do these syllables belong to?

The classical Bayesian decryption approach (Ravi and Knight, 2011\) formulates the problem as a substitution: there exists an unknown mapping σ that transforms each symbol of the ciphertext into a symbol of the plaintext. The goal is to find σ\* \= argmax P(σ | ciphertext), where P is factored using a plaintext language model as a prior. Ravi and Knight applied this method at the character level. Here it is adapted to the syllable level: each Voynich syllable is mapped to a syllable of the candidate language, and plausibility is assessed using a syllabic language model plus two morphological components.

Syllable adaptation introduces a severe computational challenge: with 792 functional types mapped to inventories of comparable size, the space of bijective permutations is on the order of 800\!, astronomically larger than the \~30\! of character-level decryption. This space necessitates the use of intelligent initialization and MCMC exploration to find high-probability regions that have not been exhaustively explored.

## **17.2 Method: SyllableLM, MappingState, multi-component scoring**

### **Syllable Language Model (SyllableLM)**

For each candidate language, a syllable bigram language model with Witten-Bell smoothing is trained:

P(syl\_i | syl\_{i-1}) \= λ × C(syl\_{i-1}, syl\_i) / C(syl\_{i-1}) \+ (1-λ) × P\_backoff(syl\_i)

where λ is determined by Witten-Bell and the backoff is the unigram distribution. BOS/EOS tokens are included to model the start and end word probabilities. Probabilities are calculated in log₂ (cell 5 of the notebook).`06_bayesian_syllabic.ipynb`).

### **Mapping State**

The class`MappingState`It maintains a bijective σ mapping between Voynich syllables and candidate language syllables, with a class restriction: onset syllables map only to onset syllables, nuclear syllables to nuclear syllables, and codas to codas. This reduces the search space and ensures positional consistency. The main methods are:

- `propose_swap()`: swaps the target of two random syllables within the same functional class  
- `apply_word()`: given a mapping σ, transform a Voynich word into a sequence of syllables of the candidate language  
- `apply_corpus()`: applies the mapping to the entire corpus and calculates the aggregate score

### **Multi-component scoring**

The total score combines three components with fixed weights (cell 5):

**S\_total \= 2.0 × S\_LM \+ 1.5 × S\_paradigm \+ 1.0 × S\_harmony**

where:

- **S\_LM**(weight 2.0): average log-likelihood of the corpus mapped under the SyllableLM of the candidate language. It measures how closely the resulting syllable sequence resembles actual text of that language.

- **S\_paradigma**(weight 1.5): combination of JSD between suffix distributions, suffix inventory overlap, and Gini similarity between Voynich and candidate language paradigms. Measures whether morphological paradigms are preserved after mapping.

- **Harmony**(weight 1.0): preservation of nuclear-coda co-occurrence restrictions. Measures whether the preferred associations between Voynich roots and suffixes are maintained in the mapped language.

## **17.3 Five candidate languages**

Five languages ​​are selected that cover the main typological candidates identified in Parts II-IV (cell 7):

| Language | Family | Typology | Justification |
| :---- | :---- | :---- | :---- |
| Turkish | Altaica | Binder | Spectral gap \= 0.509, vowel harmony |
| Finnish | Uralic | Binder | Rich case paradigms, gap \= 0.577 |
| Latin | Indo-European | Inflexible | 15th-century lingua franca |
| Hebrew | Semitic | Triconsonantal roots | Classical Semitic Hypothesis |
| Arabic | Semitic | Triconsonantal roots | Semitic control |

The selection balances the two families most compatible with the statistical properties of the Voynich corpus (agglutinative due to the spectral gap, Semitic due to the positional structure), with Latin as the default historical candidate. The reference corpora are obtained from the Leipzig Corpora Collection and processed with the same TP-P20 segmentation applied to the Voynich corpus (cells 8-9).

## **17.4 Distributional Initialization**

### **7D distributional vectors**

Each syllabic type (both Voynich and each candidate language) is described by a 7-dimensional vector (cell 13):

1. Normalized frequency  
2. Proportion in initial position  
3. Proportion in middle position  
4. Proportion in final position  
5. Forward entropy (log₂ of the number of right contexts)  
6. Number of left contexts  
7. Number of legal contexts

### **Hungarian algorithm**

The initialization uses`scipy.optimize.linear_sum_assignment`to find the bijective assignment that minimizes the total cosine distance between Voynich vectors and candidate language vectors, respecting the class constraints (onset↔onset, nuclear↔nuclear, coda↔coda). This initialization is optimal within the linear constraints and provides an informed starting point for subsequent optimization (cells 14-15).

## **17.5 EM adapted \+ MCMC multi-chain**

### **Phase EM**

30 iterations of an EM algorithm adapted for each candidate language are executed (cell 17):

- In each iteration, swaps are proposed within each functional class.  
- Swaps that improve the overall score are accepted  
- Early stopping with patience for 5 iterations without improvement  
- 2,000-word subsample per iteration for efficiency

### **Fase MCMC**

For languages ​​with the best EM score, a Metropolis-Hastings multi-chain MCMC (cell 20\) is run:

| Parameter | Value |
| :---- | :---- |
| Chains | 4 (seeds: 42, 137, 256, 999\) |
| Iterations/string | 15,000 |
| Burn-in | 3,000 (discarded) |
| Thinning | Every 5th sample → 2,400 samples/chain |
| Total samples | 12,000 per language |
| Proposal | Random swap within class |
| Temperature | Calibrated from 300 proposals, T\_ratio \= 100 |
| Acceptance | Metropolis-Hastings, target \~50% |
| Subsample/iter | 2,000 words (5.4% of the corpus) |

The temperature is calibrated empirically: 300 test proposals are run and T\_start is set to obtain an acceptance rate close to 50%. The temperature decreases exponentially to T\_end, focusing the exploration on high-probability regions.

## **17.6 Results: language ranking**

The final ranking combines the EM and MCMC phases. For Hebrew and Aramaic (top-2 after EM), the reported score is the best found by MCMC; for the remaining four, the EM score (cell 25):

| \# | Language | Family | Score total | S\_LM | S\_paradigma | Harmony | PPX mapped | Native PPX | Ratio PPX |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 1 | **Hebrew** | Semitic | **\-35.70** | \-17.55 | 0.049 | \-0.669 | 100.19 | 25.1 | 3.99 |
| 2 | **Aramaic** | Semitic | **\-35.71** | \-17.78 | 0.363 | \-0.690 | 106.4 | 25.25 | 4.21 |
| 3 | **Arabic** | Semitic | \-37.41 | \-18.39 | 0.140 | \-0.834 | 124.9 | 25.4 | 4.91 |
| 4 | Finnish | Binder | \-39.28 | \-19.36 | 0.195 | \-0.846 | 161.1 | 29.4 | 5.49 |
| 5 | Latin | Indo-European | \-39.83 | \-19.77 | 0.259 | \-0.675 | 179.5 | 13.9 | 12.94 |
| 6 | Turkish | Binder | \-39.89 | \-19.69 | 0.250 | \-0.886 | 175.6 | 33.2 | 5.29 |

Note: In the EM phase, Aramaic was ranked \#1 (-36.50 vs \-36.66 for Hebrew). The MCMC reversed the order by a margin effectively zero (0.01 nats).

> **Reproducibility note:** Exact MCMC scores vary between runs due to the stochastic nature of the sampler. The Hebrew-Aramaic gap fluctuates between ~0.01 and ~0.27 nats across executions, but always remains within the bootstrap 95% CI that spans zero. The companion paper reports 0.27 nats from an earlier execution; the values above reflect the most recent run. All qualitative conclusions (NW Semitic cluster, >3.5 nats separation from non-Semitic) are stable across runs.

### **Interpretation of the ranking**

The ranking shows a three-level structure:

**Level 1 — Northwest Semites:**Hebrew and Aramaic are virtually tied (Δ \= 0.01 points). Hebrew has a better S\_LM (-17.55 vs \-17.78) and a lower PPX ratio (3.99 vs 4.21), while Aramaic has a significantly better S\_paradigm (0.363 vs 0.049), indicating that its morphological paradigms fit the Voynich syllabic structure better. The difference is minimal and does not allow for confident discrimination between the two.

**Level 2 — Arabic:**Arabic is 1.5 points behind the Northwest Semitic languages. It shares the Semitic family but has a more distinct phonotaxis from Voynich, which is reflected in its higher PPX ratio (4.91).

**Level 3 — Non-Semitic:**Finnish, Latin, and Turkish form a cluster at \>3.5 points away from Northwest Semitic languages. The gap between the Semitic and non-Semitic levels is substantial and consistent.

Aramaic as a candidate has a strong historical basis: the Targum Onkelos (Biblical Aramaic) shares approximately 70% of its roots with Hebrew but has its own distinct phonotaxis. Its inclusion as the sixth candidate language was motivated by the roots-vs-phonotaxis paradox in Chapter 20 (Part VII): constrained mapping detects Hebrew roots but does not produce fluent Hebrew n-grams, which is consistent with a related Semitic language.

The PPX ratio (mapped perplexity / native perplexity) is revealing: for Hebrew, the mapped corpus has 3.99× the perplexity of native Hebrew. This is high—indicating that the mapping does not produce fluent Hebrew text—but it is the lowest of the six candidates. Latin has the worst ratio (12.94) despite having the lowest native PPX (13.9), indicating that its low intrinsic complexity does not compensate for the poor quality of the mapping.

## **17.7 MCMC diagnoses: limited convergence**

Convergence diagnoses reveal a fundamental limitation of the syllabic approach (cell 22):

### **Aramaic**

| Metric | Value |
| :---- | :---- |
| R-hat \< 1.1 | **38/713 syllables (5%)** |
| R-hat mediana | 1.555 |
| Average confidence | 0.218 |

### **Hebrew**

| Metric | Value |
| :---- | :---- |
| R-hat \< 1.1 | **40/697 syllables (6%)** |
| R-hat mediana | 1.505 |
| Average confidence | 0.209 |

Convergence is extremely limited: only 5–6% of syllables have R-hat \< 1.1, the standard convergence threshold (Gelman & Rubin, 1992). The median R-hat (\~1.5) is well above the threshold, indicating that the strings have not explored the same modal space. Hebrew and Aramaic show virtually identical convergence, which is to be expected given that they share the same 22–27 character script and a similar syllabic structure.

### **Interpretation**

The poor convergence is not an implementation flaw but a consequence of the search space: with \~800 functional types and bijective permutations within three classes, the search space is enormously multimodal. Strings become trapped in different local modes. This result has a substantive implication: if Voynich were truly a syllable-level substitution cipher, strings should converge better—the signal would be clearer. The poor convergence suggests that the one-to-one substitution assumption is incorrect and that the encoding is likely compositional.

## **17.8 Qualitative Reconstruction**

Despite the limited convergence, the higher confidence mappings later allow a partial reconstruction of the text (cells 26-30).

### **High-confidence mappings**

| Voynich syllable | Hebrew syllable | Subsequent trust |
| :---- | :---- | :---- |
| Q2 | Kaf | 0.996 |
| J1 | ח (the) | 0.778 |
| Not | ג (gimel) | 0.602 |
| Aa | נ (we) | 0.500 |

Only a handful of syllables have a posterior confidence clearly superior to chance (0.5). The mapping Q2→כ is the most robust (0.996), but most syllables have a confidence of \~0.5, indicating that the strings do not agree.

### **Reconstructed paradigms**

Suffix paradigms mapped to Hebrew show partial structure:

| Voynich root | Mapped root | N suffixes | Dominant suffix | Tokens |
| :---- | :---- | :---- | :---- | :---- |
| Q1 | — | 8 | M-Y-M (204 tok, 70.3%) | 290 |
| K2 | פ (only) | 8 | ד (102 tok, 47.7%) | 214 |
| Q2 | Kaf | 6 | א (96 tok, 75.0%) | 128 |

The reconstruction shows that the paradigms are partially preserved, but overall coherence is low: the perplexity of the reconstructed text (75.07) is much higher than that of native Hebrew (25.1).

## **17.9 Limitations**

1. **Intractable search space.**With approximately 800 functional syllable types, the space of bijective permutations (approximately 800\!) is astronomically larger than in character-level decryption (approximately 30\!). Even with Hungarian initialization and multi-chain MCMC, the exploration is insufficient to guarantee convergence.

2. **Assumption of 1-to-1 substitution.**The model assumes that each Voynich syllable corresponds to exactly one syllable of the candidate language. If the encoding is compositional—as suggested by the SilPart model in Part III—this assumption is fundamentally incorrect: each Voynich syllable is composed of glyphs (onset \+ nucleus \+ coda) that encode independent phonological information.

3. **Bigram language model.**A bigram syllabic LM captures only dependencies between adjacent syllables. A higher-order or neural LM could provide more discriminative scoring.

4. **Limited language coverage.**Only 6 of the world's \~7,000 languages. The inclusion of Aramaic (Targum Onkelos) improves Semitic coverage, but the absence of Romance languages ​​(Italian, Catalan, Occitan) is notable given the manuscript's historical context.

5. **Lack of external information.**No information is included regarding the illustrations, the structure of the manuscript, or the provenance history, which could provide*cribs*to anchor the decryption.

### **Motivation for the compositional approach**

The limited convergence of syllabic MCMC (\~7% R-hat \< 1.1) has a direct implication: if Voynich encoding is not substitutive but compositional (as predicted by the SilPart model), the correct level of analysis is the glyph, not the syllable. Chapter 18 implements precisely this change: a compositional decryption where each glyph maps to a character of the candidate language (many-to-one, 166 glyphs → \~27-30 characters), reducing the search space and allowing multiple glyphs to collapse onto the same target character.

# **Part V References**

- Gelman, A. y Rubin, D. B. (1992). "Inference from Iterative Simulation Using Multiple Sequences." *Statistical Science* 7(4): 457--472.

- Ravi, S. y Knight, K. (2011). "Deciphering Foreign Language." *Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics* (ACL 2011), pp. 12--21.

Notebook: `06_bayesian_syllabic.ipynb`Results:`bayesiano_silabico_resultados.json`

Parts I-VII are available as separate documents.


# **PART II**

**Mathematical Foundations**

*This section develops the mathematical tools used in the analysis. For each tool, it explains what it measures, why that measure is useful for studying the Voynich Maneuver, and how it is calculated in practice. No prior mathematical knowledge beyond basic arithmetic is required.*

| Chapter | Tool | Question that answers |
| :---- | :---- | :---- |
| **5** | **Shannon's Entropy and Mutual Information** | How much uncertainty does the text have? How well does the glyph predict the position? |
| **6** | **Permutation tests and p-values** | Could the observed pattern appear by chance? |
| **7** | **Chi-square and Jensen-Shannon divergence** | Are two frequency distributions different? |
| **8** | **Markov chains and spectral gap** | How do dependencies spread between glyphs? |
| **9** | **Neural networks, statistical footprint, weighted distance, and sensitivity** | What generative mechanism reproduces the Voynich fingerprint? Is the result robust? |
| **10** | **Combinatorial optimization and Bayesian inference** | Which candidate language is the Voynich syllabic mapping most compatible with? |

# **Chapter 5\. Shannon's Entropy and Mutual Information**

## **5.1 The problem of measuring uncertainty**

Imagine you have to guess the next symbol in a sequence. If the sequence is completely random, each symbol is equally likely, and you can't do any better than chance. If the sequence has structure, some symbols are more likely than others in each context, and you can do better. Claude Shannon's information theory (1948) was born precisely to quantify how much uncertainty exists in a source of information and how much disappears when the context is considered.

Shannon was a mathematician and engineer at Bell Labs working on the problem of transmitting messages efficiently over noisy channels. To solve it, he needed a measure of how much information a message contains. His solution was entropy, a function that has exactly the intuitive properties one would expect from a measure of uncertainty.

## **5.2 Entropy: Measuring Uncertainty**

### **5.2.1 The intuitive idea**

Think about flipping a coin. If the coin is fair, heads and tails are equally likely: there is maximum uncertainty about the outcome. If the coin is rigged and lands on heads 99% of the time, there is little uncertainty: we almost always know what it will land on. A fair six-sided die has more uncertainty than a coin because there are six possibilities instead of two.

Shannon formalized this intuition into a function he called entropy, borrowing the name from thermodynamics due to the mathematical similarity between the two quantities. The entropy of a probability distribution measures how much average uncertainty there is when observing a symbol from that distribution.

**Shannon's definition of entropy**

Given a probability distribution over N possible symbols, where symbol i has probability p\_i, the entropy H is defined as: H \= −Σ p\_i · log₂(p\_i). The sum covers all possible symbols. The log₂ function uses base-2 logarithms, which means the entropy is measured in bits. The negative sign ensures that the result is always positive or zero.

### **5.2.2 Why this formula works**

The formula may seem arbitrary at first. To understand why it makes sense, let's think about what properties we want a measure of uncertainty to have:

- If all symbols are equally probable (maximum uncertainty), the entropy must be maximum.

- If a symbol has a probability of 1 (absolute certainty), the entropy must be 0\.

- If we add an impossible symbol (probability 0), the entropy should not change.

- If we have two independent sources, the entropy of the combination must be the sum of the individual entropies.

The function −p·log₂(p) satisfies exactly these four properties. When p=1, log₂(1)=0 and the term is 0\. When p is very small but positive, the term is also small (p tends to 0 faster than log₂(p) tends to infinity). The weighted sum produces a quantity that is maximum when all p\_i are equal.

**Numerical example: the Voynich alphabet**

The Voynich corpus has 166 distinct glyphs. If they were all equally frequent, the entropy would be log₂(166) ≈ 7.37 bits. But in reality, the glyphs have very different frequencies: A1 appears thousands of times, while glyphs like Ys or Yp appear less than 100 times. This inequality reduces the actual entropy. The Voynich corpus has an entropy H₀ ≈ 4.14 bits, significantly below the theoretical maximum.

### **5.2.3 Bits as a unit**

Choosing base 2 for the logarithm means that entropy is measured in bits. A bit is the amount of information in a fair coin toss: there are two options, 0 or 1, and each has a probability of 1/2. The formula gives −(1/2)·log₂(1/2)−(1/2)·log₂(1/2) \= 1 bit, exactly.

An entropy of 4.14 bits means that, on average, approximately 4.14 bits of information are needed to specify which Voynich glyph comes next, assuming we know only the overall frequency distribution but not the context. For comparison: Medieval Latin has H₀ ≈ 4.12 bits (similar to Voynich because it also has a similarly sized alphabet with a non-uniform distribution).

## **5.3 Conditional entropy: the role of context**

### **5.3.1 From global entropy to conditional entropy**

The entropy we just described measures the average uncertainty of a symbol when we know nothing about its context. But in a real text, the previous symbol (or the N preceding ones) gives us information about the next. In Spanish, 'u' almost always follows 'q'. Conditional entropy measures how much uncertainty remains about the next symbol when we know the N preceding ones.

The conditional entropy of order N, which we write H\_N, is defined as the average uncertainty of the symbol at position t+1, given that we know the N preceding symbols (positions t-N+1 to t). Mathematically:

**H\_N \= −Σ P(context, symbol) · log₂ P(symbol | context)** *(Conditional entropy of order N)*

where the sum traverses all pairs (context of length N, next symbol) that appear in the corpus.

### **5.3.2 A fundamental law: conditional entropy cannot grow**

There is a fundamental mathematical property that all conditional entropy must respect: H\_N ≤ H\_{N-1} for all N. In other words: knowing more context can never increase uncertainty. This makes intuitive sense: if you already knew the last three glyphs and now I tell you the fourth one, you have more information, not less.

This property is one of the reasons we detected the error in our first version of the code. When the parser produced an inflated vocabulary of 9,762 tokens, the entropy calculations violated this law: H₁ \> H₀, which is mathematically impossible. It was a sign that something was wrong with the data, not the mathematics.

**Monotonicity as a test of correctness**

If any conditional entropy analysis shows that H\_N \> H\_{N-1} for some N, there is almost certainly an error in the data or the estimator. This mathematical property functions as an automatic sanity check: the results in block C of the analysis include an explicit monotonicity check before interpreting any results.

### **5.3.3 How it is calculated in practice and the problem of scarce data**

Calculating H\_N in practice requires estimating P(symbol | context) by counting how many times each symbol follows each possible context in the corpus. For N=1 this is simple: there are 166 possible glyphs as context and 166 as following symbol, so we need to estimate 166×166 \= 27,556 probabilities.

For N=2, the context has 166² \= 27,556 possible pairs, and for N=3 there are 166³ ≈ 4.6 million. The problem is that our corpus has only \~157,000 glyphs. For N=3, most possible contexts never appear in the text, and their estimated probability would be 0 if we don't apply any correction.

This problem is called the data sparsity problem, and there are several techniques for dealing with it. The simplest is Laplace smoothing, which adds 1 to all counts, including zeros. The problem is that with a large vocabulary (9,762 false tokens in the flawed version), adding 1 to thousands of empty cells introduces more noise than signal. With the correct vocabulary of 166 tokens, the smoothing is proportional and well-behaved.

For the conditional entropy analysis in this work (Block C), we use the Witten-Bell estimator, which is more robust than Laplace for moderate vocabularies. The idea behind the Witten-Bell estimator is that the probability of seeing a new symbol in a given context is proportional to the number of distinct types of symbols that have already been seen in that context, not to a fixed 1\.

## **5.4 Mutual information: measuring dependence**

### **5.4.1 The question that mutual information answers**

Entropy measures absolute uncertainty. Mutual information measures how much uncertainty about one variable is reduced when we know another. Formally, the mutual information I(X;Y) between two random variables X and Y measures how many bits of information they share.

In the context of the Voynich analysis, we use mutual information to answer a specific question: how much information does the glyph share with its position within the word (beginning, middle, end)? If the answer is a lot, it means that the glyphs are not randomly distributed throughout the word: some prefer the beginning, others the end. This is precisely the signature of a system with morphology.

**I(X ; Y) \= Σ P(x, y) · log₂ \[ P(x, y) / (P(x) · P(y)) \]** *(Mutual information)*

where X is the glyph, Y is the position (start/middle/end), and the sum runs through all the (glyph, position) pairs that appear in the corpus.

### **5.4.2 Interpretation: when it is large or small**

When X and Y are independent, P(x,y) \= P(x)·P(y), the logarithm is log₂(1) \= 0, and mutual information is 0\. This means that knowing the glyph tells you nothing about its position and vice versa. If the glyphs were evenly distributed between the beginning, middle, and end of a word, mutual information would be 0\.

When dependence exists, frequent pairs have P(x,y) \> P(x)·P(y), the logarithm is positive, and they contribute positively to the MI. Infrequent pairs have the opposite, but the weight P(x,y) makes them contribute little. The net result is positive and is greater the stronger the dependence.

| Body / system | MY positional | Interpretation |
| :---- | :---- | :---- |
| Completely random text | **≈ 0.00 bits** | Glyphs have no preferred position |
| English (Pride & Prejudice) | **0.232 bits** | Weak structure: English prefixes and suffixes are moderately predictable |
| **Voynich (complete corpus)** | **0.658 bits** | Strong structure: the glyphs have highly preferred positions |
| Probabilistic slot p=0.75 | **0.821 bits** | Similar to Voynich: each slot has a 75% probability of its canonical morpheme |
| Rigid slot (fixed morphology) | **1.585 bits** | Theoretical maximum: each glyph appears exclusively in one position |

The Voynich morphological index (0.658 bits) is clearly higher than that of a typical natural language like English (0.232 bits) and clearly lower than a perfectly rigid slot system (1.585 bits). This places Voynich in an intermediate zone compatible with a flexible morphological system: there are strong but not absolute positional preferences.

### **5.4.3 Bigram Mutual Information**

In addition to the MI between glyph and position, we also calculate the mutual information between adjacent glyphs within the same word: I(glyph\_i ; glyph\_{i+1}). This measures how much information a glyph shares with the one that immediately follows it.

A high bigram MI value indicates that the transitions between glyphs are not free: certain glyphs tend to be followed by certain others. This is also a morphological signature: roots have their own bigram structures, distinct from those of prefixes and suffixes.

For the Voynich corpus, the bigram MI is 1.681 bits, comparable to that of a probabilistic slot system with p≈0.92. The most informative bigrams are D1→A1 (contribution 0.1321 bits), A3→G1 (0.1212 bits), and A1→Q1 (0.1164 bits). These bigrams are so frequent and predictable that they alone explain one-third of the entire bigram MI in the corpus.

## **5.5 Conditional Entropy and the U-Shape of the Voynich**

### **5.5.1 What we expect to see in a natural language**

In a natural language, the H\_N curve (entropy of order N for N=0,1,2,3,4) decreases monotonically: each additional context glyph reduces uncertainty. In Latin, H₀=4.12 bits, H₁=3.46 bits, H₂=2.95 bits, H₃=2.59 bits, H₄=2.46 bits. The reduction is smooth and continuous because Latin words are long and dependencies within words span several characters.

In a monoalphabetic cipher like Caesar, the curve is almost identical to that of the ciphertext (Latin in our case), because the cipher is simply a permutation of the symbols and doesn't change the statistics of the transitions. In a polyalphabetic cipher like Vigenère, the curve decreases more slowly because the key mixes the patterns, but it remains monotonic.

### **5.5.2 The Voynich Anomaly**

The Voynich curve has a completely different shape from all other control systems. H₀=4.14, H₁=2.96: the context of a glyph reduces entropy by more than one bit. So far, it looks like a normal language with strong bigram dependencies. But H₂=2.99, H₃=3.32, H₄=3.77: entropy rises again. The curve is U-shaped.

This pattern, which we call 'bounce', has a precise morphological interpretation: the bigram accurately predicts the next glyph (low H₁), but the 2-4 glyph context crosses the word boundary and loses predictive power. This occurs because Voynich words are very short (average of \~4.2 glyphs) and dependencies are confined within the word. A 3-4 glyph context almost always spans the end of one word and the beginning of the next, where the correlation is minimal.

| Body / system | H₀ | H₁ | H₂ | H₃ | H₄ |  |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **Voynich** | 4.141 | **2.961** | **2.990** | **3.317** | **3.774** |  |
| Latin | 4.122 | 3.462 | 2.948 | 2.588 | 2.459 |  |
| Caesar | 4.121 | 3.463 | 2.951 | 2.593 | 2.466 |  |
| Vigenère | 4.616 | 4.324 | 3.593 | 3.116 | 2.894 |  |

*The orange values ​​for Voynich are the 'bounce': H₂, H₃ and H₄ are greater than H₁. The green value (H₁=2.961) is the minimum of the curve, reached with only 1 context glyph.*

**The rebound as a unique morphological signature**

The rebound of the entropic curve (U-shaped) is the most remarkable statistical finding of the analysis. None of the control corpora—Latin, Caesar, Vigenère—exhibit this behavior. The rebound indicates that Voynich dependencies are strictly local: very strong within words (especially in bigrams) but nonexistent between words. This is incompatible with substitution ciphers, which would inherit the extent of dependencies from the cipher language.

## **5.6 Entropy and the Witten-Bell estimator**

As mentioned earlier, estimating high-order conditional entropies requires addressing the problem of unseen contexts. The Witten-Bell estimator works as follows: when a previously seen context appears, it uses the relative frequency of each symbol observed in that context. For symbols that have never followed that context, it distributes an 'escape' probability proportional to the number of distinct symbol types that do appear in that context.

The intuition is that if a context is followed by many different symbols (a 'promiscuous' context), there is a greater chance of a new symbol appearing; if a context is always followed by the same symbol (a 'rigid' context), the probability of seeing something new is low. This is more reasonable than assigning the same probability of escape to all contexts, as Laplace does.

**Chapter summary**

- Shannon entropy H measures the average uncertainty of a symbol in a distribution. It is measured in bits. A uniform distribution has maximum entropy; a distribution where one symbol dominates has low entropy.

- The conditional entropy H\_N measures the uncertainty that remains about the next symbol when we know the previous N. H\_N is always ≤ H\_{N-1}: more context can never increase the uncertainty.

- Mutual information I(X;Y) measures how much information two variables share. In Voynich, it is used to measure how well the glyph predicts its position in the word (positional MI \= 0.658 bits) and how well the glyph predicts the next glyph (bigram MI \= 1.681 bits).

- The Voynich H₀→H₄ curve is U-shaped (0.813-bit bounce), unlike Latin, Caesar, and Vigenère, which are monotonically decreasing. This is the most distinctive statistical signature of the Voynich writing system.

# **Chapter 6\. Permutation Tests and p-values**

## **6.1 The fundamental problem of statistical inference**

Suppose you calculate the mutual positional information of the Voynich script and get 0.658 bits. Is this a high value? Is it evidence that the text has structure? Compared to English (0.232 bits), it seems high. But perhaps the Voynich script is simply random, with some fluctuations that happen to produce 0.658.

This is the central problem of statistical inference: distinguishing between a real pattern and a random fluctuation. The mathematical answer to this problem is hypothesis testing, and the key tool is the p-value. Before explaining what a p-value is, we need to understand what question it answers, because it is one of the most misunderstood concepts in all of statistics.

## **6.2 The null hypothesis and the p-value**

### **6.2.1 The null hypothesis**

In a statistical hypothesis test, you always start with a null hypothesis, which represents the most boring explanation of the data: that nothing interesting is happening. In our case, the null hypothesis for the positional MI test is:

*"H₀: Voynich glyphs are randomly distributed among the start, middle, and end positions of a word. The observed MI of 0.658 bits is simply the result of the statistical fluctuation of a random distribution."*

If the null hypothesis were true, what MI would we expect to observe? Not exactly 0 bits, because even random data has fluctuations. We would observe a positive but small MI, and that MI would fluctuate from sample to sample around some expected value close to 0\.

### **6.2.2 What exactly is the p-value?**

The p-value is the probability of observing an outcome as extreme as the one we observed (or more extreme), assuming the null hypothesis is true. A small p-value means: 'if the text were random, it would be very unlikely to obtain this result'. A large p-value means: 'this result is consistent with chance'.

The usual convention in science is to reject the null hypothesis when the p-value is less than 0.05 (5%) or, for more robust results, 0.001 (0.1%). These thresholds are arbitrary but are well established as standards within the scientific community.

**What the p-value does NOT say**

The p-value is NOT the probability that the null hypothesis is true. It doesn't say 'there is a 0.1% probability that the text is random'. What it says is 'if the text were random, there would only be a 0.1% probability of observing an MI ≥ 0.658'. The difference is subtle but crucial. Converting p-values ​​into hypothesis probabilities requires Bayes' theorem, which demands prior knowledge that we generally lack.

## **6.3 Permutation tests: an approach without assumptions**

### **6.3.1 The problem with classical parametric tests**

Classical statistical tests (such as the chi-square test, which we will discuss in the next chapter) assume that the data follow a known mathematical distribution. The chi-square test, for example, assumes that the observed frequencies follow a chi-square distribution under the null hypothesis. This assumption may be incorrect for linguistic texts, where words are not independent of each other.

Permutation tests avoid this problem by constructing the reference distribution directly from the data, without assuming any parametric distribution. They are a family of nonparametric tests particularly well-suited for linguistic analysis.

### **6.3.2 How a permutation test works**

The idea is simple and elegant. Instead of calculating the theoretical distribution of the statistic under the null hypothesis, we generate it empirically by destroying the pattern we want to test and seeing what values ​​the statistic produces in the absence of that pattern.

For the Voynich positional MI test, the procedure is:

1. Calculate the positional MI of the original corpus: 0.658 bits. This is the observed value.

2. Create a copy of the corpus where, in each word, the glyphs are randomly mixed together (intra-word permutation). This destroys the order within the word but preserves exactly which glyphs are in which words.

3. Calculate the positional MI of the permuted corpus.

4. Repeat steps 2-3 a large number of times (in our analysis, n=1,000 permutations).

5. The collection of 1,000 MI values ​​from permuted corpora is the reference distribution under the null hypothesis.

6. The p-value is the proportion of permutations that produce an MI equal to or greater than the observed value (0.658).

**Why intra-word permutation**

Permutation mixes glyphs within each word, not between words. This is important because we specifically want to test for positional structure within the word. If we mixed glyphs between words, we would also destroy the frequency distribution of glyphs by word position (word-beginning vs. word-end), introducing a different kind of destruction than the one we're interested in. Intra-word permutation is the minimal perturbation that destroys the order within the word while preserving everything else.

### **6.3.3 Results of the permutation test in the Voynich**

With n=1,000 permutations with fixed seeds (for reproducibility), the results are:

- MI observada: 0.658 bits

- My average of permuted corpora: 0.198 bits

- Standard deviation of MI in permutations: 0.004 bits

- p-value: 0.000 (none of the 1.000 permutations produce an MI ≥ 0.658)

A p-value of 0.000 with n=1.000 permutations means that the observed value is at least 100 times more extreme than the worst result obtained in the permutations. In terms of the number of standard deviations, the observed value is (0.658 − 0.198) / 0.004 \= 115 standard deviations from the mean of the null distribution. This is an extraordinarily significant result.

**The importance of testing all glyphs**

In addition to the global MI test, the analysis applies the permutation test individually to each of the 166 glyphs in the vocabulary. The result is that 32 glyphs (those with a frequency ≥ 20, to ensure statistical power) show positional preferences with p \< 0.001. Among them, D1 appears in word-initial position 98.9% of the time, an extraordinarily rigid preference. This is the computational signature of a prefix.

## **6.4 Holdout validation as a time permutation test**

Block B of the analysis applies a conceptual variant of the permutation test: instead of permuting the glyphs within the corpus, it divides the corpus into two independent halves (even-numbered folios as training, odd-numbered folios as testing) and verifies that the patterns discovered in the first half are replicated in the second.

The motivation is to avoid analytical circularity: if we discover that D1 is a prefix using all the data and then validate this finding on the same data, we are seeing what we want to see. The holdout ensures that the validation is done on data that did not participate in the pattern discovery.

The results of the holdout (116 training folios, 110 test folios, with similar proportions of words and glyphs in both splits) show that the positional preferences of all significant glyphs are replicated in the test set with high consistency. This rules out the possibility that the results are artifacts of the specific folios used for the analysis.

**Chapter summary**

- The null hypothesis is the boring explanation of the data: that there is no real pattern, only random fluctuation.

- The p-value is the probability of seeing an extreme result as observed if the null hypothesis were true. It is NOT the probability that the null hypothesis is true.

- Permutation tests construct the reference distribution by destroying the pattern being tested (permuting the order of the glyphs within each word) and calculating the statistic on the destroyed corpus, repeated n=1,000 times.

- The Voynich positional MI test yields a p-value of 0 with n \= 1,000 permutations: the observed value (0.658 bits) is 115 standard deviations away from the mean of the null distribution (0.198 bits). This is one of the most significant results of the analysis.

- The holdout by folio (even folios / odd folios) is a second level of validation that rules out analytical circularity.

# **Chapter 7\. Chi-square and Jensen-Shannon Divergence**

## **7.1 The problem of comparing distributions**

Many interesting questions in Voynich analysis take the form: 'Are these two distributions distinct?' For example: Is the distribution of glyphs in the herbal section distinct from that in the biological section? If the Voynich is a text with semantically distinct content, we would expect so. If it is random text or a uniform cipher, we would expect not.

Two distinct mathematical tools approach this problem from complementary angles. Pearson's chi-squared test answers with a p-value: 'Are these distributions significantly different?' The Jensen-Shannon divergence quantifies how different they are, producing a number between 0 (identical) and 1 (maximally different).

## **7.2 The chi-square test**

### **7.2.1 The intuitive idea**

The chi-square test compares what we observe with what we would expect if the distributions were equal. If the distribution of glyphs in the herbal and biological sections were identical, each glyph should appear in each section in proportion to its overall frequency. The chi-square test measures how much the observed data deviates from this expectation.

Consider a simple example: if the herbal section contains 38.5% of all words in the corpus and the biological section contains 18.2%, then we would expect glyph A1 to appear 38.5% of its total occurrences in herbal and 18.2% in biological. If it actually appears 45% of the time in herbal and 12% of the time in biological, there is a deviation. The chi-square test sums all these squared (normalized) deviations for the 166 glyphs and the 4 sections.

### **7.2.2 The formula and its interpretation**

**χ² \= Σ (Observed − Expected)² / Expected** *(Pearson's chi-square test)*

where the sum traverses all cells of the contingency table (all glyph × section combinations). The resulting χ² value approximately follows a chi-square distribution with (number of glyphs − 1\) × (number of sections − 1\) degrees of freedom, from which the p-value is obtained.

For the Voynich Manuscript, the contingency table has 166 glyphs × 4 sections \= 664 cells, but some are merged because they contain little data. The result is χ² \= 6,626.75 with p ≈ 0 (essentially zero: the exact value exceeds the numerical precision of the computer). The 468 degrees of freedom correspond approximately to (166−1) × (4−1).

**Interpretation of the chi-square result**

The χ² value of 6,626.75 with p ≈ 0 and 468 degrees of freedom means that the glyph distribution is statistically distinct among the four sections with a certainty exceeding any conventional threshold. To put this in context: if the distributions were identical, we would expect a χ² value of approximately 468 (equal to the degrees of freedom). We obtain 6,626, which is more than 14 times the expected value under the null hypothesis. This result is only possible if there are substantial differences in the glyph vocabulary between sections.

### **7.2.3 Limitations of the chi-square test**

The chi-square test has two important limitations. First, it requires that the expected frequencies be sufficiently large (rule of thumb: ≥ 5 in each cell); otherwise, the approximation to the chi-square distribution is inaccurate. Therefore, we excluded the astronomical and zodiacal sections from the analysis: they have very few words, and many glyphs would have expected frequencies \< 5\.

Second, the chi-square test only tells us if there is a difference, not how much or where. To quantify the magnitude of the differences between pairs of sections, we need the Jensen-Shannon divergence test.

## **7.3 The Jensen-Shannon Divergence**

### **7.3.1 The Kullback-Leibler divergence as a starting point**

To understand the Jensen-Shannon (JSD), it's helpful to start with the Kullback-Leibler (KL) divergence, which is the basic building block. The KL divergence of the Q distribution from P measures how much extra information is needed to describe symbols of P using Q instead of P.

**D\_KL(P || Q) \= Σ P(x) · log₂ \[ P(x) / Q(x) \]** *(Kulback-Leibler Divergence)*

A D\_KL value of 0 means that P and Q are identical. A large value means that Q is a poor approximation of P. KL has a problem: it is not symmetric. D\_KL(P || Q) ≠ D\_KL(Q || P), so it cannot be used directly as a 'distance' between distributions.

### **7.3.2 The Jensen-Shannon Divergence**

The JSD solves the KL asymmetry problem by averaging the two directions through an intermediate distribution M \= (P \+ Q) / 2:

**JSD(P, Q) \= ½ · D\_KL(P || M) \+ ½ · D\_KL(Q || M)** *(Jensen-Shannon Divergence)*

The result is between 0 and 1 (when using base-2 logarithms). JSD \= 0 means that P and Q are identical. JSD \= 1 means that P and Q have no elements in common: they are maximally distinct.

The JSD is also the square root of a true metric distance between probability distributions, which makes it mathematically very well behaved for multiple comparisons.

### **7.3.3 JSD results between Voynich sections**

We calculated the JSD between the word distributions (top-500 most frequent words) of each pair of sections:

|  | herbal | organic | pharmaceutical |
| :---- | :---- | :---- | :---- |
| **organic** | 0.316 | \--- | \--- |
| **pharmaceutical** | 0.252 | 0.469 | \--- |
| **recipes** | 0.217 | 0.168 | 0.384 |

*Green: JSD \< 0.25 (similar sections). Red: JSD \> 0.40 (very different sections). Average JSD between all pairs: 0.301.*

The distance pattern shows thematic coherence: biological and prescriptions are the most similar sections (JSD \= 0.168), perhaps because both are text-dense with similar functional vocabulary. Pharmaceutical and biological are the most distinct (JSD \= 0.469), possibly because the pharmaceutical section contains more names of specific ingredients.

A uniform cipher (one that does not preserve semantic content) would produce JSD ≈ 0 across all sections, because the cipher would shuffle the glyphs regardless of their content. The fact that we obtain JSD values ​​between 0.17 and 0.47 is incompatible with a uniform cipher consistent with a specialized vocabulary for each section.

## **7.4 The logistics classifier as additional validation**

An alternative way to check if the sections are distinguishable is to train an automatic classifier: given the glyph profile of a word, can an algorithm predict which section it was written in?

We used logistic regression (one of the simplest and most interpretable machine learning classifiers) with the following ingredients: for each word, we calculated the relative frequency of each glyph and the word length, producing a feature vector of 167 numbers. The logistic regression learns to assign a section to each vector.

Validation is performed using stratified 5-fold cross-validation: the corpus is divided into 5 equal parts, the classifier is trained on 4 parts and evaluated on the 5th, rotating the parts. This ensures that the classifier does not 'see' the evaluation data during training.

**Classifier result**

Accuracy mean \= 0.429 ± 0.012 (5-fold CV). The random baseline is 0.250 (4 equal-sized sections). The classifier outperforms chance by 72% relative. The low variance between folds (±0.012) confirms stability. This result means that the glyph profile of a word contains real information about the subject section to which it belongs.

An accuracy of 43% may seem low in absolute terms, but it needs to be put into context. The classifier works with individual words of only \~4 glyphs on average, using only glyph frequency as features. With such limited information, for example, it's remarkable that it consistently outperforms chance.

**Chapter summary**

- The chi-square test compares frequency distributions by counting how much the observed frequencies deviate from those expected under the assumption of equality. For the Voynich, χ² \= 6,626.75 with p ≈ 0: the glyph distributions are significantly different between sections.

- The Jensen-Shannon divergence quantifies how different two distributions are, with values ​​ranging from 0 (identical) to 1 (no overlap). The mean JSD across Voynich sections is 0.301, with thematically consistent variation.

- A logistic classifier trained solely on the glyph profile of each word correctly predicts the section 43% of the time (baseline: 25%). This confirms that the glyph vocabulary is thematically specialized.

- These three combined results are incompatible with a uniform cipher, which would not preserve vocabulary specialization between sections.

# **Chapter 8\. Markov Chains and Spectral Gap**

## **8.1 Modeling sequences with memory**

So far we have studied static properties of text: frequency distributions, positional preferences. But language has an essential dynamic property: what comes next depends on what has just happened. A mathematical model that captures this dependency is the Markov chain.

A Markov chain is a probabilistic model of a sequence where the probability of the next state depends only on the current state, not on the entire preceding history. For a text, the 'state' is the current glyph and the 'transition' is which glyph comes next. This is a simplification (the actual relevant context may be longer), but it captures first-order dependencies and produces analyzable results.

## **8.2 The transition matrix**

### **8.2.1 Construction**

To construct the Markov chain of a text, we count how many times each glyph is followed by every other glyph within the same word. This produces an array M of dimensions (number of glyphs) × (number of glyphs), where M\[i\]\[j\] is the number of times glyph i is followed by glyph j.

Normalizing each row by the row sum, we obtain the stochastic transition matrix P, where P\[i\]\[j\] is the probability that glyph i is followed by glyph j. Each row sums to 1 (as a probability distribution should).

For the Voynich Manuscript, the matrix has dimensions 166 × 166 \= 27,556 cells. Most cells have a value of 0 (most glyph pairs never appear together), but frequent pairs have substantial probabilities. For example, P\[D1\]\[A1\] ≈ 0.85: when D1 appears, there is an 85% probability that the next glyph will be A1.

### **8.2.2 The eigenvalues ​​of the transition matrix**

The mathematical tool we use to analyze the transition matrix is ​​decomposition into eigenvalues ​​(also called proper values). The eigenvalues ​​of a matrix are special numbers that summarize its transformation properties in ways that are difficult to see by looking at the individual elements.

For a stochastic transition matrix of an ergodic Markov chain (which can visit all states), there is always a dominant eigenvalue λ₁ \= 1\. This eigenvalue corresponds to the stationary distribution of the chain: the probability distribution to which the chain converges if it is allowed to evolve indefinitely.

**Important: λ₁ ≈ 1 is not an anomaly**

In the initial analyses of this work (notebook 02\_permutation\_bootstrap.ipynb, cell 44), the dominant eigenvalue of the Voynich transition matrix was 0.9997, very close to 1\. This was initially interpreted as remarkable. In reality, it is mathematically unavoidable in any ergodic Markov chain. What matters for the analysis is not λ₁ but the difference between λ₁ and the second largest eigenvalue |λ₂|, which is called the spectral gap.

## **8.3 Spectral gap and mixing speed**

### **8.3.1 What does the spectral gap measure?**

The spectral gap δ \= λ₁ − |λ₂| measures the rate at which the Markov chain 'forgets' its initial state and converges to the stationary distribution. This rate of convergence is what is called the mixing time in Markov theory.

Intuitively: a large spectral gap means that the chain mixes quickly; that is, the current state predicts little about future states after a few steps. A small spectral gap means that the chain takes many steps to 'forget' its initial state, implying long-range dependencies.

**δ \= λ₁ − |λ₂| ; t\_mezcla ≈ 1 / δ** *(Spectral gap and mixing time)*

### **8.3.2 Relationship with the structure of language**

In the context of Voynich analysis, the spectral gap captures how far dependencies propagate between glyphs. A system with strong local morphology (prefixes combining with roots combining with suffixes) has dependencies confined within the word. Once the string crosses the word boundary, the correlation disappears, and mixing is rapid within the new context.

A monoalphabetic substitution cipher (Caesar) inherits the exact spectral gap of the ciphertext: changing A→N, B→O, etc., does not change the scrambling speed, it only renames the states. A polyalphabetic cipher (Vigenère) has a larger spectral gap (scrambles faster) because the key scrambles the patterns.

| Corpus | Vocab | λ₂ | Gap d | t\_mixture |
| :---- | :---- | :---- | :---- | :---- |
| **Voynich** | 166 | **0.459** | **0.541** | 1.8 steps |
| Medieval Latin | 26 | **0.342** | **0.658** | 1.5 steps |
| Caesar (ROT-13) | 26 | **0.342** | **0.658** | 1.5 steps |
| Vigenère | 26 | **0.145** | **0.855** | 1.2 steps |

The spectral gap of Voynich (0.541) is smaller than that of Latin (0.658), indicating slightly more persistent dependencies between glyphs. This is consistent with the strong local morphology observed in the positional MI analysis: Voynich glyphs have more 'memory' of their neighbors than Latin characters.

**The Voynich cipher is neither a Caesar nor a Vigenère cipher.**

If the Voynich cipher were a Caesar cipher over Latin, it would have exactly the same spectral gap as Latin (0.658), because the cipher only renames the glyphs. If it were a Vigenère cipher, it would have a larger gap (0.855). The Voynich cipher has a gap of 0.541, significantly different from both. This result, combined with the U-shape of the conditional entropy and the high positional MI, constitutes convergent evidence that the Voynich cipher is not a substitution cipher over Latin.

## **8.4 The eigenvector of λ₂ as a morphological diagnosis**

In addition to the eigenvalue λ₂, the corresponding eigenvector (the vector v₂ such that M·v₂ \= λ₂·v₂) has an interesting morphological interpretation. The glyphs with the greatest weight in v₂ are those that most 'differentiate' the two groups of states that take the longest to mix.

For the Voynich Manuscript, the glyphs with the highest weight in v₂ are Ys (0.114), Yp (0.049), Yn (0.019), Xd (0.018), and Tf (0.017). These are low-to-medium frequency glyphs that appear in specific positions and have highly predictable bigrams. Their presence in v₂ is the mathematical signature of glyphs with a marked positional distribution, consistent with the function of morphological markers (indicators of section, class, or derivation).

## **8.5 The relationship between the spectral gap and the U-shape**

There is a deep connection between the spectral gap (Block D) and the U-shape of the entropic curve (Block C/F). Both measure, from different angles, the extent of dependencies between glyphs.

The U-shape indicates that the context of 1 glyph predicts the next one well (low H₁), but the context of 3-4 glyphs predicts no better than that of 1 (high H₂-H₄). The spectral gap indicates that the sequence mixes in \~1.8 steps, meaning that after 2 glyphs, the current state predicts little about the future state.

These are two sides of the same coin: both point to a system where dependencies are strong within the word scale (1-2 glyphs) but rapidly attenuate. This consistency between two independent mathematical tools is cumulative evidence that we are measuring a real property of the system, not an artifact of the method.

**Chapter summary**

- A Markov chain models a sequence where the probability of the next element depends only on the current one. The transition matrix P collects these probabilities for all pairs of glyphs.

- The eigenvalues ​​of the transition matrix summarize its dynamic properties. The dominant eigenvalue λ₁ \= 1 is unavoidable in every ergodic chain; what is relevant is the spectral gap δ \= λ₁ − |λ₂|.

- The spectral gap measures the mixing speed: large gap → fast mixing → short dependencies. The approximate mixing time is t ≈ 1/δ steps.

- The Voynich cipher has a δ \= 0.541 (mixture in \~1.8 steps), different from Latin (0.658, \~1.5 steps) and very different from the Vigenère cipher (0.855, \~1.2 steps). A Caesar cipher over Latin would have exactly the gap of Latin.

- The spectral gap and the U-shape of conditional entropy are independent tools that converge on the same conclusion: Voynich dependencies are strong and local, confined to the range of 1-2 glyphs.

# **Chapter 9\. Neural Networks and Transformers: Intuition**

## **9.1 Why a neural language model**

The four previous analysis blocks (A, B, C/F, D, E) are statistical tests on specific properties of the text. We complement this analysis with a neural network model: a small Transformer trained on the Voynich corpus. The model is not the main analysis, but it provides two things that the statistical tests cannot: a learned representation of the glyphs (the embeddings) and a perplexity measure that captures the overall structure of the text in an integrated way.

This chapter explains the intuition behind the model's components, without delving into the complete mathematical derivations. The goal is for the reader to understand what the model learns and what that learning tells us about the Voynich Maneuver.

## **9.2 Embeddings: representing symbols as vectors**

### **9.2.1 The problem of representing discrete symbols**

Machine learning algorithms work with numbers, not symbols. To apply them to Voynich glyphs, we need a way to convert each glyph into a numerical vector. The simplest representation would be a vector of 166 zeros with a single 1 at the glyph's position (one-hot encoding). The problem is that this representation treats all glyphs as equally distinct from one another: A1 is no closer to A2 than it is to Q1.

Embeddings are a learned representation where each glyph is mapped to a vector of low-dimensional real numbers (32 in our model). The key is that learning adjusts these vectors so that glyphs that behave similarly in the text (appear in the same contexts, predict the same successors) have similar vectors.

### **9.2.2 What the Voynich embeddings reveal**

We applied Principal Component Analysis (PCA) to the learned embeddings to see how much structure is present in the representation space. PCA is a technique that finds the directions of greatest variance in a set of vectors, revealing the underlying low-rank structure.

Model v2 (n\_embd=32, the one we used in the final analysis) requires only 7 PCA components to explain 50% of the variance, compared to 15 in model v1 (n\_embd=128). This means that the representations of model v2 are more compact and specialized: the relevant information is concentrated in fewer dimensions.

The cosine similarity graph between embeddings, where we connect glyphs with cosine similarity \> 0.15 with edges, produces 3 communities detected with the Louvain algorithm that roughly correspond to the morphological categories: vowel suffixes, prefixes/roots, and function-free glyphs. This correspondence between the learned representation and the statistically observed morphological structure is an independent cross-validation.

**La convergence PPMI--Embeddings**

The graph constructed from pure statistical co-occurrence (PPMI: Positive Pointwise Mutual Information) and the graph constructed from Transformer embedding similarity produce similar communities. Two completely different methods—one purely statistical, the other based on learning—arrive at the same glyph clustering. This convergence is the most robust validation of morphological analysis: it is not an artifact of either method.

## **9.3 Transformer architecture: intuition**

### **9.3.1 The problem of variable context**

A language model must predict the next glyph given a context of variable length. Classical architectures (n-grams, LSTM) struggle to capture long-range dependencies or do so computationally expensively. The Transformer, proposed by Vaswani and colleagues in 2017, solves this problem with the self-attention mechanism.

### **9.3.2 Self-attention: each glyph looks at all the others**

The central idea of ​​the Transformer is that to predict the next glyph, the model can look at any position in the context with varying degrees of attention, learning which parts of the context are relevant to each prediction.

For each glyph in the context, the model calculates three vectors: Query (Q, 'what I'm looking for'), Key (K, 'what I offer'), and Value (V, 'the information I have'). The attention the current glyph pays to each previous position is proportional to the dot product of its Query and the Key of that position. The Values ​​of all positions are combined, weighted by these attentions.

**Attention(Q, K, V) \= softmax(Q·Kᵀ / √d\_k) · V** *(Self-attention mechanism)*

where d\_k is the dimension of the Keys, which normalizes the scalar product to avoid extremely small gradients during training.

### **9.3.3 VoynichLM v2 Model Hyperparameters**

The model we train has the following characteristics:

| Parameter | Value | Why this value? |
| :---- | :---- | :---- |
| Vocabulary (vocab\_size) | **167** | 166 glyphs \+ word separator '.' |
| Embedding dimension | **32** | Ratio 0.19× vocab \--- specialization strength |
| Heads of attention | **4** | 4 heads × 8 dims/head \= 32 total |
| Transformer Blocks | **3** | Minimum with compositional capacity |
| Context length | **64** | \~15 words of context |
| Total parameters | **50.791** | \~3.2× vocabulary size \--- no overfitting |
| Loss final (train / val) | **1.561 / 1.562** | Difference \< 0.001 \--- no memorization |

The most important piece of data in the table is that the validation loss (1.562) is virtually identical to the training loss (1.561) after 8,000 iterations. This means that the model generalizes: it hasn't memorized the corpus but rather learned its regularities. A model that memorizes would have a much lower training loss than its validation loss.

## **9.4 Perplexity as a measure of how well the model predicts**

Perplexity is the standard metric for evaluating language models. It is defined as two raised to the power of the model's cross-entropy loss: PPL \= 2^(loss). A perplexity of 2 means that the model is as good at predicting the next glyph as if it had to choose between two equally likely options at each step. A perplexity of 167 means that the model is no better than randomly choosing from all glyphs.

The loss of the VoynichLM v2 model is 1.562 bits, which corresponds to a perplexity of 2^1.562 ≈ 2.95. This means that, on average, the model predicts the next glyph as if it had to choose from approximately 3 options. Considering that there are 166 possible glyphs, this is a remarkable understanding of the text's structure.

For comparison, the zero-order entropy of the corpus is 4.14 bits (perplexity ≈ 17.7). The model, using contexts of up to 64 glyphs, reduces the uncertainty from 17.7 to 2.95: it absorbs more than 80% of the original uncertainty. This is consistent with a text that has a strong and predictable structure, not with random text.

**Chapter summary**

- The embeddings represent each glyph as a vector in a 32-dimensional space, so glyphs with similar behaviors in the text have similar vectors. The cosine similarity graph between embeddings produces 3 communities that correspond to morphological categories.

- The convergence between the co-occurrence graph (PPMI) and the embeddings graph cross-validates both methods: two independent approaches obtain the same structure.

- The Transformer's self-attention mechanism allows the model to look at any position in the context with different weight, learning which parts of the context are relevant to each prediction.

- The VoynichLM v2 model (50,791 parameters, 3 blocks, n\_embd=32) converges to loss=1,562 bits (perplexity ≈ 2.95) without overfitting: train loss ≈ val loss throughout the entire training.

- A perplexity of 2.95 out of 166 possible glyphs means that the model absorbs more than 80% of the uncertainty of the corpus, capturing the morphological structure of the writing system.

# **Chapter 10\. Combinatorial Optimization and Bayesian Inference**

Chapter 9 closed the phase of*characterization*We have measured the statistical fingerprint of Voynich and determined that a probabilistic syllabary is the most plausible generative mechanism. But characterization is not decipherment. If the Voynich syllables encode a real language, which one? This chapter develops the mathematical tools for Bayesian decipherment at the syllable level: how to find the optimal mapping between Voynich syllables and syllables of a candidate language, how to explore the solution space, and how to measure confidence in the result.

The approach is based on the work of Ravi and Knight (2011), who showed that substitution decryption can be formulated as a Bayesian optimization problem. Here we adapt their method to operate at the syllable level rather than the character level, incorporating positional class constraints (onset, nuclear, coda) and a multi-component scoring function.

## **10.1 The assignment problem: bipartite matching**

### **10.1.1 The formulation**

The deciphering of substitution at the syllabic level reduces to finding a bijective function*f*that maps each Voynich syllable*sv*to a syllable of the candidate language*st*so that the "translated" Voynich corpus is as natural as possible under the candidate language model. If the Voynich inventory has*n*functional syllable types and the candidate has*m*, the function*f*select one of the*m\!/(m−n)\!*possible matches \---an astronomical number even for modest inventories.

A crucial restriction reduces this space: Voynich syllables are classified into four positional classes (onset, nuclear, coda, free), and only syllables of the same class are allowed to be mapped. If a Voynich syllable is onset, it can only be mapped to an onset syllable of the candidate language. This partitions the problem into four independent subproblems, each much smaller than the entire problem.

### **10.1.2 The Hungarian (Kuhn-Munkres) algorithm**

The Hungarian algorithm solves the optimal assignment problem in polynomial time. Given a set of agents (Voynich syllables) and a set of tasks (candidate syllables) with a cost associated with each assignment, it finds the one-to-one assignment that minimizes the total cost.

Formally, given a cost matrix C of dimensions*n* × *m*where C\[i\]\[j\] is the cost of assigning the Voynich syllable*i*to the candidate syllable*j*The algorithm finds the permutation σ that minimizes:

*coste\_total \= Σᵢ C\[i, σ(i)\]*

The algorithm operates in O(n³) operations, making it tractable even for inventories of hundreds of syllables. It was developed independently by Harold Kuhn (1955) and James Munkres (1957), based on earlier work by the Hungarian mathematicians Dénes König and Jenő Egerváry.

### **10.1.3 Distributional vectors and cosine distance**

To construct the cost matrix of the Hungarian algorithm, we represent each syllable (both Voynich and candidate) as a 7-dimensional distributional vector:

1. Normalized frequency in the corpus  
2. Proportion of occurrence in word-start position  
3. Proportion in middle position  
4. Proportion in final position  
5. Forward entropy (log₂ of the number of distinct right contexts)  
6. Number of left contexts  
7. Number of legal contexts

The cosine distance between two vectors*in* and *in*Measure the angular difference between them:

*d\_cos(u, v) \= 1 − (u · v) / (||u|| · ||v||)*

where *u · v*is the dot product and ||u|| is the Euclidean norm. A value of 0 indicates vectors identical in direction; a value of 1 indicates orthogonal vectors. The cosine distance is ideal here because it is scale-invariant: two syllables with the same*distributional profile*but different absolute frequencies will have low cosine distance.

The Hungarian algorithm's result is an initial assignment that respects positional classes and matches syllables with similar statistical distributions. This assignment is a reasonable starting point, but it doesn't account for the text's sequential structure (which syllables tend to appear together). To incorporate that information, we need iterative optimization.

## **10.2 Expectation-Maximization (EM)**

### **10.2.1 The idea**

The EM algorithm (Dempster, Laird, and Rubin, 1977\) is an iterative technique for optimizing functions with latent variables—variables that we don't directly observe but that influence the data. In decryption, the latent variable is the mapping: we don't know which Voynich syllable corresponds to which syllable in the candidate language, but if we did, we could evaluate how well the resulting "translation" fits the candidate language model.

EM alternates between two steps:

**E-step (expectation)**Given the current mapping, "translate" the Voynich corpus into the candidate language and evaluate its naturalness under the bigram language model. This evaluation produces a score that measures the quality of the mapping.

**M-step (maximization)**: look for mapping modifications that improve the score. In the implementation adapted to our problem, this consists of testing swaps of syllable pairs within the same positional class and accepting those that improve the score.

### **10.2.2 Convergence**

The EM has a fundamental property: the score never worsens between iterations. Each M-step only accepts changes that improve the score, so the sequence of scores is monotonically non-decreasing. The algorithm converges when no swap improves the score—that is, when a local optimum is reached.

**The EM finds a local optimum, not necessarily a global one.**The result depends on the initialization, which justifies using the Hungarian algorithm as a starting point (which already provides a reasonable solution) and then refining with MCMC.

Convergence is detected using a patience criterion: if the score does not improve in*P*After consecutive iterations, the algorithm stops. In practice, with P \= 5 and 30 random swaps per class per iteration, EM typically converges in 10–20 iterations.

## **10.3 MCMC y Metropolis-Hastings**

### **10.3.1 The EM problem: local optima**

The EM is doomed to remain trapped at the nearest local optimum. If the solution space has many local optima—and it does with hundreds of syllables—the EM could converge to a mediocre solution simply because there is no single swap that improves it, even though a combination of several simultaneous swaps would.

This is where Bayesian inference using Markov chains Monte Carlo (MCMC) comes in. Instead of searching*and*Optimal mapping, MCMC samples from the posterior distribution over mappings, exploring both high-score regions and the transitions between them.

### **10.3.2 The Metropolis-Hastings algorithm**

The Metropolis-Hastings algorithm (Metropolis et al., 1953; Hastings, 1970\) is the workhorse of computational Bayesian inference. It constructs a Markov chain whose stationary distribution is the posterior distribution of interest. The chain explores the solution space by making random suggestions and accepting or rejecting them according to a precise rule.

The cycle is:

1. **Current state**: a complete mapping Voynich syllable → candidate syllable, with score*S\_actual*.  
2. **Proposal**: swap of two random Voynich syllables of the same positional class, producing a candidate mapping with score*S\_proposal*.  
3. **Decision**: to accept the proposal with probability:

*α \= min(1, exp((S\_proposed − S\_actual) / T))*

And*S\_propuesta \> S\_actual*(the proposal improves), it is always accepted (α \= 1). If*S\_propuesta \< S\_actual*(If the proposal worsens), it is accepted with exponentially decreasing probability in the magnitude of the worsening. The temperature*T*controls how much worsening is tolerated: with*T*High, significant deteriorations are acceptable; with*T*Low, only minor improvements or worsenings are accepted.

This acceptance rule is the key to MCMC: it allows escaping local optima by temporarily accepting worse solutions, in order to later explore regions of space that might contain better solutions.

### **10.3.3 Acceptance rate as a diagnosis**

The fraction of accepted proposals (acceptance rate) is a key indicator of chain health. A rate that is too high (\>60%) indicates that the chain is not exploring efficiently: almost all proposals are accepted, suggesting that the temperature is too high or that the swaps are too conservative. A rate that is too low (\<10%) indicates that the chain is stuck: almost all proposals are rejected, and exploration is minimal. The optimal range is between 15% and 40%, depending on the dimensionality of the problem.

## **10.4 Simulated annealing: el schedule de temperatura**

### **10.4.1 The metallurgical analogy**

Simulated annealing takes its name from metallurgy: when a metal is cooled slowly from a high temperature, the atoms have time to rearrange themselves into the lowest energy crystal configuration. If it is cooled too quickly, the atoms become trapped in disordered (metastable) configurations. The mathematical idea is identical: start with a high temperature that allows for extensive exploration, and gradually reduce it so that the chain is concentrated in the high-score regions.

### **10.4.2 The geometric schedule**

The most common temperature schedule—and the one used in our analysis—is the geometric one:

*T(t) \= T\_start · (T\_end / T\_start)^(t / (N − 1))*

where *t*is the current iteration (from 0 to N−1),*T\_start*is the initial temperature and*T\_end*This is the final temperature. The temperature drops exponentially, spending half the total time in the high-temperature phase (exploration) and the other half in the low-temperature phase (exploitation).

With *T\_start \= 1.0* and *T\_end \= 0.01*, el schedule produce:

| Phase | Iterations | Temperature | Behavior |
| :---- | :---- | :---- | :---- |
| Exploration | first \~40% | T \> 0.1 | Accepts worsenings of up to \~10% of the score |
| Transition | \~40-70% | 0.01 \< T \< 0.1 | Accept only minor deteriorations |
| Exploitation | last \~30% | T ≈ 0.01 | It practically only accepts improvements |

The advantage of annealing over fixed-temperature MCMC is that it combines global exploration (hot phase) with local optimization (cold phase). The disadvantage is that the result depends on the schedule: excessively rapid cooling traps the string at a local optimum, while excessively slow cooling wastes computation time on unnecessary exploration.

## **10.5 Multi-chain MCMC and Gelman-Rubin diagnosis**

### **10.5.1 Why multiple chains**

A single MCMC string can become trapped in one mode of the posterior distribution without exploring other equally probable modes. The standard solution is to run multiple independent strings, each with a different random seed. If all the strings converge to the same region of the space, we can be confident that the posterior is well-sampled. If they converge to different regions, there is evidence of multimodality, and the single-string posterior would be misleading.

In addition to diversification, multiple chains multiply the number of effective samples for the subsequent chain.*k*chains of*N*iterations and a burn-in period of*B*, the total number of post-burn-in samples is*k · (N − B)*In our analysis, 4 chains of 15,000 iterations with a burn-in of 3,000 produce 4 × 12,000 \= 48,000 samples, compared to 4,000 from a single chain of 5,000 iterations with a burn-in of 1,000.

### **10.5.2 Burn-in y thinning**

The first iterations of each MCMC chain are contaminated by initialization: the chain has not yet converged to the stationary distribution, and its samples are not representative of the later one. The burn-in period discards these initial samples.

How many iterations should be discarded? In practice, the score trace (score vs. iteration) is examined to identify the point at which the chain has reached a stable level. A conservative criterion is to discard the first 20% of the iterations.

Thinning is a complementary technique: storing only each*k*\-th sample instead of all of them. With 15,000 iterations × 4 strings × \~500 syllables per mapping, storing all the mappings would consume hundreds of megabytes. A thinning factor of 5 reduces memory consumption to one-fifth without significant loss of information, because consecutive MCMC samples are highly correlated.

### **10.5.3 The R-hat (Gelman-Rubin) diagnosis**

The R-hat diagnostic (Gelman and Rubin, 1992\) is the standard criterion for determining whether MCMC chains have converged. The idea is to compare the variance.*between*chains with the variance*within*of each string. If the strings have converged to the same distribution, both variances should be similar.

For each syllable Voynich*sv*A binary indicator is defined: does the string assign*sv*to its target MAP (the most likely target a posteriori) in this iteration? With this indicator, the following are calculated:

**Varianza within (W)**The mean of the variances of each individual chain. It measures how much the indicator fluctuates.*within*of each chain.

**Varianza between (B)**The variance of the chain means. It measures how much the chains differ.*each other*.

The estimator of the posterior variance is:

*V̂ \= (1 − 1/n) · W \+ (1/n) · B*

where *n*is the number of samples per chain. The R-hat diagnosis is:

*R̂ \= √(V̂ / W)*

**Interpretation**:

- *R̂ \= 1.0*Perfect convergence. The variance between is zero; all strings sample the same distribution.  
- *R̂ \< 1.1*: acceptable convergence. The standard of the Bayesian community (Gelman et al., 2013).  
- *R̂ \> 1.1*Insufficient convergence. The strings have not explored the same region of space; more iterations or reparametrization are needed.  
- *R̂ → ∞*: the chains are in completely different regions (variance within ≈ 0, variance between \> 0).

The R-hat is calculated per syllable, not globally. This allows us to identify which syllables have stable mapping (R̂ ≈ 1.0) and which remain ambiguous (R̂ \> 1.1). A useful summary is the percentage of syllables with R̂ \< 1.1: if this percentage is high (\>70%), most of the mapping has converged.

## **10.6 The multi-component scoring function**

### **10.6.1 Three complementary components**

Both EM and MCMC require a function that assesses the quality of a mapping. Our function combines three components that measure different aspects of language compatibility:

**Score LM (2.0 pesos)**: average log-likelihood of the Voynich corpus mapped under the candidate language bigram model. Measures whether the resulting syllable sequences "sound" like the candidate language.

**Score paradigm (peso 1.5)**It combines three sub-metrics evaluated using the Jensen-Shannon divergence (Chapter 7): (a) JSD between the Voynich and candidate paradigm size distributions, (b) fraction of mapped suffixes that exist in the candidate inventory, and (c) similarity of the paradigms' Gini coefficients. It measures whether Voynich morphology is preserved under mapping.

**Harmony score (weight 1.0)**JSD between joint distributions of (nuclear, coda) pairs in the mapped Voynich and in the candidate. Measures whether intra-word phonological dependencies are compatible.

*S\_total \= 2.0 · S\_LM \+ 1.5 · S\_paradigm \+ 1.0 · S\_harmony*

### **10.6.2 The Gini coefficient**

The Gini coefficient, used within the paradigm score, measures the inequality of a distribution. Originally developed by the Italian statistician Corrado Gini (1912) to measure economic inequality, it is applied here to the frequency distribution of suffixes within a paradigm.

For an ordered vector of frequencies (c₁ ≤ c₂ ≤ ... ≤ cₙ), the Gini coefficient is calculated as:

*G \= (2 · Σᵢ i · cᵢ) / (n · Σᵢ cᵢ) − (n \+ 1\) / n*

A value of 0 indicates perfectly uniform distribution (all suffixes equally frequent); a value of 1 indicates total concentration (a single suffix accounts for all frequencies). The Voynich paradigm has a Gini coefficient of 0.49, somewhere in between: the paradigms have a real variety of suffixes but with a few dominant endings. If a mapping produces paradigms with very different Gini coefficients (too uniform or too concentrated), the paradigm score penalizes it.

## **10.7 Posterior distribution and mapping confidence**

### **10.7.1 From the MCMC samples to the later**

Each sample of the MCMC string (after the burn-in) is a complete mapping. For each Voynich syllable*sv*We can count how many times each candidate syllable was assigned.*st*across all samples. The fraction of samples in which*sv* → *st*is an estimate of the posterior probability P(*st* | *sv*, data).

The candidate syllable with the highest posterior probability is the target MAP (maximum a posteriori). The posterior probability of the target MAP is the mapping confidence for that syllable: a confidence of 0.95 means that 95% of the MCMC samples assigned the same candidate syllable, indicating high certainty. A confidence of 0.30 means that the samples are split among multiple candidates, indicating ambiguity.

### **10.7.2 Confidence Thresholds**

The distribution of confidence levels across all syllables summarizes the overall quality of the mapping:

| Threshold | Interpretation |
| :---- | :---- |
| \>90% | Virtually safe mapping |
| \>70% | Reliable mapping; useful for text reconstruction |
| \>50% | Probable mapping; the target MAP is more probable than any single alternative |
| \<50% | Ambiguous mapping; multiple candidates have similar probability |

A low median confidence level (e.g., \~45%) does not necessarily mean the mapping is poor: it could mean the posterior distribution is multimodal (there are families of equally good mappings) or that the number of effective samples is insufficient. Upgrading from single-chain to multi-chain MCMC increases the number of effective samples and, consequently, the resolution of the posterior distribution.

**Chapter summary**

- Syllabic Bayesian decryption seeks the Voynich syllable → candidate syllable assignment that maximizes compatibility with the candidate language model, respecting positional class restrictions.

- He **Hungarian algorithm**(O(n³)) provides the optimal initial assignment based on the cosine distance between 7-dimensional distributional vectors.

- **IN**It iteratively refines the allocation: the E-step evaluates the mapped corpus under the LM target, the M-step applies swaps that improve the score. It converges to a local optimum.

- **MCMC Metropolis-Hastings**escapes local optima by accepting worsenings with probability*exp(ΔS/T)*The acceptance rate (15-40%) indicates the health of the chain.

- **Simulated annealing**cools the temperature geometrically from*T\_start* a *T\_end*, combining global exploration (hot phase) with local optimization (cold phase).

- **Multi-chain MCMC**executes*k*independent chains to multiply the effective samples (k × (N − burn-in)) and diversify the exploration.

- He **R-hat diagnosis**(Gelman-Rubin) compares between/within variance between strings: R̂ \< 1.1 indicates acceptable convergence.

- He **Gini coefficient**It measures the inequality of suffixes in paradigms: 0 \= uniform, 1 \= a single dominant suffix. The Voynich paradigm has a Gini coefficient of 0.49.

- The **posterior**It assigns a confidence level per syllable: the fraction of MCMC samples that match the target MAP. With 48,000 effective samples (4 strings × 12,000 post-burn-in), the resolution is 12× higher than a single string.

**Closing of Part II**

The six chapters in this part have built the complete mathematical arsenal that we will use in the analysis. Each tool has been presented with three elements: what it measures in general terms, why that measure is useful for the Voynich problem in particular, and what the first numerical results tell us.

It is worth pausing to note the argumentative architecture that emerges from these tools. They are not redundant: each one illuminates a different angle of the same object.

| Cap. | Tool | Angle that illuminates |
| :---- | :---- | :---- |
| **5** | **Entropy and mutual information** | How much structure is there and where is it located (positional vs. sequential) |
| **6** | **Permutation tests** | Is the structure real or could it be a random fluctuation? |
| **7** | **Chi-square and JSD** | If the structure varies with the thematic content |
| **8** | **Markov chains** | How far do dependencies spread between glyphs |
| **9** | **Transformer y embeddings** | Which internal representation is consistent with the corpus |
| **10** | **Optimization and Bayesian inference** | Which candidate language is syllabic mapping most compatible with? |

## **9.5 The statistical footprint and the distance metric**

The mathematical tools developed in this section—conditional entropy, permutation tests, chi-square and Jensen-Shannon divergence tests, Markov chains, neural networks, and Bayesian optimization—each produce numerical metrics that characterize a corpus. The set of these metrics forms what we call the statistical fingerprint of the corpus: a vector in a multidimensional space that captures its essential structural properties.

For the Voynich, the statistical fingerprint includes: the conditional entropy curve H₀ to H₄ (which exhibits the U-shape described in Section 5.5), the shape-derived metrics (bounce, decay), the spectral gap (Section 8.3), and the positional and bigram mutual information measures (Section 5.4). Together, these six metrics define a point in a six-dimensional space that distinguishes the Voynich from all other control systems.

### **9.5.1 Weighted Euclidean distance**

To quantify the similarity between two statistical fingerprints, we use the weighted Euclidean distance:

*d(A, B) \= √( Σᵢ wᵢ · (Aᵢ − Bᵢ)² )*

where Aᵢ and Bᵢ are the i-th components of the fingerprints of corpora A and B, and wᵢ is the weight assigned to the i-th component. The choice of weights allows emphasis on the metrics with greater discriminatory power.

| Weight Metric (wᵢ) Justification |
| :---- |

Rebound 3.0 The most distinctive property of the Voynich; unique among all the tested corpora

Decay 2.0 Quantifies the asymmetry of the entropy curve

MI positional 1.5 Glyph-position dependency in the word

My bigram 1.5 Dependence between adjacent glyphs

Spectral gap 1.0 Markov chain mixing speed

|  |
| :---- |
| The rebound receives the highest weight (w=3) because it is the most distinctive property of the Voynich: no other tested system—nor the |

### **9.5.2 Generative models as a testbed**

A direct application of the statistical footprint is the forward modeling methodology: constructing generative models with known mechanisms, generating synthetic corpora from each model, calculating its statistical footprint, and measuring the distance to the Voynich manuscript. The model whose footprint is closest suggests the most plausible mechanism behind the manuscript.

This methodology reverses the usual approach to cryptographic analysis: instead of attempting to decipher an existing ciphertext, we synthesize text under controlled hypotheses and observe which one best reproduces the statistical properties of the original. If a generator based on a probabilistic syllabary produces a fingerprint close to the Voynich manuscript, this constitutes evidence that the manuscript was produced by a syllabic-type mechanism. Chapter 14 of Part III elaborates on this methodology with eleven generative models—seven of our own and four based on hypotheses from the literature (Rugg 2004, Timm and Schinner 2020, Hermes 2022, Greshko 2025).

### **9.5.3 Sensitivity analysis: Spearman correlation and Dirichlet sampling**

The choice of weights in the weighted distance is subjective. To verify that the conclusions are robust to this choice, Chapter 14 includes a sensitivity analysis that uses two additional mathematical tools.

**Spearman rank correlation.**Spearman's rank correlation (ρ) measures the monotonic association between two rankings. Given two rank vectors R and S of length n, it is defined as:

*ρ \= 1 − (6 Σ dᵢ²) / (n (n² − 1))*

where dᵢ \= Rᵢ − Sᵢ is the difference in ranks of the i-th element. The value ρ \= 1 indicates identical rankings; ρ \= 0 indicates no correlation; ρ \= −1 indicates inverted rankings. Unlike Pearson's correlation (which measures linear association between values), Spearman's operates on ordinal ranks and is insensitive to monotonic transformations of distances. This makes it ideal for assessing whether the*order*The ranking is preserved when the weights change, regardless of how much the absolute values ​​of the distances change.

In our analysis, we calculated ρ between the base ranking (with the chosen weights) and the ranking produced by each alternative set of weights. If ρ \> 0.9 consistently, the ranking is robust: the winning model does not depend on the specific choice of weights.

**Dirichlet distribution.**To explore the weight space exhaustively, we generate sets of random weights sampled from a symmetric Dirichlet distribution. The Dirichlet distribution is a probability distribution over vectors of k positive components that sum to 1\. With concentration parameter α \= 1 (uniform distribution over the simplex), each component has the same marginal distribution and there is no preference for any particular weight.

Formally, if (x₁, ..., xₖ) \~ Dir(α₁, ..., αₖ), the density is:

*f(x₁, ..., xₖ) \= \[Γ(Σ αᵢ) / Π Γ(αᵢ)\] · Π xᵢ^(αᵢ−1)*

where Γ is the gamma function. With α₁ \= ... \= αₖ \= 1, all weight vectors in the simplex are equally probable. The vectors are rescaled to maintain the total magnitude similar to that of the basis weights (sum ≈ 9).

By generating hundreds of sets of Dirichlet weights and calculating the ranking under each, we obtain an empirical distribution of ρ and a frequency of "wins" for each model: how many times it occupies the first position (top-1) or is among the top three (top-3). If a model dominates top-1 with high frequency (\>50%) under completely random weights, its ranking position is not an artifact of the weight choice.

When these six tools, applied to the same data, converge on the same diagnosis, the evidence is far more robust than if it came from a single technique. This convergence—or its absence—is the central argument of Parts III and IV.

*\--- Continued in Part III: Analysis and Results \---*


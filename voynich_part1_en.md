COMPUTATIONAL ANALYSIS OF

# **VOYNICH MANUSCRIPT**

*Natural language, encryption, or artificial system? An investigation from the perspectives of information theory, machine learning, and computational statistics*

| Format: | Research paper |
| :---- | :---- |
| **Language:** | Spanish |
| **Version:** | Part I of XI \--- Context and Introduction |
| **Corpus:** | STA1 2.0 \--- Voynich Manuscript (37,087 words, 157,254 glyphs) |
| **Tools:** | Python 3.12 · PyTorch · scikit-learn · NumPy · NetworkX |
| **Source code:** | 01\_statistical\_fingerprint.ipynb · 02\_permutation\_bootstrap.ipynb · 03\_entropy\_spectral.ipynb · 04\_multilingual\_controls.ipynb · 05\_generative\_models.ipynb · 06\_bayesian\_syllabic.ipynb · 07\_compositional.ipynb · 08\_validation.ipynb · 09\_constrained\_em.ipynb |

*\--- Part I: Context and Introduction \---*

# **Preface**

This work stemmed from a seemingly simple question: can a machine say anything useful about the most mysterious text in history? The answer, as with everything interesting, turned out to be complicated.

The Voynich Manuscript has resisted all attempts at decipherment for over a century. Cryptographers, linguists, historians, mathematicians, and enthusiasts from around the world have tried to read it. Some have claimed to have deciphered it. None have convinced the scientific community. This work does not aim to decipher it either. What it does aim to do is apply modern mathematical and computational tools to answer a more modest but more rigorous question: what kind of system is the Voynich text? Does it behave like a natural language? Like a cipher? Like something else?

The document is written for a reader who may have a background in linguistics, history, or statistics, but not necessarily all three. Therefore, each mathematical tool used in the analysis is explained from its foundations: not how its formula is derived, but what it measures, why that measure is useful for our problem, and what its specific result tells us about the Voynich Manuscript.

The code that produces all the results in this work is available in nine Python notebooks. Whenever a number or graph is cited, the cell that generated it and how to interpret it are indicated. Reproducibility is not an academic luxury; it is the only way to ensure that the results are truly arguments and not mere assertions.

This is the first of seven volumes. Here, the historical and scientific context is established, the corpus being analyzed is described, and the research question is precisely stated. Subsequent volumes develop the mathematical foundations (Part II), the results of the analysis (Part III), syllabic segmentation (Part IV), Bayesian syllabic decryption (Part V), compositional decryption (Part VI), and validation with grammatical constraints (Part VII).

# **Chapter 1\. The Voynich Manuscript: History and Description**

## **1.1 Physical description**

The Voynich Manuscript is a parchment manuscript containing approximately 240 folios, although it is believed to have originally had more pages, some of which have been lost. It is small in size, about 23 by 16 centimeters, and is bound in a leather cover that is probably not the original. It is currently housed in the Beinecke Rare Book and Manuscript Library at Yale University, where it is cataloged as MS 408\.

Radiocarbon dating, carried out in 2011 on parchment samples, places its creation between 1404 and 1438\. This situates it in the 15th century, during the early Renaissance. The text is written in dark brown ink, with some additions in red. The illustrations, which occupy a considerable portion of the volume, include fantastical or unfamiliar plants, astronomical or astrological diagrams, female figures in what appear to be pools or bathtubs connected by tubes, and tables with stars and symbols.

The writing system is completely unknown. It has not been identified with any known alphabet. The symbols, which in this work we will call glyphs, have an appearance that remotely evokes medieval Latin or Arabic, but are neither. There are approximately 25 to 30 basic glyphs, although the number varies depending on the transcription system used. The text is written from left to right, with reasonably regular margins and no visible punctuation.

**Why the name 'Voynich'?**

The manuscript takes its name from Wilfrid Voynich, a Polish-American bookseller who acquired it in 1912 from the Jesuit Villa Mondragone in Frascati, Italy. Voynich actively promoted it in academic and scientific circles, although its exact provenance before 1912 is somewhat uncertain. In 1969, his widow donated it to bookseller Hans Kraus, who in turn gave it to the Beinecke Library in 1969\.

## **1.2 History of the transmission of the manuscript**

The documentary trail of the Voynich manuscript truly begins with a 1666 letter from the Bohemian scholar Johannes Marcus Marci to the Jesuit Athanasius Kircher in Rome, requesting his assistance in deciphering it. In the letter, Marci mentions that the book had previously belonged to Emperor Rudolf II of Habsburg, who supposedly paid six hundred gold ducats for it—an enormous sum at the time, suggesting that it was already considered to be of special importance.

Before Rudolf II, the history of the manuscript is speculative. Marci's letter also mentions the name of Roger Bacon, the 13th-century English Franciscan friar known for his interests in natural philosophy and alchemy, as a possible author. This attribution has been much debated, and most modern researchers consider it unlikely, not least because radiocarbon dating places Bacon more than a century later.

Between 1666 and 1912, the manuscript remained in the archives of the Society of Jesus, probably at Villa Mondragone. When Voynich acquired it, as part of a collection of manuscripts that the Jesuits were discreetly selling, the modern history of the Voynich Manuscript as an object of public and scholarly fascination began.

| Approximate date | Event |
| :---- | :---- |
| 1404--1438 | Creation of the manuscript (radiocarbon dating of 2011\) |
| \~1580--1612 | Possession by Rudolf II of Habsburg (according to Marci's letter) |
| 1666 | Johannes Marcus Marci sends it to Athanasius Kircher in Rome |
| 1666--1912 | Archives of the Society of Jesus, Villa Mondragone (Frascati) |
| 1912 | Wilfrid Voynich acquired it and made it known in academic circles |
| 1969 | Donated to the Beinecke Library, Yale University (MS 408\) |
| 1991 | First facsimile edition published (Interrorum Publishers) |
| 2004 | Complete digitization and open access by Yale |
| 2011 | Radiocarbon dating: parchment created between 1404 and 1438 |

## **1.3 The illustrations and their sections**

Although the Voynich text has not been deciphered, the illustrations have allowed researchers to divide the manuscript into thematic sections with reasonable confidence. This division is important for our analysis because one of the tests we conducted specifically asks whether the glyph vocabulary varies between sections, something we would expect if the text reflected different content.

The main sections recognized by research tradition are the following:

| Section | Approximate number of pages | Description of the illustrations |
| :---- | :---- | :---- |
|  | **Herbal** | f1--f66, f85--f98 | Plants with elaborate roots, leaves, and flowers. Most do not correspond to known botanical species, although some have been tentatively identified. |
|  | **Astronomical** | f67--f69 | Concentric circular diagrams with stars, symbols, and female figures. Possible representations of constellations or calendars. |
|  | **Zodiac** | f70--f73 | Circles with the signs of the zodiac and nude female figures inside. One of the few elements that can be identified with certainty. |
|  | **Biological** | f74--f84 | Female figures in bathtubs or pools connected by tubes. Their interpretation is particularly controversial: spas, alchemy, and anatomy have all been suggested. |
|  | **Pharmaceutical** | f88--f102 | Containers, jars, and vessels of various shapes, alongside illustrations of plants. Possible recipes or inventories of ingredients. |
|  | **Recipes** | f103--f116 | Dense text with few illustrations. It resembles lists or recipes. It is the most text-dense section. |

*Note: The section division used in our analysis follows the standard mapping of the STA1 2.0 transcript, which assigns each folio to a section according to its number. The astronomical and zodiac folios are not included in the semantic differentiation tests due to their small size (the astronomical section has only 1,342 words, insufficient for the classification tests).*

## **1.4 The writing system**

The most perplexing aspect of the Voynich Manuscript is not its illustrations but its text. It appears to have all the properties of a written language: symbols that combine regularly, forming units separated by spaces (which we interpret as words), and these units have varying lengths but are distributed similarly to the words in natural languages. Yet, no one has been able to decipher it.

Some features of the writing system are particularly striking to a linguist or a statistician:

- The words are surprisingly short. The average length is about four or five units (glyphs), well below the average for medieval Latin or Arabic.

- Some glyphs appear almost exclusively at the beginning of words, others almost exclusively at the end. This pattern, which we will see quantified in detail later, is reminiscent of the behavior of prefixes and suffixes in morphologically rich languages.

- The vocabulary of distinct words is relatively small compared to the size of the corpus. Many words are frequently repeated, but there are also a large number of words that appear only once.

- There is a curious internal uniformity: the text appears to have been written by a single hand, or at most two, with a very consistent style throughout the 240 pages.

**The problem of hapaxlegomena**

In linguistics, a 'hapax legomenon' (plural: hapax legomena) is a word that appears only once in the entire corpus. Natural languages ​​have a characteristic proportion of hapax: in long texts, between 40% and 60% of distinct words are typically hapax. The Voynich Manuscript has an unusually high proportion of hapax, which some researchers have interpreted as evidence of a fabricated vocabulary and others as evidence of a text that is more information-dense than normal.

# **Chapter 2\. State of the art: one hundred years of attempts**

## **2.1 The major hypotheses**

In over a century of research, the hypotheses about the Voynich Manuscript have been organized into four main categories. None has definitively convinced the academic community, but each has provided partial evidence that any serious analysis must consider.

### **2.1.1 Encryption Hypothesis**

The most persistent hypothesis, especially among cryptographers, is that the Voynich manuscript is a text in a known language, protected by some kind of cipher. Proposed cipher types range from simple substitutions (each glyph representing a Latin or Arabic letter) to more elaborate systems such as polyalphabetic substitution ciphers, nomenclator codes, or combined shortening and substitution systems.

During World War II, the Voynich Manuscript was studied by professional cryptographers from the U.S. Navy and Marine Corps, including William F. Friedman, considered the father of modern American cryptology. Friedman and his team, who had access to tools and methods that had broken highly sophisticated military ciphers, were unable to crack the Voynich Manuscript. Friedman privately concluded, in his personal notes, that the manuscript might not be decipherable using classical techniques because it might not be based on any natural language.

A fundamental problem with the simple cipher hypothesis is that modern statistical tools, including those used in this work, should detect residual patterns of the underlying language even after applying a substitution. If the Voynich were a Caesar or Vigenère cipher over Latin, its entropy curves should resemble those of Latin. As we shall see, this is not the case. Recently, Greshko \[2025\] proposed the Naibbe cipher, a verbose homophonic cipher that can be run by hand on 15th-century materials and which, when applied to Latin and Italian, reproduces several statistical properties of the Voynich. Our quantitative implementation (Chapter 14\) confirms that Naibbe is the closest model in the literature to the Voynich (d=1.028), with a significant bounce (0.554) and good bigram IM (1.725), but with a null positional IM (0.001), suggesting that a historically plausible cipher cannot be completely ruled out but also does not reproduce the full fingerprint.

### **2.1.2 Constructed Language Hypothesis**

John Dee, the mathematician and astrologer at the court of Elizabeth I of England, and his associate Edward Kelley held séances in the 1580s in which they claimed to receive dictation in an angelic language they called Enochian. Some researchers have suggested that Voynich may be an early example of a constructed language—that is, a linguistic system deliberately invented for philosophical, religious, or cryptic purposes.

This hypothesis has gained some modern support. Linguist Stephen Bax published an analysis in 2014 proposing tentative readings for some glyphs and words, suggesting a possible underlying Semitic language. However, his results have not been independently replicated. More recently, in 2019, researcher Gerard Cheshire proposed that the Voynich manuscript is written in Proto-Romance, a medieval Mediterranean dialect. This hypothesis was widely criticized by medievalists and linguists.

### **2.1.3 Hypothesis of nonsense**

The most radical hypothesis, proposed by Gordon Rugg \[2004\] among others, is that Voynich simply means nothing. Rugg showed that it is possible to generate text with the superficial statistical properties of Voynich using a Cardan table, a 16th-century cipher device that mechanically combines prefixes, roots, and suffixes. The resulting text appears coherent at first glance but does not encode any message. Rugg and Taylor \[2017\] extended this result by showing that the method also replicates quantitative properties such as the Zipf distribution and word-length distributions.

In partial support of this line of thought, Gaskell and Bowern \[2022\] recruited 42 volunteers to write nonsense texts and found that Voynich is statistically more similar to human gibberish than to meaningful text across several metrics (low entropy, high repetition, character positional bias). Similarly, Schinner \[2007\] concluded that the text's properties are more consistent with gibberish produced by a quasi-stochastic method than with natural languages.

This hypothesis has the merit of explaining why no one has been able to decipher the manuscript, but it faces a serious problem: a mechanically generated text using random combinations should have a different statistical profile than the Voynich Manuscript in certain tests of deep structure. Precisely, the positional mutual information analysis we performed in this work was designed to distinguish between text with real morphological structure and text generated by mechanical slots. In fact, our quantitative implementation of Cardan's table (Chapter 14\) shows that this mechanism produces the corpus furthest removed from the Voynich Manuscript of all the models tested (d=4.485), with a decay of 75.5% (vs. 8.9%), a bigram MI of 5.087 (vs. 1.681), and a positional MI of 1.075 (vs. 0.658): the table generates a text that is too regular and predictable.

### **2.1.4 Partially Encrypted Natural Language Hypothesis**

A fourth, and arguably intermediate, hypothesis is that the Voynich cipher combines a natural language with an encoding system that is not a pure cipher but rather a non-standard transliteration. Under this hypothesis, the glyphs are not letters of a cipher alphabet but symbols representing syllables, morphemes, or entire words of some language, possibly with an idiosyncratic system developed by the author. Hermes \[2022\] has documented that Johannes Trithemius's Polygraphia III cipher, applied as a random procedure, produces text that mimics the statistical properties of the Voynich cipher and presents itself as an artificial language, providing a concrete historical precedent for this type of system. However, our quantitative implementation (Chapter 14\) shows that Polygraphia III destroys the positional structure within the word (MI\_pos≈0 vs. 0.658 for the Voynich cipher), which limits its plausibility as a complete generative mechanism.

This hypothesis is consistent with the results we will present: Voynich has more positional structure than a typical natural language but less than a rigid slot system. Its dependencies between glyphs are very strong at short range (within the word) but attenuate rapidly. This can be interpreted as a system where words have predictable internal morphology but the lexical vocabulary is opaque.

## **2.2 Previous statistical findings**

Beyond the hypotheses about the content, the research community has accumulated a body of statistical results on the formal properties of the text that any analysis must take into account.

### **2.2.1 Zipf's law and entropy**

Jorge Stolfi \[2000–2012\], one of the researchers who has contributed most to the statistical study of the Voynich Manuscript, demonstrated that the text follows Zipf's law: if we order the words by frequency, the frequency of the nth word is approximately proportional to 1/n. Landini \[2001\] confirmed this result with spectral analysis and also showed that character autocorrelation is consistent with a cipher language. This law holds true for virtually all known natural languages. Its observable nature in the Voynich Manuscript provides moderate evidence that it is not a completely random text, although it can also be verified in certain artificially generated texts \[Rugg and Taylor, 2017; Timm and Schinner, 2020\].

Shannon entropy analysis of the Voynich Manuscript, which measures the uncertainty in each symbol given its context, yields values ​​that fall between those of natural languages ​​and those of a random text. Bennett \[1976\] was the first to apply entropy analysis to the manuscript, finding that the second-order entropy is considerably lower than that of most comparison languages, with values ​​similar only to some Polynesian languages. Prescott Currier \[1976\] extended these findings, and Lindemann and Bowern \[2020\] extended them to 316 comparison texts, finding that the conditional character entropy of the Voynich Manuscript is*"distinctly lower than any of the 316 comparison texts"*In our analysis we confirm this with greater precision and extend it to higher-order conditional entropies, where we identify the characteristic U-shape that is not documented in the previous literature.

### **2.2.2 The Courier Groups**

Prescott Currier \[1976\], a U.S. Navy cryptanalyst, observed that the Voynich text can be divided into two statistically distinguishable groups, which he called group A and group B. The folios in group A tend to have longer words and a different vocabulary than the folios in group B. This difference is marked enough to be automatically detected.

The most common interpretation of Currier's groups is that they reflect different sections of the manuscript (the herbal/biological/recipe division mentioned earlier), possibly written at different times or for different purposes. Some researchers have proposed that the two groups were written by different hands. Our analysis of semantic differentiation between sections (Block E) is a modern and more granular version of Currier's original analysis.

### **2.2.3 Results of modern computational analysis**

In the last decade, several groups have applied advanced quantitative techniques to the Voynich Manuscript. Montemurro and Zanette \[2013\] analyzed the long-range structure of the manuscript using Shannon entropy methods and identified networks of semantic keywords distributed across sections, providing strong evidence for a genuine message. Amancio et al. \[2013\] compared the Voynich Manuscript with the New Testament in 15 languages ​​using first-order statistics, complex network topology, and intermittency analysis, concluding that in 90% of cases the statistical properties of the Voynich Manuscript are compatible with genuine texts.

Stolfi \[2000–2012\] identified the positional “paradigms” of the Voynich script: certain glyphs are exclusive to the initial position, others to the final position, and others to the middle position, proposing a three-layer model (cortex, mantle, core). Matlach, Janeckova, and Dostal \[2022\] extended this analysis by exploring the possibility that some glyphs are compounds or ligatures, suggesting that the effective alphabet could be much smaller than it appears.

Regarding the identification of the underlying language, Hauer and Kondrak \[2016\] applied automatic decryption methods to 380 languages ​​and suggested Hebrew as the source language, although the result was criticized for the inadequacy of models trained on modern languages ​​for a 15th-century manuscript. Lindemann \[2022\] applied the Moving Average Type-Token Ratio (MATTR) and found that the morphological complexity of Voynich lies between that of Romance/Germanic and Semitic/Slavic languages, with the nearest proximal centroid in the Iranian family. Babaahmadi \[2019\] applied a hidden Markov model with two internal states and found that the transitions identify vowel- and consonant-equivalent regimes, with frequencies similar to those of natural languages.

Regarding generative models, Timm and Schinner \[2020\] proposed a "self-citation" algorithm where the scribe would copy and modify previous words in the manuscript, reproducing both of Zipf's laws. Our quantitative implementation (Chapter 14\) shows that self-citation produces good bigram correlations (MI\_big \= 1.836) but a low bounce (0.120) and a distance of d \= 1.356 to the Voynich Manuscript. Timm and Schinner \[2024\] reviewed the debate at the International Conference on the Voynich Manuscript (Malta, 2022). Reddy and Knight \[2011\] provided a synthesis of computational linguistics that documented both linguistically aberrant properties (lack of repeated bigrams, anomalous line-edge distributions) and properties conforming to natural language (length distributions, frequency distributions, apparent morphology).

The most comprehensive review to date is that of Bowern and Lindemann \[2021\], which systematically evaluates the linguistic arguments for and against the Voynich encoding a natural language, concluding that the statistical evidence favors a genuine linguistic substrate.

None of these studies, however, has systematically combined multiple independent statistical tests with formal controls (permutation tests, folio holdout, comparison with known ciphers and languages ​​from four distinct language families) to produce a comprehensive scorecard of evidence, nor has it applied forward modeling with multiple generative models—including quantitative implementations of the hypotheses of Rugg \[2004\], Timm and Schinner \[2020\], Hermes \[2022\], and Greshko \[2025\]—to identify which mechanism reproduces the statistical footprint of the Voynich Manuscript. This is precisely the aim of our work.

## **2.3 Limitations of the state of the art**

The field of Voynich studies suffers from several recurring methodological problems that this work attempts to avoid. It is worth explicitly naming them because they help to explain why so many previous analyses have failed to convince the scientific community.

- Analytical circularity: discovering a pattern in the data and then validating it in the same data. That's why we use holdout by folio (Block B): the rules are discovered in one half of the corpus and validated in the other half.

- Lack of controls: comparing the Voynich cipher only with itself, without comparing it with known natural languages ​​and ciphers under the same tests. In our analysis, each Voynich result is contextualized with eight control corpora: Medieval Latin, Caesar cipher, Vigenère cipher, Biblical Hebrew, Quranic Arabic, Turkish, and Finnish.

- Hypothesis confirmation: Select the tests that support the preferred hypothesis and ignore those that contradict it. We report all results, including those that are ambiguous or that initially pointed in the wrong direction.

- Overinterpretation of partial evidence: claiming that the manuscript has been deciphered based on a few tentative lexical matches. We carefully distinguish between what the data can and cannot prove.

# **Chapter 3\. The Corpus: STA1 2.0 and its Preprocessing**

## **3.1 The problem of transcription**

To apply any statistical or computational analysis to the Voynich manuscripts, the handwritten glyphs must first be converted into symbols that a computer can process. This seemingly trivial step introduces decisions that profoundly affect the results.

The central problem is that there is no consensus on how many distinct glyphs exist in the Voynich Manuscript. Depending on how allographic variants (symbols that appear to be variations of the same basic glyph) are treated, the inventory can range from 20 to more than 50\. A transcription that groups many variants together will produce a smaller vocabulary and shorter words. A transcription that distinguishes more variants will produce the opposite effect. This decision is not neutral: it can make the text appear more or less like a natural language.

Throughout the 20th century, several transcription systems were developed. The most widely used are the EVA (European Voynich Alphabet), proposed in 1998 by René Zandbergen and Gabriel Landini, and the STA (Stolfi-Takahashi Alphabet), proposed by Jorge Stolfi. This work uses Stolfi's STA1 2.0 version, which is open access and produces a well-documented glyph vocabulary.

## **3.2 The STA1 2.0 Transcription**

The STA1 2.0 system encodes each glyph as a two-character token: an uppercase letter that identifies the glyph family, followed by a digit or lowercase letter that indicates the variant. For example, A1, A2, and A3 are variants of the same 'A' glyph family; Q1 and Q2 are variants of the 'Q' family.

This encoding has an important consequence for computational analysis: the resulting vocabulary size is 166 distinct glyphs (plus the word separator '.'), which is a number large enough to capture the variety of the writing system but small enough for statistical tests to be statistically powerful.

**A critical error we found during the analysis**

In the first version of our preprocessing code (notebook 01\_statistical\_fingerprint.ipynb), a bug in the parser was producing 9,762 unique tokens instead of 166 because the code was concatenating the glyphs instead of separating them. This bug contaminated all entropy tests and Markov chain analyses, producing absurd results (entropies that increased with context, which violates a fundamental mathematical law). Detecting and correcting this bug was an important lesson about the importance of validating data before interpreting results. The correct, validated parser is in notebook 02\_permutation\_bootstrap.ipynb, cell 1\.

## **3.3 The validated parser**

The correct parser extracts glyphs using the following regular expression:

glyphos \= re.findall(r'\[A-Z\]\[0-9a-z\]', palabra\_raw)

This expression searches for the exact combination of an uppercase letter followed by a digit or lowercase letter, which is the format of all STA1 tokens. The complete process for each line of the transcript file is:

1. Ignore empty lines, comments (starting with \#), and folio metadata.

2. Extract the text content that follows the position tag with re.match(r'^\<\[^\>\]+\>\\s+(.\*)', line).

3. Clean internal tags and convert hyphens to periods (hyphens in STA indicate word separation).

4. Divide the resulting text by '.' to obtain individual words.

5. For each word, apply findall to extract the glyphs and add '.' as a word end marker.

## **3.4 Corpus Statistics**

The corpus processed with the validated parser has the following properties:

| Property | Value |
| :---- | :---- |
| Total tokens (glyphs \+ separators) | **194 341** |
| Total number of glyphs (without separators) | **157 254** |
| Total number of words (units separated by '.') | **37 087** |
| Unique vocabulary (distinct glyphs) | **166** |
| Word separator '.' | **Included as token 0 in the vocabulary** |
| Glyphs with frequency ≥ 5 | **76 (46% of the vocabulary)** |
| Glyphs with frequency \< 5 (hapax and rare) | **91 (54% of the vocabulary)** |
| Average word length | **\~4.2 glyphs** |
| Minimum word length | **1 glyph** |
| Maximum observed word length | **\~12 glyphs** |

## **3.5 Section Mapping**

In addition to the flat corpus, for semantic differentiation analysis we need to know which section each word belongs to. The notebook 02\_permutation\_bootstrap.ipynb (cell 14\) implements a function that reads the folio number of each document directly from the transcript metadata and assigns it to a section using standard ranges:

| Section | Folios | Words | Glyphs |
| :---- | :---- | :---- | :---- |
|  |  | herbal | f1--f66, f85--f98 | **14 278** | **58 832** |
|  |  | recipes | f103--f116 | **10 606** | **45 661** |
|  |  | organic | f74--f84 | **6 768** | **28 911** |
|  |  | pharmaceutical | f88--f89, f99--f102 | **2 505** | **10 652** |
|  |  | zodiac | f70--f73 | **1 588** | **7 327** |
|  |  | astronomical | f67--f69 | **1 342** | **5 871** |
|  |  | **TOTAL** | **226 pages** | **37 087** | **157 254** |

*Methodological note: In the section classification tests (Block E), the astronomical and zodiacal sections are excluded because their small size (less than 2,000 words) makes the classification tests statistically weak. The analysis uses the four main sections: herbal, recipes, biological, and pharmaceutical.*

## **3.6 The control corpus: Medieval Latin and ciphers**

A basic principle of statistical analysis is that a result only has meaning in relation to a reference point. The fact that the Voynich cipher has an entropy of 4.14 bits tells us nothing by itself; it tells us a lot when we know that medieval Latin has 4.12 bits and that a Vigenère cipher has 4.62 bits.

For all the tests we performed, we compared the Voynich corpus with three control corpora:

- Medieval Latin (Vulgate): downloaded from Project Gutenberg (text \#8300). The Vulgate is the Latin translation of the Bible, primarily by St. Jerome, in the 4th century, which was the standard Latin text throughout the Middle Ages. It is the best available proxy for the Latin used in the Voynich period and geographical context.

- Caesar cipher (ROT-13 over Latin): a simple monoalphabetic substitution cipher where each letter is replaced by the letter 13 positions later in the alphabet. It is the simplest possible cipher and represents the lower limit of cryptographic sophistication.

- Vigenère cipher (from Latin, key 'voynich'): a polyalphabetic cipher where the key defines which substitution applies to each position. It is significantly more difficult to break than the Caesar cipher and was considered unbreakable for centuries. It represents a more realistic level of cryptographic sophistication for the 15th century.

**Why encrypt Latin and not Spanish?**

We use Latin as the source text for the ciphers because if the Voynich Manuscript were a cipher of a medieval text, that text would most likely be in Latin. Ciphering modern Spanish and comparing it to the Voynich Manuscript would introduce an unjustified historical asymmetry. Furthermore, Latin and the Voynich Manuscript share the same historical period and roughly the same cultural sphere.

## **3.7 Limitations of the corpus**

Before proceeding with the analysis, it is important to be explicit about the limitations of the corpus we are using. Honesty regarding these limitations does not weaken the conclusions; on the contrary, it makes them more robust because it clearly defines what can and cannot be stated.

- The STA1 2.0 transcription is not perfect: there are parts of the manuscript that are difficult to read where the transcriber has had to make interpretive judgments. The results may vary slightly with other transcriptions.

- We don't know if the transcription captures all the relevant distinctions of the original writing system. If two glyphs that the transcription treats as the same are actually distinct to the manuscript's author, our analysis will ignore them.

- The corpus contains only approximately 37,000 words. This is sufficient for our tests, but significantly smaller than the corpora used in serious linguistic studies (which typically contain millions of words). This increases the statistical variance of some estimates.

- The assignment of folios to thematic sections is conventional, not universal. Some researchers use different divisions. Our results on semantic differentiation depend in part on this division.

# **Chapter 4\. The Research Question**

## **4.1 Precise formulation of the problem**

Before applying any statistical tool, it is essential to formulate precisely what question is being answered. Vague questions produce vague answers. 'The Voynich Manuscript has language-like properties' is not a scientific statement because it does not specify what properties, in what sense it is similar, or compared to what.

The research is structured around one main question and three derived sub-questions:

**Main research question**

What type of generative system is compatible with the statistical footprint of the Voynich Manuscript?

Specifically: are the statistical properties of the text—positional glyph structure, contextual dependencies, Markov mixing speed, and semantically differentiated vocabulary by section—more consistent with those of a natural language with morphology, with those of a substitution cipher applied to a natural language, or with those of some other generative mechanism?

**Subquestion 1 — Typological diagnosis**

Does the Voynich statistical profile group with any known language family (Indo-European, Semitic, agglutinative) or does it lie outside the space of variation of natural languages? To answer this, we compare Voynich with six languages ​​from four language families and two classical ciphers under the same six tests (Blocks A–F).

**Subpregunta 2 — Forward modeling**

Which specific generative mechanism—among eleven candidates, including the hypotheses of Rugg \[2004\], Timm and Schinner \[2020\], Hermes \[2022\], and Greshko \[2025\]—best reproduces the complete statistical footprint of the Voynich? To answer this, we generated eleven calibrated synthetic corpora and measured their weighted Euclidean distance to the Voynich in a five-metric space (Block G).

**Subquestion 3 — Quantitative filter**

Is it possible to define a set of numerical constraints (bounce, positional MI, bigram MI, spectral gap) that any future decryption proposal must satisfy to be statistically plausible?

Note what these questions do not ask: they do not ask whether the Voynich Manuscript is decipherable, they do not ask what underlying language (if any) is present, and they do not ask whether it has meaning. These are legitimate questions, but they cannot be answered with the tools we use here. Our questions are specifically about the type of system that produces the observable text, about its position in the space of variation of natural languages, and about which mechanisms are quantitatively ruled out.

## **4.2 Why this question is tractable**

An important feature of our question is that it is operationalizable: we can convert it into concrete statistical tests with numerical results and p-values. This is not the case with all questions about the Voynich manuscript. Hypotheses such as "it is written in medieval Hebrew" or "it is a complete forgery" are much more difficult to disprove.

The reason our question is tractable is that natural languages, ciphers, and artificial systems have distinct statistical signatures that we can measure. The table below summarizes the predictions for each type of system for the five properties we measured:

| Property | Natural language | Substitution cipher | artificial syllabic system |
| :---- | :---- | :---- | :---- |
|  |  | **Positional structure of morphemes** | Strong: prefixes and suffixes in fixed positions | Inherited from the original language | Very strong: glyphs partitioned by position |
|  |  | **Conditional entropy (N=1→4)** | It decreases monotonically | It diminishes like the encrypted language | U-shaped: falls at N=1, rises at N≥2 |
|  |  | **Markov mixing speed** | Moderate (spectral gap \~0.5--0.8) | The same as the encrypted language | Low (gap \~0.5, similar to binders) |
|  |  | **Vocabulary by section** | Differentiated (different topics) | Uniform (the encryption does not distinguish themes) | Differentiated if it encodes real content |
|  |  | **Mutual positional information** | Moderate (\~0.15--0.31 bits) | Same as the original language | Alta (\~0.5--0.7 bits) |

The "artificial syllabic system" column reflects the predictions of the SilPart model (Chapter 14), which turned out to be the closest to the Voynich model. The research question is, essentially, to determine in which of these three columns the Voynich model falls—and if it falls somewhere in between or outside the three, what that implies.

## **4.3 Analysis Structure**

To answer the question, we organized the analysis into six independent diagnostic blocks, plus a forward modeling block that evaluates eleven generative hypotheses. The independence between diagnostic blocks is key: if all the tests used the same statistical property, a favorable result would be a single repeated observation. With six distinct tools, the convergence of results is genuine cumulative evidence.

| Block | Tool | What does it measure? | Part of the study |
| :---- | :---- | :---- | :---- |
|  |  | **A** | **Mutual positional information** | Do glyphs have preferred positions in a word? | Part III, ch. 9 |
|  |  | **B** | **Holdout by folio** | Do the patterns replicate in unseen data? | Part III, ch. 10 |
|  |  | **C** | **Conditional entropy of order N** | How does the context predict the following glyph? | Part III, ch. 11 |
|  |  | **D** | **Markov spectral gap** | How persistent are the dependencies between glyphs? | Part III, ch. 12 |
|  |  | **AND** | **Semantic differentiation** | Does the vocabulary vary between thematic sections? | Part III, ch. 13 |
|  |  | **F** | **Curve shape metrics** | Does the shape of the entropic curve distinguish the Voynich? | Part III, ch. 11 |
|  |  | **G** | **Forward modeling (11 modelos)** | What generative mechanism reproduces the Voynich footprint? | Part III, ch. 14 |

## **4.4 What this analysis can and cannot demonstrate**

It is important to be explicit about the interpretive limitations of our analysis before the reader arrives at the results. This is not rhetorical modesty: it is the only way to ensure that the conclusions are honest.

**What we can demonstrate**

- Whether the Voynich cipher is statistically different from a Caesar or Vigenère cipher applied to Latin, under multiple independent tests.

- If the glyphs have positional preferences within the word that are statistically incompatible with random text.

- If the vocabulary of glyphs varies between sections of the manuscript in a manner consistent with semantically differentiated content.

- If the properties of the chain of transitions between glyphs are more like those of a natural language than those of a cipher.

- Whether the statistical profile of Voynich is grouped with any specific language family or is located outside the space of variation of the six natural languages ​​tested (Subquestion 1).

- Which specific generative mechanisms are capable of reproducing the complete statistical footprint of the Voynich and which are quantitatively ruled out (Sub-question 2).

- What minimum numerical constraints must any future decryption proposal satisfy to be statistically plausible? (Subquestion 3\)

**What we cannot prove**

- Whether Voynich is a known or unknown natural language: our tests distinguish "language-like structure" from "cipher structure," but cannot identify which language.

- The manuscript has meaning: an artificial system with designed morphology can pass all our tests without encoding any message.

- That our interpretation of the thematic sections is correct: if the herbal/biological/recipes division is incorrect, Block E has no valid interpretation.

- The results would hold true with other transcriptions: we have only tested with STA1 2.0.

*With the context established, the corpus described, and the question precisely formulated, we are ready to develop the mathematical tools we will use in the analysis. That is the subject of Part II.*

# **Part I References**

- Amancio , D. R. , Altmann , E. G. , Rybski , D. , Oliveira Jr. , O. N. , and Costa , L. da F. (2013). "Probing the Statistical Properties of Unknown Texts: Application to the Voynich Manuscript." *PLoS ONE*8(7): e67310. TWO:[10.1371/journal.pone.0067310](https://doi.org/10.1371/journal.pone.0067310)

- Babaahmadi, K. (2019). "A Hidden Markov Model for the Linguistic Analysis of the Voynich Manuscript." *Mathematical and Computational Applications (MDPI)* 24(1): 14\. [https://www.mdpi.com/2297-8747/24/1/14](https://www.mdpi.com/2297-8747/24/1/14)

- Bennett, W. R. (1976). *Scientific and Engineering Problem Solving with the Computer.* Englewood Cliffs: Prentice-Hall.

- Bowern, C. y Lindemann, L. (2021). "The Linguistics of the Voynich Manuscript." *Annual Review of Linguistics* 7: 285--308. DOI: [10.1146/annurev-linguistics-011619-030613](https://doi.org/10.1146/annurev-linguistics-011619-030613)

- Currier, P. (1976). "Papers on the Voynich Manuscript." Presented at a seminar on the Voynich Manuscript.[https://www.voynich.nu/extra/curr\_main.html](https://www.voynich.nu/extra/curr_main.html)

- Gaskell, D. E. y Bowern, C. L. (2022). "Gibberish After All? Voynichese Is Statistically Similar to Human-Produced Samples of Meaningless Text." *Proceedings of the International Conference on the Voynich Manuscript 2022*, CEUR Workshop Proceedings, Vol. 3313\. [https://ceur-ws.org/Vol-3313/paper4.pdf](https://ceur-ws.org/Vol-3313/paper4.pdf)

- Greshko, M. A. (2025). "The Naibbe Cipher: A Substitution Cipher that Encrypts Latin and Italian as Voynich Manuscript-Like Ciphertext." *Cryptologia*. DOI: [10.1080/01611194.2025.2566408](https://doi.org/10.1080/01611194.2025.2566408)

- Hauer, B. y Kondrak, G. (2016). "Decoding Anagrammed Texts Written in an Unknown Language and Script." *Transactions of the Association for Computational Linguistics* 4: 75--86. DOI: [10.1162/tacl\_a\_00084](https://doi.org/10.1162/tacl_a_00084)

- Hermes, J. (2022). "Polygraphia III: The Cipher that Pretends to be an Artificial Language." *Proceedings of the International Conference on the Voynich Manuscript 2022*, CEUR Workshop Proceedings, Vol. 3313\. [https://ceur-ws.org/Vol-3313/paper7.pdf](https://ceur-ws.org/Vol-3313/paper7.pdf)

- Landini, G. (2001). "Evidence of Linguistic Structure in the Voynich Manuscript Using Spectral Analysis." *Cryptologia* 25(4): 275--295. DOI: [10.1080/0161-110191889932](https://doi.org/10.1080/0161-110191889932)

- Lindemann, L. (2022). "Crux of the MATTR: Voynichese Morphological Complexity." *Proceedings of the International Conference on the Voynich Manuscript 2022*, CEUR Workshop Proceedings, Vol. 3313\. [https://ceur-ws.org/Vol-3313/paper9.pdf](https://ceur-ws.org/Vol-3313/paper9.pdf)

- Lindemann, L. y Bowern, C. (2020). "Character Entropy in Modern and Historical Texts: Comparison Metrics for an Undeciphered Manuscript." arXiv preprint arXiv:2010.14697. [https://arxiv.org/abs/2010.14697](https://arxiv.org/abs/2010.14697)

- Matlach, V., Janeckova, B., and Dostal, D. (2022). "The Voynich Manuscript: Symbol Roles Revisited."*PLoS ONE*17(1): e0260948. DOI:[10.1371/journal.pone.0260948](https://doi.org/10.1371/journal.pone.0260948)

- Montemurro, M. A. y Zanette, D. H. (2013). "Keywords and Co-Occurrence Patterns in the Voynich Manuscript: An Information-Theoretic Analysis." *PLoS ONE*8(6): e66344. TWO:[10.1371/journal.pone.0066344](https://doi.org/10.1371/journal.pone.0066344)

- Reddy, S. y Knight, K. (2011). "What We Know About The Voynich Manuscript." *Proceedings of the 5th ACL-HLT Workshop on Language Technology for Cultural Heritage, Social Sciences, and Humanities*, pp. 78--86. [https://aclanthology.org/W11-1511/](https://aclanthology.org/W11-1511/)

- Rugg, G. (2004). "An Elegant Hoax? A Possible Solution to the Voynich Manuscript." *Cryptologia* 28(1): 31--46. DOI: [10.1080/0161-110491892755](https://doi.org/10.1080/0161-110491892755)

- Rugg, G. y Taylor, G. (2017). "Hoaxing Statistical Features of the Voynich Manuscript." *Cryptologia* 41(3): 247--268. DOI: [10.1080/01611194.2016.1206753](https://doi.org/10.1080/01611194.2016.1206753)

- Schinner, A. (2007). "The Voynich Manuscript: Evidence of the Hoax Hypothesis." *Cryptologia* 31(2): 95--107. DOI: [10.1080/01611190601133539](https://doi.org/10.1080/01611190601133539)

- Stolfi, J. (2000--2012). "Statistical Properties of the Voynich Manuscript." Technical Reports, Institute of Computing, UNICAMP. [https://www.ic.unicamp.br/\~stolfi/EXPORT/projects/voynich/](https://www.ic.unicamp.br/~stolfi/EXPORT/projects/voynich/)

- Timm, T. y Schinner, A. (2020). "A Possible Generating Algorithm of the Voynich Manuscript." *Cryptologia* 44(1): 1--20. DOI: [10.1080/01611194.2019.1596999](https://doi.org/10.1080/01611194.2019.1596999)

- Timm, T. y Schinner, A. (2024). "The Voynich Manuscript: Discussion of Text Creation Hypotheses." *Cryptologia* 48(4): 305--322. DOI: [10.1080/01611194.2023.2225716](https://doi.org/10.1080/01611194.2023.2225716)


# Caramuel's Logodaedala and the Voynich Positional Encoding

## Source

Martinez Gavilan, M. D. (2025). En los limites de la linguistica: el "Apparatus philosophicus" (1665) de Juan Caramuel y los nuevos intereses en el estudio del lenguaje. *Boletin de la Sociedad Espanola de Historiografia Linguistica*, (19), 99-152. https://doi.org/10.5281/zenodo.17961147

## Context

Juan Caramuel (1606-1682) was a Spanish polymath who formalized the discipline of constructing artificial languages in his *Apparatus Philosophicus* (1665). His work documents ideas rooted in earlier traditions (Aristotelian predicaments, Lullian combinatorics, Kabbalistic letter mysticism) and provides a theoretical framework that closely parallels the encoding system found throughout the Voynich Manuscript.

## Key Concepts from Caramuel

### Cifras Ineffabiles (Ineffable Ciphers)
Signs that refer directly to things or concepts without the mediation of natural language words. Caramuel distinguishes these from *cifras effabiles* (substitution ciphers on existing alphabets). The Voynich text behaves as cifras ineffabiles: its glyphs encode categorical properties through their position in the word, rather than substituting for letters of a natural language.

### Logodaedala (The Ingenious Construction of Language)
A discipline Caramuel institutes as part of the liberal arts, with rules for constructing languages guided by:
- **Brevity**: words should be as short as possible (monosyllabic, triliteral)
- **Regularity**: strict one-to-one correspondence between form and meaning
- **Positional encoding**: vowels carry fixed categorical meaning (the 6 Aristotelian predicaments: substance, quantity, quality, relation, location, duration), consonants provide specificity

### Lingua Atlantica
An agglutinative language based on Latin roots with prefixed/suffixed letters encoding grammatical categories. Each affix position has a single, fixed meaning — no syncretism, no irregularity. This is structurally analogous to the SilPart model of Voynich words (onset + nucleus + coda with fixed positional roles).

## Direct historical link to the Voynich provenance

The Martínez Gavilán paper (2025) documents two facts that connect the Caramuel framework directly to the Voynich's known chain of custody:

1. **Caramuel and Athanasius Kircher were active correspondents.** Their epistolary exchange was edited by Ramón Ceñal (1953). Both belonged to the same scholarly network — Gassendi, Mersenne, **Marci**, Rheita, Kircher — i.e. precisely the circle in which the Voynich Manuscript circulated in the 17th century (Marci sent the manuscript to Kircher in 1665/1666).

2. **Kircher himself authored a published pasigraphy.** His *Polygraphia Nova et Universalis* (Rome, 1663) presents a universal written language followed by ciphering systems built on Vigenère and Trithemius. Caramuel praised it explicitly in a letter dated 4 August 1663 (Ceñal 1953, 139–142). This means the documented owner of the Voynich was himself an author and theorist of pasigraphic-cipher hybrids, two years before Caramuel formalized the *cifra ineffabilis* category in the *Apparatus*.

The implication is non-trivial: the theoretical framework that best describes the Voynich's encoding (philosophical pasigraphy, *cifra ineffabilis*) was an actively cultivated research programme **inside the very network that owned and transmitted the manuscript**. Kircher → Marci → Caramuel are not three isolated names; they are three nodes of a single 17th-century pasigraphy circle.

## Parallel with the Voynich Manuscript

### The SilPart model applies to the entire manuscript

The positional structure is not limited to the zodiac section. The SilPart model (best generative fit, d=0.445) shows that 73% of Voynich glyphs are position-locked across **all sections** — herbal, balneological, pharmaceutical, cosmological, and zodiac alike. Every Voynich word follows the same onset + nucleus + coda architecture with fixed positional roles.

### The zodiac section as verification

In the zodiac section (notebooks 70-71), this positional encoding could be **verified** because the astrological properties of each degree provide ground truth:

| Caramuel's System | Voynich (verified in zodiac) |
|---|---|
| Each vowel position = one predicament | Each atom position = one astrological property |
| Vowel A = substance, E = quantity, etc. | Pos2 = season (p=0.0002), Pos3 = fertility, Pos4 = sign type |
| Fixed prefix/suffix markers | Pos0 = zodiac marker (A1), Pos5 = degree marker (A2) |
| Triliteral monosyllabic words | 4-7 atom labels |
| Inspired by Chinese and Hebrew | Statistical match with NW Semitic (Hebrew/Aramaic) |
| Biunivocal form-meaning mapping | Each position independently encodes one category |

The same positional structure operates in all other sections, but without equivalent ground truth to verify what each position encodes there.

### The central paradox explained

The cipher-type diagnostics (notebook 29) analyzed the **full corpus** (37,087 words) and found: high Index of Coincidence (12.7x random), no polyalphabetic signal, no transposition improvement, strong bigram dependencies — the text behaves statistically like natural language but resists all 16 monoalphabetic decipherment models tested.

A cifra ineffabile explains this paradox: the text has natural-language-like statistics because it was designed with systematic regularities (positional categories, combinatorial rules), but it cannot be deciphered as a substitution cipher because it was never a cipher of natural language in the first place. The glyphs do not stand for letters — they encode categorical properties directly.

### Supporting evidence across the manuscript

| Finding | Notebook | Scope | Implication |
|---|---|---|---|
| SilPart best generative fit (d=0.445) | 04 | Full corpus | Positional structure is real and universal |
| 73% glyphs position-locked | 08 | Full corpus | Onset/nucleus/coda roles are fixed |
| 166 glyph types, too many for alphabet, too few for logography | 01-05 | Full corpus | Consistent with positional combinatorial system |
| No two distinct glyph populations (nomenclator discarded) | 30-31 | Full corpus | Single encoding system, not mixed cipher+code |
| IC=0.0764, no polyalphabetic/transposition signal | 29 | Full corpus | Not a cipher of natural language |
| 16 monoalphabetic models fail (root ceiling) | 06-18 | Full corpus | Not reducible to letter substitution |
| Dual visual + textual encoding | 72 | Zodiac | Redundant channels consistent with reference manual |
| Pos2 x season Bonferroni-significant (p=0.0002) | 71 | Zodiac | Verified: positions encode categories |

## What This Means (and What It Doesn't)

**What it confirms**: The encoding system found throughout the Voynich is historically plausible. The idea of positional categorical encoding — where each slot in a word carries a fixed semantic category — was formalized by Caramuel in 1665 but draws on much older intellectual traditions (Aristotle, Llull, Kabbalah) that predate the Voynich (c. 1404-1438).

**What it doesn't provide**: Caramuel's work does not help decipher the Voynich. His system is based on Latin and post-dates the manuscript by 200+ years. It offers no table of correspondences, no identification of what each position encodes in non-zodiac sections, and no specific connection to the Voynich.

**Theoretical implication**: The Voynich Manuscript is likely not a cipher of natural language at all, but rather a *philosophical pasigraphy* — a constructed notation system (cifra ineffabile) designed to encode categorical knowledge directly. Caramuel's Logodaedala provides the historical-theoretical name for what the Voynich encoding appears to be.

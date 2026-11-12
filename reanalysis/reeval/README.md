# Unified n-gram re-evaluation

Re-scores the n-gram realism test of every stored decipherment mapping with one protocol, fixing the inverted-direction error found in the original notebooks.

```bash
cd LLM_training/paper_dsh/revision_R1/reeval
../../../.venv/bin/python run_ngram_reeval.py            # B = 1000, ~minutes
../../../.venv/bin/python run_ngram_reeval.py --only 7 14 --B 200
```

Outputs: `results/ngram_reeval.json` (all numbers) and `results/ngram_reeval.md` (table with old values side by side).

## Protocol (`thresholds.json`)

- **Statistic:** JSD between word-internal trigram distributions, identical to the notebooks' `trigram_jsd`.
- **Samples:** full Voynich corpus (STA1: 37,087 words; EVA: 34,725) vs. a size-matched target sample (seed 42, as in the notebooks). The original runs used only the first 5,000 words of each.
- **Null:** within-table permutation of the learned mapping, B = 1000. This preserves the multiset of target units, so the null differs from the real mapping only in which glyph gets which unit. The originals used random draws with replacement (B = 100).
- **p-value:** (1 + #{null ≤ real}) / (B + 1), lower is better. PASS p < 0.05, MARGINAL p < 0.20, FAIL otherwise.
- **Ceiling:** JSD between the reference sample and a disjoint sample of genuine target text.
- **Realism index:** (null mean − real) / (null mean − ceiling). 0 means no better than a permuted mapping; 1 means as close as genuine target text.

## Fidelity checks

- Corpus parsing, TP-P20 syllabification, EVA parsing and allograph rewriting are executed **verbatim from the notebook source** (`nbcode.py`), not re-implemented.
- With the old samples (first 5,000 words), the re-implemented JSD reproduces the stored `real_jsd` to 4 decimals for Models 1, 5, 7, 14, 15, 17 and 19.
- Sefaria texts come from the frozen copies in `LLM_training/corpus/sefaria/`, verified against the original word counts.

## Not covered

- Model 4 has no mapping (semantic cross-validation).
- Models 12 and 13 have no stored mapping. Notebooks 20 and 21 must be re-run, and notebook 20 also carries the `np.mean` bug.

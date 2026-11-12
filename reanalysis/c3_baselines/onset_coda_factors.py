"""Follow-up to onset_coda_null.py: verbose ciphers of Hebrew invert the onset/coda ratio (1.4-1.8),
but those streams also have long words (~6 glyphs) and small alphabets (16-18). Separate the factors
on the Torah sample:
  long words      pairs of consecutive words concatenated (natural alphabet, ~7.6 letters)
  small alphabet  27 letters merged at random into 16 classes (natural word length)
  both            small alphabet + concatenated pairs
  verbose len-2   every letter -> a unique 2-glyph code over 18 glyphs (no variable code length)
  verbose fixed   reference (h1_verbose.verbose_cipher, codes of length 1-3)
Observed, reversed and shuffled-in-word (B_SHUF reps) ratios, as in onset_coda_null.

Usage: python onset_coda_factors.py  -> results/onset_coda_factors.json
"""
import json

import numpy as np

from onset_coda_null import C, HERE, N_WORDS, ratios, summary, verbose_cipher

B_SHUF = 10


def concat_pairs(words):
    return [words[i] + words[i + 1] for i in range(0, len(words) - 1, 2)]


def merge_alphabet(words, k=16, seed=42):
    rng = np.random.default_rng(seed)
    letters = sorted({c for w in words for c in w})
    cls = list(range(k)) + list(rng.integers(k, size=len(letters) - k))  # surjective onto k classes
    rng.shuffle(cls)
    m = {c: f's{j:02d}' for c, j in zip(letters, cls)}
    return [[m[c] for c in w] for w in words]


def verbose_len2(words, seed=42):
    rng = np.random.default_rng(seed)
    glyphs = [f'g{i:02d}' for i in range(18)]
    letters = sorted({c for w in words for c in w})
    pairs = [(a, b) for a in glyphs for b in glyphs]
    pick = rng.choice(len(pairs), size=len(letters), replace=False)
    code = {c: pairs[i] for c, i in zip(letters, pick)}
    return [[g for c in w for g in code[c]] for w in words]


if __name__ == '__main__':
    torah = C.subsample(C.torah_hebrew(), N_WORDS)
    small = merge_alphabet(torah)
    conds = {
        'Torah plain': torah,
        'long words (pairs)': concat_pairs(C.subsample(C.torah_hebrew(), 2 * N_WORDS)),
        'small alphabet (16)': small,
        'small alphabet + long words': concat_pairs(merge_alphabet(C.subsample(C.torah_hebrew(), 2 * N_WORDS))),
        'verbose len-2 codes': verbose_len2(torah),
        'verbose fixed (len 1-3)': verbose_cipher(torah, 'fixed')[0],
    }
    res = {}
    for name, words in conds.items():
        rng = np.random.default_rng(42)
        obs = ratios(words)
        rev = ratios([w[::-1] for w in words])
        shuf = summary([ratios([list(rng.permutation(w)) for w in words])['pair'] for _ in range(B_SHUF)])
        V = len({c for w in words for c in w})
        L = float(np.mean([len(w) for w in words]))
        res[name] = {'n_words': len(words), 'V': V, 'mean_len': L, 'observed': obs, 'reversed': rev,
                     'shuffled_pair': shuf}
        print(f"{name:30s} n={len(words):6d} V={V:3d} len={L:4.1f} | pair {obs['pair_onsets']}/{obs['pair_codas']}"
              f"={obs['pair']:.2f} rev {rev['pair']:.2f} shuf {shuf['mean']:.2f} | class {obs['class']:.2f}",
              flush=True)
    (HERE / 'results' / 'onset_coda_factors.json').write_text(json.dumps(res, indent=1, ensure_ascii=False),
                                                              encoding='utf-8')

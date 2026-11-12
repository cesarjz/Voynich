"""Onset/coda ratio of verbose ciphers of Hebrew across codebooks (body §6.3, Fig. onset/coda, Supp. S4).

Reconstructs results/onset_coda_factors_seeds.json, first produced by an inline command (2026-11-10):
five further codebooks (seeds SEEDS) for each of four verbose designs, enciphering the same Torah sample
used by onset_coda_null.py / onset_coda_factors.py:
  fixed   verbose_merge.verbose_cipher(mode='fixed')   codes of length 1-3 over 18 glyphs
  homoph  verbose_merge.verbose_cipher(mode='homoph')  same, two alternative codes per letter
  slot    verbose_merge.slot_cipher                    3 x 6 slot-structured codes
  len2    onset_coda_factors.verbose_len2              every letter -> unique 2-glyph code
Per codebook: observed and reversed pair ratio (distinct onsets / distinct codas in two-unit O-C words).
The seed-42 codebooks of 'fixed' and 'homoph' are in onset_coda_null.json (22 codebooks in all).

Usage: python onset_coda_seeds.py [--seeds 1 2 3 4 5]  -> results/onset_coda_factors_seeds.json
"""
import argparse
import json

from onset_coda_null import C, HERE, N_WORDS, ratios, verbose_cipher
from onset_coda_factors import verbose_len2

ap = argparse.ArgumentParser()
ap.add_argument('--seeds', type=int, nargs='+', default=[1, 2, 3, 4, 5])
ap.add_argument('--out', default=str(HERE / 'results' / 'onset_coda_factors_seeds.json'))
a = ap.parse_args()

torah = C.subsample(C.torah_hebrew(), N_WORDS)
gen = {'fixed': lambda s: verbose_cipher(torah, 'fixed', s)[0],
       'homoph': lambda s: verbose_cipher(torah, 'homoph', s)[0],
       'slot': lambda s: verbose_cipher(torah, 'slot', s)[0],
       'len2': lambda s: verbose_len2(torah, s)}
res = {}
for name, g in gen.items():
    res[name] = []
    for s in a.seeds:
        w = g(s)
        res[name].append([round(ratios(w)['pair'], 2), round(ratios([x[::-1] for x in w])['pair'], 2)])
    print(f'{name} obs/rev per seed: {[tuple(p) for p in res[name]]}', flush=True)
json.dump(res, open(a.out, 'w'))

"""C5 follow-up: section classification within a single scribal hand (body §7.1, Supp. S6).

Reconstructs results/classifier_c5_withinhand.json, first produced by an inline command (2026-11-09).
Same pages, labels, features (34 core-glyph frequencies, core = glyphs with >= 100 tokens over all pages),
classifier and uncertainty as classifier_c5.py; one rng (seed 42) shared across hands 1-4, in that order.
Sections with a single page in a hand are dropped (no leave-one-out centroid; hand 1: one cosmo page).
Hand 5 (7 pages) is not tested.

Usage: python classifier_c5_withinhand.py [--out PATH]  -> results/classifier_c5_withinhand.json
"""
import argparse
import json
from collections import Counter

import numpy as np

from classifier_c5 import HERE, META, PAGE_SECTION, encode, evaluate, glyph_features, load_pages

ap = argparse.ArgumentParser()
ap.add_argument('--out', default=str(HERE / 'results' / 'classifier_c5_withinhand.json'))
a = ap.parse_args()

rng = np.random.default_rng(42)
pages = load_pages()
names = sorted(p for p in pages if PAGE_SECTION.get(p, 'unknown') != 'unknown')
sec = [PAGE_SECTION[p] for p in names]
lang = [META.get(p, {}).get('L', '?') for p in names]
hand = [META.get(p, {}).get('H', '?') for p in names]
all_words = [w for p in names for w in pages[p]]
core = sorted(g for g, c in Counter(g for w in all_words for g in w).items() if c >= 100)
X34 = glyph_features(pages, names, core)
res = {}
for H in ('1', '2', '3', '4'):
    n_sec = Counter(s for s, h in zip(sec, hand) if h == H)
    m = np.array([h == H and n_sec[s] >= 2 for s, h in zip(sec, hand)])  # a one-page section has no LOO centroid
    yy, cc = encode([s for s, k in zip(sec, m) if k])
    r = evaluate(X34[m], yy, rng)
    r.pop('pred')
    res[H] = {'sections': dict(Counter(s for s, k in zip(sec, m) if k)),
              'currier': dict(Counter(l for l, k in zip(lang, m) if k)), **r}
    print(f"hand {H}: {res[H]['sections']} acc {r['accuracy']:.3f} bal {r['balanced_accuracy']:.3f} "
          f"[{r['bal_ci'][0]:.3f},{r['bal_ci'][1]:.3f}] p {r['p_bal']:.4f}", flush=True)
json.dump(res, open(a.out, 'w'), indent=1)

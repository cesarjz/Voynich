"""Visual glyph families vs position (Supp. S4; body §6 moved to the supplement 2026-11-10).

Re-runs notebook 75 (Voynich/75_family_position_correlation.ipynb). Cells 1-3 and 8 are executed verbatim
(STA1 parser, TP-P20 SilPart classes, per-glyph class counts, per-glyph counts at word positions 1-8; glyphs
with >= 5 tokens). Family = first character of the STA1 code; families with >= 2 members enter the statistic.
Statistic: mean over families of the Shannon entropy of the family's pooled distribution (positions 1-8, or
the four SilPart classes). Null: family labels permuted among glyphs, either freely or within frequency
terciles (nb 75 cell 13), B = 10,000. Each test here has its own rng (seed 42); the notebook shared one rng
across tests, so its p and z differ in the last digit. p = (1 + #{null <= obs}) / (B + 1); the notebook
reported #{null <= obs} / B.

Usage: python family_position.py  -> results/family_position.json
"""
import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
NB = HERE.parents[1] / '75_family_position_correlation.ipynb'
B = 10_000

cells = json.loads(NB.read_text(encoding='utf-8'))['cells']
code = [''.join(c['source']) for c in cells if c['cell_type'] == 'code']
ns = {'__name__': 'nb75'}
import os
cwd = os.getcwd()
os.chdir(NB.parent)
try:
    for i in (0, 1, 2):          # nb cells 1-3: corpus, SilPart pipeline, per-glyph class counts
        exec(code[i], ns)
    exec(code[7].split('# Family-level word-position entropy')[0], ns)   # nb cell 8: counts at positions 1-8
finally:
    os.chdir(cwd)
df, df_pos = ns['df'], ns['df_pos']
CLASSES = ns['CLASSES']
POS = [f'p{i}' for i in range(1, 9)]


def mean_family_entropy(fam, counts, min_members=2):
    size = Counter(fam)
    tot = {}
    for f, c in zip(fam, counts):
        tot[f] = tot.get(f, 0) + c
    H = []
    for f, c in tot.items():
        if size[f] < min_members or c.sum() == 0:
            continue
        p = c / c.sum()
        p = p[p > 0]
        H.append(-(p * np.log2(p)).sum())
    return float(np.mean(H))


def test(frame, cols, stratified):
    fam = frame['family'].values.copy()
    counts = frame[cols].values.astype(float)
    bands = pd.qcut(frame['total'], q=3, labels=False).values
    rng = np.random.default_rng(42)
    obs = mean_family_entropy(fam, counts)
    null = np.empty(B)
    for b in range(B):
        if stratified:
            s = fam.copy()
            for k in np.unique(bands):
                idx = np.where(bands == k)[0]
                s[idx] = rng.permutation(fam[idx])
        else:
            s = rng.permutation(fam)
        null[b] = mean_family_entropy(s, counts)
    return {'observed': obs, 'null_mean': float(null.mean()), 'null_sd': float(null.std()),
            'z': float((obs - null.mean()) / null.std()),
            'p': float((1 + (null <= obs).sum()) / (B + 1))}


size = Counter(df['family'])
res = {'n_glyphs': int(len(df)), 'n_families': len(size),
       'n_families_ge2': sum(v >= 2 for v in size.values()),
       'family_sizes': dict(sorted(size.items())),
       'tercile_ranges': [[int(g['total'].min()), int(g['total'].max())]
                          for _, g in df.groupby(pd.qcut(df['total'], q=3, labels=False))],
       'B': B, 'tests': {}}
for name, frame, cols in (('word position 1-8', df_pos, POS), ('SilPart class', df, CLASSES)):
    for strat in (False, True):
        key = f"{name} | {'frequency-stratified' if strat else 'free'}"
        res['tests'][key] = r = test(frame, cols, strat)
        print(f"{key:45s} obs {r['observed']:.4f} null {r['null_mean']:.4f} ({r['null_sd']:.4f}) "
              f"z {r['z']:+.2f} p {r['p']:.4f}", flush=True)
print({k: v for k, v in res.items() if k != 'tests'})
(HERE / 'results' / 'family_position.json').write_text(json.dumps(res, indent=1), encoding='utf-8')

"""C1 follow-up: §4.2 model ranking without the bounce (estimator artefact, see bounce_calibration.py).

Uses the stored metrics of nb 05 (synthetic_corpora_results.json, cell 27/63 inputs)
and the natural-language rows hard-coded in nb 05 cell 25. Same weighted Euclidean distance and
the same 500-draw Dirichlet test as nb 05 cell 63 (seed noted below), for three metric sets:
  full       bounce, decay, MI_pos, MI_big, gap   (reproduces the paper: SilPart d = 0.445)
  no_bounce  decay, MI_pos, MI_big, gap
  clean      MI_pos, MI_big, gap  (decay = (H0-H4)/H0 also uses the escape-inflated H4)
Caveat: the model parameters were tuned (nb 05 sweeps) against the full distance, bounce included.

Usage: python rerank_no_bounce.py → results/rerank_no_bounce.json
"""
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
SRC = HERE / 'synthetic_corpora_results.json'
W = {'rebote': 3.0, 'decay': 2.0, 'MI_pos': 1.5, 'MI_big': 1.5, 'gap': 1.0}
KEY = {'rebote': 'Rebote', 'decay': 'Decay', 'MI_pos': 'MI_pos', 'MI_big': 'MI_big', 'gap': 'Gap'}
SETS = {'full': list(W), 'no_bounce': ['decay', 'MI_pos', 'MI_big', 'gap'], 'clean': ['MI_pos', 'MI_big', 'gap']}
NAMES = {'slot': 'Slot', 'verbose': 'Verbose', 'nomenclator': 'Nomenclator', 'hybrid': 'Hybrid',
         'nompoly': 'NomPoly', 'silabico': 'Silabico', 'silpart': 'SilPart', 'cardan': 'Cardan',
         'autocita': 'AutoCita', 'polyg3': 'Polyg3', 'naibbe': 'Naibbe'}
NATURAL = {  # nb 05 cell 25 MULTI_METRICS
    'Latin': {'Decay': 0.402, 'Gap': 0.658, 'Rebote': 0.000, 'MI_pos': 0.267, 'MI_big': 1.082},
    'Hebrew': {'Decay': 0.299, 'Gap': 0.812, 'Rebote': 0.000, 'MI_pos': 0.311, 'MI_big': 0.607},
    'Arabic': {'Decay': 0.334, 'Gap': 0.798, 'Rebote': 0.000, 'MI_pos': 0.234, 'MI_big': 0.749},
    'Turkish': {'Decay': 0.342, 'Gap': 0.509, 'Rebote': 0.000, 'MI_pos': 0.151, 'MI_big': 0.835},
    'Finnish': {'Decay': 0.305, 'Gap': 0.577, 'Rebote': 0.000, 'MI_pos': 0.205, 'MI_big': 0.652},
    'Vigenere': {'Decay': 0.373, 'Gap': 0.855, 'Rebote': 0.000, 'MI_pos': 0.053, 'MI_big': 0.445},
}


def dist(m, t, w):
    return math.sqrt(sum(w[k] * (m[KEY[k]] - t[k]) ** 2 for k in w))


def main():
    d = json.loads(SRC.read_text(encoding='utf-8'))
    t = d['voynich_target']
    models = {NAMES[k]: d[k]['metrics'] for k in NAMES}
    out = {}
    for sname, keys in SETS.items():
        w = {k: W[k] for k in keys}
        rank = sorted(((n, dist(m, t, w)) for n, m in {**models, **NATURAL}.items()), key=lambda x: x[1])
        rng = np.random.default_rng(42)
        top1, top3 = Counter(), Counter()
        for _ in range(500):
            wd = dict(zip(keys, rng.dirichlet(np.ones(len(keys))) * sum(w.values())))
            r = sorted(models, key=lambda n: dist(models[n], t, wd))
            top1[r[0]] += 1
            top3.update(r[:3])
        out[sname] = {'ranking': rank, 'dirichlet_top1': dict(top1.most_common()),
                      'dirichlet_top3': dict(top3.most_common())}
        print(f'\n== {sname} ({", ".join(keys)})')
        for i, (n, x) in enumerate(rank, 1):
            print(f'  {i:2d} {n:12s} {x:.3f}{"" if n in models else "   (natural/cipher control)"}')
        print('  Dirichlet top-1:', {k: f'{v / 5:.1f}%' for k, v in top1.most_common()})
        print('  Dirichlet top-3:', {k: f'{v / 5:.1f}%' for k, v in top3.most_common(5)})
    (HERE / 'results' / 'rerank_no_bounce.json').write_text(json.dumps(out, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()

"""Does the six-role grammar capture more than any 6-class grouping of the glyphs?

role_transition_null.py shows that role transitions exceed a positional null (MI 0.223 vs 0.032) and that roles
recover 58 % of the glyph bigram's held-out gain over a positional model. Any partition of the 34 core glyphs into
classes would also pick up first-order glyph dependence, so the yardstick is:
  random   B_RAND partitions of the same 34 glyphs with the role sizes (10/7/8/3/3/3), fixed across folds
           (label-free, no leakage)
  ceiling  the 6-class partition maximising role-bigram MI, found by exchange (Brown-style, N_START random starts)
           inside each training fold for the held-out score, and on the whole text for in-sample MI
  roles    the nb 76 roles (in-sample MI; held-out with roles re-derived per fold = role_transition_null.heldout)
Measures: role-bigram MI within words (grammar_stats), held-out bits per glyph of the role model R and the share
(A - R)/(A - G) of the glyph bigram's gain. Same 10 folds (seed 42) as role_transition_null.heldout.

Usage: python role_partition_control.py [--workers 12]  -> results/role_partition_control.json
"""
import argparse
import json
import os
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

import numpy as np

import role_transition_null as RT

B_RAND, N_START, K_FOLD = 200, 20, 10
LAB = ['OPENER', 'ENCODER', 'CLOSER', 'BODY', 'SCAFFOLD', 'MIXED']

palabras = RT.ns['tokens_a_palabras'](RT.ns['parsear_sta_completo'](str(RT.VOYNICH_DIR / 'corpus' / 'voynich_sta.txt')))
V = sorted({g for w in palabras for g in w})
FOLDS = np.random.default_rng(42).permutation(len(palabras)) % K_FOLD


def heldout_fixed(part_for_fold):
    """part_for_fold(f, train) -> roles dict; returns pooled bits A, R, G and share."""
    tot, N = {'A': 0.0, 'R': 0.0, 'G': 0.0}, 0
    for f in range(K_FOLD):
        train = [w for w, z in zip(palabras, FOLDS) if z != f]
        test = [w for w, z in zip(palabras, FOLDS) if z == f]
        roles = part_for_fold(f, train)
        b, n = RT.evaluate(test, RT.fit(train, roles, V), roles, V)
        for k in tot:
            tot[k] += b[k] * n
        N += n
    out = {k: v / N for k, v in tot.items()}
    out['share'] = (out['A'] - out['R']) / (out['A'] - out['G'])
    return out


def core_glyphs(words):
    return sorted(g for g, c in Counter(g for w in words for g in w).items() if c >= RT.MIN_FREQ)


def bigram_matrix(words, core):
    ix = {g: i for i, g in enumerate(core)}
    M = np.zeros((len(core), len(core)))
    for w in words:
        if all(g in ix for g in w):
            for a, b in zip(w, w[1:]):
                M[ix[a], ix[b]] += 1
    return M


def mi_classes(M, z, k=6):
    Z = np.zeros((len(z), k))
    Z[np.arange(len(z)), z] = 1
    C = Z.T @ M @ Z
    N, r, c = C.sum(), C.sum(1), C.sum(0)
    nz = C > 0
    return float((C[nz] / N * np.log2(C[nz] * N / np.outer(r, c)[nz])).sum())


def best_partition(words, seed, k=6):
    core = core_glyphs(words)
    M = bigram_matrix(words, core)
    rng = np.random.default_rng(seed)
    best, best_z = -1, None
    for _ in range(N_START):
        z = rng.integers(k, size=len(core))
        cur = mi_classes(M, z, k)
        improved = True
        while improved:
            improved = False
            for i in rng.permutation(len(core)):
                old = z[i]
                for c in range(k):
                    if c == old:
                        continue
                    z[i] = c
                    m = mi_classes(M, z, k)
                    if m > cur + 1e-12:
                        cur, old, improved = m, c, True
                z[i] = old
        if cur > best:
            best, best_z = cur, z.copy()
    return {g: LAB[c] for g, c in zip(core, best_z)}


def random_job(b):
    rng = np.random.default_rng(10_000 + b)
    core = sorted(OBS_ROLES)
    labels = [r for r in LAB for _ in range(SIZES[r])]
    part = dict(zip(core, rng.permutation(labels)))
    mi = RT.grammar_stats(palabras, part)['mi_bits']
    ho = heldout_fixed(lambda f, train: part)
    return {'mi': mi, **ho}


OBS_ROLES = RT.assign_roles(palabras)
SIZES = Counter(OBS_ROLES.values())

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument('--brand', type=int, default=B_RAND)
    a = ap.parse_args()
    print(f'core glyphs {len(OBS_ROLES)}, role sizes {dict(SIZES)}', flush=True)
    obs_mi = RT.grammar_stats(palabras, OBS_ROLES)['mi_bits']
    obs_ho = RT.heldout(palabras)          # roles re-derived per fold (article value)
    obs_ho_global = heldout_fixed(lambda f, train: OBS_ROLES)
    print(f'roles: MI {obs_mi:.3f}  held-out R {obs_ho["R"]:.3f} share {obs_ho["frac_seq_info_by_roles"]:.3f}', flush=True)

    best_all = best_partition(palabras, seed=7)
    ceil_mi = RT.grammar_stats(palabras, best_all)['mi_bits']
    ceil_ho = heldout_fixed(lambda f, train: best_partition(train, seed=100 + f))
    print(f'ceiling: MI {ceil_mi:.3f} sizes {dict(Counter(best_all.values()))}  held-out R {ceil_ho["R"]:.3f} '
          f'share {ceil_ho["share"]:.3f}', flush=True)

    with ProcessPoolExecutor(a.workers) as ex:
        rand = list(ex.map(random_job, range(a.brand)))
    q = lambda x: {'mean': float(np.mean(x)), 'q025': float(np.quantile(x, .025)),  # noqa: E731
                   'q975': float(np.quantile(x, .975)), 'max': float(np.max(x))}
    mi_r = [r['mi'] for r in rand]
    sh_r = [r['share'] for r in rand]
    res = {'B_rand': a.brand, 'n_start': N_START, 'role_sizes': dict(SIZES),
           'roles': {'mi': obs_mi, 'heldout_rederived': obs_ho, 'heldout_global': obs_ho_global},
           'random': {'mi': q(mi_r), 'share': q(sh_r), 'R': q([r['R'] for r in rand]),
                      'p_mi': (1 + sum(m >= obs_mi for m in mi_r)) / (a.brand + 1),
                      'p_share': (1 + sum(s >= obs_ho['frac_seq_info_by_roles'] for s in sh_r)) / (a.brand + 1)},
           'ceiling': {'mi': ceil_mi, 'sizes': dict(Counter(best_all.values())), 'partition': best_all,
                       'heldout': ceil_ho}}
    r = res['random']
    print(f"random: MI {r['mi']['mean']:.3f} [{r['mi']['q025']:.3f},{r['mi']['q975']:.3f}] max {r['mi']['max']:.3f} "
          f"p {r['p_mi']:.4f} | share {r['share']['mean']:.3f} [{r['share']['q025']:.3f},{r['share']['q975']:.3f}] "
          f"p {r['p_share']:.4f}", flush=True)
    (RT.HERE / 'results' / 'role_partition_control.json').write_text(json.dumps(res, indent=1), encoding='utf-8')

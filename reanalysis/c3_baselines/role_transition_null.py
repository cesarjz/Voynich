"""C3: does the six-role grammar add anything beyond positional profiles?

Roles (nb 76 cell 1, verbatim rules): for each of the 34 core glyphs (>= 100 tokens), peak position
p* over absolute word positions 1..8 and dominant SilPart class d:
  OPENER  p* = 1 and P(p1) > .25    ENCODER  p* = 2 and P(p2) > .20    CONNECTOR  d = nuclear
  CLOSER  p* >= 3 and d = coda      BODY     p* >= 4                   SCAFFOLD   d = free, peak < .30
  MIXED   otherwise
Since roles are defined from positions, directional role transitions are expected by construction.

Test 1 — null preserving positional frequencies and word lengths: surrogate
corpora where the glyph at position i of a word of length L is drawn from the empirical
P(glyph | i, L); lengths are kept word by word. Roles are re-derived on each surrogate with the same
rules (and, cheaper, also with the observed roles fixed). Compared: role transition matrix,
P(ENCODER | OPENER) (paper: 63.5 %), position-1 -> 2 share of OPENER -> ENCODER, number of
'forbidden' cells (obs/exp < 0.3), and role-bigram mutual information.

Test 2 — held-out prediction (10-fold over words; roles and all counts from the training folds):
bits per glyph of
  A  positional unigram   P(g | pos, len)
  R  role grammar         P(role(g) | role_prev, pos, len) * P(g | role(g), pos, len)
  G  glyph bigram         Witten-Bell P(g | g_prev) interpolated with A
Fraction of the sequential information captured by roles = (A - R) / (A - G).

Usage: python role_transition_null.py  -> results/role_transition_null.json
"""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / 'reeval'))
from nbcode import VOYNICH_DIR, load_defs  # noqa: E402

ns = load_defs('76_role_grammar_and_sections.ipynb', ['parsear_sta_completo', 'tokens_a_palabras',
                                                      'construir_matriz_transicion', 'segmentar_silabas_tp',
                                                      'clasificar_silabas'])
ROLES = ['OPENER', 'ENCODER', 'CONNECTOR', 'CLOSER', 'BODY', 'SCAFFOLD', 'MIXED']
CLASSES = ['onset', 'nuclear', 'coda', 'free']
MAX_POS, MIN_FREQ = 8, 100
B_NULL = 100
POS_CAP, LEN_CAP = 7, 8


def assign_roles(palabras):
    """nb 76 cell 1, unchanged logic."""
    _, m_prob, _, idx = ns['construir_matriz_transicion'](palabras)
    flat, _ = ns['segmentar_silabas_tp'](palabras, m_prob, idx, 20)
    clase, words_syl = ns['clasificar_silabas'](flat, 5)
    gcc, gpc = defaultdict(Counter), defaultdict(Counter)
    for ws in words_syl:
        for s in ws:
            c = clase.get(s, 'free')
            for g in s:
                gcc[g][c] += 1
    for p in palabras:
        for i, g in enumerate(p):
            if i + 1 <= MAX_POS:
                gpc[g][i + 1] += 1
    roles = {}
    for g in sorted(gcc):
        if sum(gcc[g].values()) < MIN_FREQ:
            continue
        dom = max(CLASSES, key=lambda c: gcc[g].get(c, 0))
        tot = sum(gpc[g].values())
        pcts = {i: gpc[g].get(i, 0) / tot if tot else 0 for i in range(1, MAX_POS + 1)}
        peak = max(pcts, key=pcts.get)
        if peak == 1 and pcts[1] > 0.25:
            r = 'OPENER'
        elif peak == 2 and pcts[2] > 0.20:
            r = 'ENCODER'
        elif dom == 'nuclear':
            r = 'CONNECTOR'
        elif peak >= 3 and dom == 'coda':
            r = 'CLOSER'
        elif peak >= 4:
            r = 'BODY'
        elif dom == 'free' and pcts[peak] < 0.30:
            r = 'SCAFFOLD'
        else:
            r = 'MIXED'
        roles[g] = r
    return roles


def grammar_stats(palabras, roles):
    seqs = [[roles[g] for g in w] for w in palabras if all(g in roles for g in w)]
    ix = {r: i for i, r in enumerate(ROLES)}
    M = np.zeros((7, 7))
    p12 = Counter()
    for s in seqs:
        for j, (a, b) in enumerate(zip(s, s[1:])):
            M[ix[a], ix[b]] += 1
            if j == 0:
                p12[a, b] += 1
    N = M.sum()
    rows, cols = M.sum(1), M.sum(0)
    P = M / np.where(rows[:, None] > 0, rows[:, None], 1)
    E = np.outer(rows, cols) / N
    oe = np.where(E > 0, M / np.where(E > 0, E, 1), np.nan)
    live = (rows > 0)[:, None] & (cols > 0)[None, :]
    nz = M > 0
    mi = float((M[nz] / N * np.log2(M[nz] * N / np.outer(rows, cols)[nz])).sum())
    return {'P': P, 'oe': oe, 'n_forbidden': int(((oe < 0.3) & live).sum()),
            'P_enc_given_open': float(P[0, 1]),
            'pos12_open_enc_share': p12['OPENER', 'ENCODER'] / max(1, sum(p12.values())),
            'mi_bits': mi, 'coverage': len(seqs) / len(palabras),
            'role_counts': dict(Counter(roles.values()))}


def surrogate(palabras, rng):
    """Glyph at position i of a length-L word drawn from P(glyph | i, L); lengths kept."""
    pools = defaultdict(list)
    for w in palabras:
        for i, g in enumerate(w):
            pools[len(w), i].append(g)
    pools = {k: np.array(v) for k, v in pools.items()}
    return [[str(x) for x in (pools[len(w), i][rng.integers(len(pools[len(w), i]))] for i in range(len(w)))]
            for w in palabras]


# ---------------------------------------------------------------- held-out prediction
def ctx(i, L):
    return min(i, POS_CAP), min(L, LEN_CAP)


def fit(train, roles, V):
    pos = defaultdict(Counter)            # (pos, len) -> glyph
    rtr = defaultdict(Counter)            # (role_prev, pos, len) -> role
    emit = defaultdict(Counter)           # (role, pos, len) -> glyph
    big = defaultdict(Counter)            # g_prev -> g
    for w in train:
        prev_r, prev_g = '<w>', '<w>'
        for i, g in enumerate(w):
            c = ctx(i, len(w))
            r = roles.get(g, '?')
            pos[c][g] += 1
            rtr[(prev_r,) + c][r] += 1
            emit[(r,) + c][g] += 1
            big[prev_g][g] += 1
            prev_r, prev_g = r, g
    role_glyphs = defaultdict(set)
    for g in V:
        role_glyphs[roles.get(g, '?')].add(g)
    return pos, rtr, emit, big, role_glyphs


def evaluate(test, model, roles, V, alpha=0.1):
    pos, rtr, emit, big, role_glyphs = model
    nV, nR = len(V), len(role_glyphs)
    bits = {'A': 0.0, 'R': 0.0, 'G': 0.0}
    n = 0
    for w in test:
        prev_r, prev_g = '<w>', '<w>'
        for i, g in enumerate(w):
            c = ctx(i, len(w))
            r = roles.get(g, '?')
            pc = pos[c]
            pA = (pc[g] + alpha) / (sum(pc.values()) + alpha * nV)
            rc = rtr[(prev_r,) + c]
            ec = emit[(r,) + c]
            pR = ((rc[r] + alpha) / (sum(rc.values()) + alpha * nR)) * \
                 ((ec[g] + alpha) / (sum(ec.values()) + alpha * len(role_glyphs[r])))
            h = big[prev_g]
            if h:
                ch, th = sum(h.values()), len(h)
                pG = (h[g] + th * pA) / (ch + th)
            else:
                pG = pA
            bits['A'] -= math.log2(pA)
            bits['R'] -= math.log2(pR)
            bits['G'] -= math.log2(pG)
            prev_r, prev_g = r, g
            n += 1
    return {k: v / n for k, v in bits.items()}, n


def heldout(palabras, k=10, seed=42):
    V = sorted({g for w in palabras for g in w})
    folds = np.random.default_rng(seed).permutation(len(palabras)) % k
    tot = {'A': 0.0, 'R': 0.0, 'G': 0.0}
    N = 0
    for f in range(k):
        train = [w for w, z in zip(palabras, folds) if z != f]
        test = [w for w, z in zip(palabras, folds) if z == f]
        roles = assign_roles(train)  # roles fixed inside the training fold
        b, n = evaluate(test, fit(train, roles, V), roles, V)
        for key in tot:
            tot[key] += b[key] * n
        N += n
    out = {key: v / N for key, v in tot.items()}
    out['frac_seq_info_by_roles'] = (out['A'] - out['R']) / (out['A'] - out['G'])
    return out


def summarize(vals):
    a = np.array(vals, dtype=float)
    return {'mean': float(a.mean()), 'q025': float(np.quantile(a, .025)), 'q975': float(np.quantile(a, .975))}


if __name__ == '__main__':
    palabras = ns['tokens_a_palabras'](ns['parsear_sta_completo'](str(VOYNICH_DIR / 'corpus' / 'voynich_sta.txt')))
    roles = assign_roles(palabras)
    obs = grammar_stats(palabras, roles)
    print(f"roles: {obs['role_counts']}  coverage {obs['coverage']:.1%}")
    print(f"observed: P(ENC|OPEN)={obs['P_enc_given_open']:.3f} pos1->2 OPEN->ENC share="
          f"{obs['pos12_open_enc_share']:.3f} forbidden={obs['n_forbidden']} MI={obs['mi_bits']:.3f}", flush=True)

    rng = np.random.default_rng(42)
    null_re, null_fix = [], []
    for b in range(B_NULL):
        s = surrogate(palabras, rng)
        null_fix.append(grammar_stats(s, roles))
        null_re.append(grammar_stats(s, assign_roles(s)))
        if (b + 1) % 20 == 0:
            print(f'  null {b + 1}/{B_NULL}', flush=True)

    res = {'observed': {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in obs.items()},
           'roles': roles, 'B_null': B_NULL, 'null': {}}
    for name, nl in (('roles_rederived', null_re), ('roles_fixed', null_fix)):
        d = {key: summarize([x[key] for x in nl])
             for key in ('P_enc_given_open', 'pos12_open_enc_share', 'n_forbidden', 'mi_bits')}
        Pn = np.array([x['P'] for x in nl])
        d['P_mean'] = Pn.mean(0).tolist()
        d['P_q025'] = np.quantile(Pn, .025, axis=0).tolist()
        d['P_q975'] = np.quantile(Pn, .975, axis=0).tolist()
        d['oe_mean'] = np.nanmean(np.array([x['oe'] for x in nl]), 0).tolist()
        d['p_mi_upper'] = float((1 + sum(x['mi_bits'] >= obs['mi_bits'] for x in nl)) / (len(nl) + 1))
        res['null'][name] = d
        print(f"null ({name}): P(ENC|OPEN)={d['P_enc_given_open']['mean']:.3f} "
              f"[{d['P_enc_given_open']['q025']:.3f},{d['P_enc_given_open']['q975']:.3f}] "
              f"pos12 share={d['pos12_open_enc_share']['mean']:.3f} forbidden={d['n_forbidden']['mean']:.1f} "
              f"MI={d['mi_bits']['mean']:.3f} [{d['mi_bits']['q025']:.3f},{d['mi_bits']['q975']:.3f}] "
              f"p(MI)={d['p_mi_upper']:.4f}", flush=True)

    print('cells (row -> col): observed P vs null (rederived) mean [95 %]:')
    d = res['null']['roles_rederived']
    for i, a in enumerate(ROLES):
        for j, c in enumerate(ROLES):
            o = obs['P'][i, j]
            if o > 0.05 or d['P_mean'][i][j] > 0.05:
                flag = '' if d['P_q025'][i][j] <= o <= d['P_q975'][i][j] else ' *'
                print(f"  {a:9s}->{c:9s} obs {o:.3f}  null {d['P_mean'][i][j]:.3f} "
                      f"[{d['P_q025'][i][j]:.3f},{d['P_q975'][i][j]:.3f}]{flag}")

    ho = heldout(palabras)
    res['heldout_bits_per_glyph'] = ho
    print(f"held-out bits/glyph: A positional {ho['A']:.3f}  R roles {ho['R']:.3f}  G glyph-bigram {ho['G']:.3f}  "
          f"fraction of sequential info captured by roles {ho['frac_seq_info_by_roles']:.2f}", flush=True)
    (HERE / 'results' / 'role_transition_null.json').write_text(json.dumps(res, indent=1, ensure_ascii=False),
                                                                encoding='utf-8')

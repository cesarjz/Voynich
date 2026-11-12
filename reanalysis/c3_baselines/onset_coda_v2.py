"""Onset/coda asymmetry, second pass (critique 2026-11-10): three checks on the body result (STA1 1.95).

1. Non-Semitic controls: the 16 historical texts of common/control_texts.py (13 Gaskell & Bowern
   'meaningful' texts + Gutenberg Caesar, Dante, Simplicissimus), each subsampled to N_WORDS words.
2. Uncertainty without type-loss bias: the word bootstrap (with replacement) drops types and biases the
   type ratio downwards (STA1 1.95 in [1.57, 2.01]). Instead: K_SUB random subsamples of N_SUB words
   WITHOUT replacement, same N_SUB for every corpus -> mean and 2.5/97.5 % quantiles, comparable across corpora.
3. Is it just "Voynich words end in few glyphs"? Edge null: keep each word's first and last glyph (and its
   length), permute the interior glyphs within the word (B_EDGE reps). If the ratio survives, the asymmetry
   is carried by the edge-glyph inventories (a restatement of the known final-glyph restriction); if it falls
   to the within-word shuffle level, it needs multi-glyph unit structure. Also reported: distinct first /
   last glyphs and H(first glyph), H(last glyph).
Ratio = distinct onsets / distinct codas in two-unit O-C words (nb 36 pipeline, body Table 2).

Usage: python onset_coda_v2.py  -> results/onset_coda_v2.json  (parallel over jobs)
"""
import json
import math
import sys
from collections import Counter
from multiprocessing import Pool

import numpy as np

from onset_coda_null import ratios, corpora as semitic_corpora
from utilization_null import HERE, N_WORDS, C

sys.path.insert(0, str(HERE.parent / 'common'))
from control_texts import FULL, GUTENBERG, GB, GUT, text_lines  # noqa: E402

N_SUB, K_SUB, B_EDGE = 18000, 30, 10
SKIP = {'Torah homophonic L1', 'Moreh homophonic L1', 'Torah verbose-fixed', 'Torah verbose-homoph'}


def all_corpora():
    out = {k: v for k, v in semitic_corpora().items() if k not in SKIP}
    for n, f in FULL.items():
        out[n] = C.subsample([w for ln in text_lines(GB / 'meaningful' / 'texts' / f) for w in ln], N_WORDS)
    for n, fs in GUTENBERG.items():
        out[n] = C.subsample([w for f in fs for ln in text_lines(GUT / f) for w in ln], N_WORDS)
    return {k: [list(w) for w in v if w] for k, v in out.items()}


def entropy(cnt):
    n = sum(cnt.values())
    return -sum(c / n * math.log2(c / n) for c in cnt.values())


def edge_shuffle(words, rng):
    return [w if len(w) <= 3 else [w[0]] + list(rng.permutation(w[1:-1])) + [w[-1]] for w in words]


def job(args):
    name, words, kind, seed = args
    rng = np.random.default_rng(seed)
    if kind == 'obs':
        first, last = Counter(w[0] for w in words), Counter(w[-1] for w in words)
        return name, kind, {**ratios(words), 'reversed': ratios([w[::-1] for w in words])['pair'],
                            'n_words': len(words), 'n_first': len(first), 'n_last': len(last),
                            'H_first': entropy(first), 'H_last': entropy(last)}
    if kind == 'sub':
        n = min(N_SUB, len(words))
        idx = sorted(rng.choice(len(words), size=n, replace=False))
        return name, kind, ratios([words[i] for i in idx])['pair']
    if kind == 'edge':
        return name, kind, ratios(edge_shuffle(words, rng))['pair']
    if kind == 'shuf':
        return name, kind, ratios([list(rng.permutation(w)) for w in words])['pair']


def q(vals):
    a = np.array(vals, float)
    return {'mean': float(np.nanmean(a)), 'q025': float(np.nanquantile(a, .025)),
            'q975': float(np.nanquantile(a, .975))}


if __name__ == '__main__':
    corp = all_corpora()
    jobs = []
    for i, (name, words) in enumerate(corp.items()):
        jobs.append((name, words, 'obs', 0))
        jobs += [(name, words, 'sub', 1000 * i + k) for k in range(K_SUB)]
        jobs += [(name, words, 'edge', 2000 * i + k) for k in range(B_EDGE)]
        jobs += [(name, words, 'shuf', 3000 * i + k) for k in range(B_EDGE)]
    res = {n: {'sub': [], 'edge': [], 'shuf': []} for n in corp}
    with Pool(15) as pool:
        for name, kind, val in pool.imap_unordered(job, jobs, chunksize=1):
            if kind == 'obs':
                res[name]['obs'] = val
            else:
                res[name][kind].append(val)
    out = {'N_SUB': N_SUB, 'K_SUB': K_SUB, 'B_EDGE': B_EDGE, 'corpora': {}}
    for name in corp:
        r = res[name]
        o = r['obs']
        out['corpora'][name] = {**o, 'subsample': q(r['sub']), 'edge_null': q(r['edge']), 'shuffle_null': q(r['shuf'])}
        s, e, sh = q(r['sub']), q(r['edge']), q(r['shuf'])
        print(f"{name:24s} n={o['n_words']:6d} pair {o['pair_onsets']:4d}/{o['pair_codas']:4d}={o['pair']:.2f} "
              f"rev {o['reversed']:.2f} | sub{N_SUB} {s['mean']:.2f} [{s['q025']:.2f},{s['q975']:.2f}] | "
              f"edge {e['mean']:.2f} [{e['q025']:.2f},{e['q975']:.2f}] shuf {sh['mean']:.2f} | "
              f"first/last types {o['n_first']}/{o['n_last']} H {o['H_first']:.2f}/{o['H_last']:.2f}", flush=True)
    (HERE / 'results' / 'onset_coda_v2.json').write_text(json.dumps(out, indent=1, ensure_ascii=False),
                                                         encoding='utf-8')

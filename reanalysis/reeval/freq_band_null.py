"""Is a model's realism index (RI) just frequency matching? (Models 12/13 gave RI 0.29 / 0.13 on 2026-11-10.)

Same JSD and ceiling as run_ngram_reeval.py, but the mapping is permuted only WITHIN frequency bands of the decoding
keys (N_BANDS quantile bands of key token frequency). A mapping that only pairs frequent Voynich units with frequent
target units keeps that pairing under this null, so its RI relative to the banded null ('RI_band') drops to ~0;
a mapping that carries sequential information beyond frequency keeps RI_band > 0.
RI_band = (banded null mean - real) / (banded null mean - ceiling).

Usage: python freq_band_null.py [models...]  -> results/freq_band_null.json
"""
import json
import sys
import time
from collections import Counter

import numpy as np

import corpora as C
import ngram as N
from run_ngram_reeval import MODELS, OUT, build

B, N_BANDS = 300, 10


def run(num, spec, sta, syl_words, eva, targets):
    keys, tables, vocab, target, target_full = build(spec, sta, syl_words, eva, targets)
    G = len(vocab)
    units = sorted({tuple(v) for t in tables for v in t.values()})
    uid = {u: i for i, u in enumerate(units)}
    enc = N.Encoder({c for w in target_full for c in w} | {c for u in units for c in u})
    key_to_unit = np.zeros(G * len(tables), dtype=np.int64)
    for ti, t in enumerate(tables):
        key_to_unit[[ti * G + i for i in range(G)]] = [uid[tuple(t[g])] for g in vocab]
    freq = Counter(k for w in keys for k in w)
    used = np.array(sorted(freq), dtype=np.int64)
    f = np.array([freq[k] for k in used], float)
    order = used[np.argsort(-f, kind='stable')]
    groups = [g for g in np.array_split(order, N_BANDS) if len(g) > 1]
    corpus = N.DecodedCorpus(keys, units, enc)
    ref = N.corpus_dist(target, enc)
    real, null, _ = N.permutation_test(corpus, key_to_unit, groups, ref, B=B, seed=42)
    chosen = set(map(id, target))
    rest = [w for w in target_full if id(w) not in chosen]
    assert len(rest) == len(target_full) - len(target), 'ceiling sample not disjoint (target not drawn from target_full)'
    ceiling = N.jsd(N.corpus_dist(C.subsample(rest, len(target), seed=7), enc), ref)
    nm = float(null.mean())
    return {'model': num, 'name': spec['name'], 'jsd_real': real, 'band_null_mean': nm, 'ceiling': ceiling,
            'RI_band': (nm - real) / (nm - ceiling), 'p_band': (1 + int(np.sum(null <= real))) / (B + 1)}


if __name__ == '__main__':
    which = [int(a) for a in sys.argv[1:]] or [12, 13, 2, 7, 19]
    sta, syl_words = C.voynich_sta()
    eva = C.voynich_eva()
    cache = {}   # load each corpus once: the ceiling's disjointness check relies on object identity (fix 2026-11-11)
    cached = lambda fn: (lambda: cache.setdefault(fn.__name__, fn()))
    targets = {k: cached(f) for k, f in {'hebrew': C.torah_hebrew, 'aramaic': C.onkelos_aramaic, 'zohar': C.zohar_nb26,
               'tibbonid': C.tibbonid, 'judeo_arabic': C.judeo_arabic, 'geez': C.geez}.items()}
    rows = []
    for num in which:
        t0 = time.time()
        r = run(num, MODELS[num], sta, syl_words, eva, targets)
        rows.append(r)
        print(f"M{num:<2} {r['name']:26s} JSD={r['jsd_real']:.4f} band-null={r['band_null_mean']:.4f} "
              f"RI_band={r['RI_band']:+.3f} p={r['p_band']:.4f} [{time.time() - t0:.0f}s]", flush=True)
    (OUT / 'freq_band_null.json').write_text(json.dumps(rows, indent=1), encoding='utf-8')

"""B3/C3: rebuild the body Table "comparison" (two-tier metrics, Voynich vs natural languages)
with one shared pipeline.

The published table (copied from Paper 2, twotier_body.tex) is not reproduced by any notebook:
nb 36/38 give Voynich O->C 50.3 % (table 52.2 %) and Torah util 2.5 % (table "Hebrew" 1.7 %, which
matches the Moreh). Here every corpus goes through the nb 36 code (parser, TP-P20, classifier,
word patterns, class transitions), subsampled to the Voynich word count with the notebook seed.

Columns as in the paper: %F, %O-C (word patterns), Util. (2-syllable O-C words, nb 36 definition),
O->C (row-normalised class transition), onsets, codas; plus the utilization sampling null
(obs/null, from utilization_null.test) because raw utilization is not comparable across corpora.
Ge'ez: TraCES v1 full fidel and consonant-only; the old geez_processed.json (interleaved
annotation layers) is included only to show what produced the published row.

Usage: python comparison_table.py  -> results/comparison_table.json
"""
import json
from collections import Counter

import numpy as np

import utilization_null as U
from utilization_null import C, HERE, N_WORDS, voynich

U.B = 2000
CLASSES = ['onset', 'nuclear', 'coda', 'free']
ABBREV = {'onset': 'O', 'nuclear': 'N', 'coda': 'C', 'free': 'F'}


def geez_consonants():
    """Every fidel sign -> its row consonant (order-1 form), as c2_benchmark/geez_data.py (gkc)."""
    def base(ch):
        cp = ord(ch)
        return chr(cp - (cp - 0x1200) % 8) if 0x1200 <= cp <= 0x137F else ch
    return [[base(c) for c in w] for w in C.geez_clean()]


CORPORA = {
    'Voynich (STA1)': lambda: voynich,
    'Hebrew (Torah)': lambda: C.subsample(C.torah_hebrew(), N_WORDS),
    'Hebrew (Moreh, Tibbonid)': lambda: C.subsample(C.tibbonid(), N_WORDS),
    'Judeo-Arabic (Quran)': lambda: C.subsample(C.judeo_arabic(), N_WORDS),
    "Ge'ez (TraCES v1, fidel)": lambda: C.subsample(C.geez_clean(), N_WORDS),
    "Ge'ez (TraCES v1, consonants)": lambda: C.subsample(geez_consonants(), N_WORDS),
}
# The earlier Ge'ez export was removed from the public repository (TraCES licence); its row is computed only if present.
if (C.VOYNICH_DIR / 'corpus' / 'geez_processed.json').exists():
    CORPORA["Ge'ez (old geez_processed.json, buggy)"] = lambda: C.geez('words')


def metrics(words):
    clase, words_syl = U.pipeline([list(w) for w in words])
    cls = lambda s: clase.get(s, 'free')  # noqa: E731
    patterns = Counter('-'.join(ABBREV[cls(s)] for s in ws) for ws in words_syl)
    n = len(words_syl)
    trans = np.zeros((4, 4))
    ix = {c: i for i, c in enumerate(CLASSES)}
    for ws in words_syl:
        for a, b in zip(ws, ws[1:]):
            trans[ix[cls(a)], ix[cls(b)]] += 1
    rows = trans.sum(axis=1)
    util = U.test(U.pairs_nb36(clase, words_syl), np.random.default_rng(42))
    return {'n_words': len(words), 'n_chars': len({c for w in words for c in w}),
            'classes': dict(Counter(clase.values())),
            'pct_F': patterns['F'] / n, 'pct_OC': patterns['O-C'] / n,
            'util': util['observed_util'], 'util_obs_over_null': util['observed_over_null'],
            'oc_transition': trans[0, 2] / rows[0] if rows[0] else float('nan'),
            'onsets': util['onsets'], 'codas': util['codas'],
            'top_patterns': dict(patterns.most_common(6))}


if __name__ == '__main__':
    res = {'n_words_target': N_WORDS, 'B_null': U.B, 'corpora': {}}
    print(f"{'corpus':40s} {'words':>6s} {'chars':>5s} {'%F':>5s} {'%O-C':>5s} {'util':>5s} "
          f"{'obs/null':>8s} {'O->C':>5s} {'on':>4s} {'co':>4s}")
    for name, load in CORPORA.items():
        m = metrics(load())
        res['corpora'][name] = m
        print(f"{name:40s} {m['n_words']:6d} {m['n_chars']:5d} {m['pct_F']:5.1%} {m['pct_OC']:5.1%} "
              f"{m['util']:5.1%} {m['util_obs_over_null']:8.2f} {m['oc_transition']:5.1%} "
              f"{m['onsets']:4d} {m['codas']:4d}", flush=True)
    (HERE / 'results' / 'comparison_table.json').write_text(json.dumps(res, indent=1, ensure_ascii=False),
                                                            encoding='utf-8')

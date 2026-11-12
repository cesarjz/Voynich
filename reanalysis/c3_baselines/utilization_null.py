"""C3: is the 6.7 % onset x coda utilization lower than chance pairing?

Rebuilds the nb 36 O-C pairs with the notebook's own parser, TP-P20 segmentation and
syllable classifier, then compares the number of distinct (onset, coda) pairs with a
permutation null that shuffles codas across tokens: both marginals and the token count
are preserved exactly, only the pairing is randomised. Done for the three pairing
definitions used in the paper (nb 36, nb 48, nb 44), on the Voynich and on natural-language
controls (frozen corpora, subsampled to the Voynich word count, same pipeline) for calibration.

Direction: selectivity predicts FEWER distinct pairs than the null.
p = (1 + #{null <= observed}) / (B + 1)   (one-sided, lower tail)

Usage: python utilization_null.py  -> results/utilization_null.json
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / 'reeval'))
from nbcode import VOYNICH_DIR, load_defs  # noqa: E402
import corpora as C  # noqa: E402

B = 10000

ns = load_defs('36_silpart_structure.ipynb', ['parsear_sta_completo', 'tokens_a_palabras',
                                              'construir_matriz_transicion', 'segmentar_silabas_tp',
                                              'clasificar_silabas'])


def pipeline(palabras):
    """nb 36 cell 2: TP-P20 segmentation + positional syllable classes."""
    _, M_prob, _, index_tr = ns['construir_matriz_transicion'](palabras)
    flat, _ = ns['segmentar_silabas_tp'](palabras, M_prob, index_tr, 20)
    clase, _, words_syl = ns['clasificar_silabas'](flat, min_freq=5)
    return clase, words_syl


voynich = ns['tokens_a_palabras'](ns['parsear_sta_completo'](str(VOYNICH_DIR / 'corpus' / 'voynich_sta.txt')))
N_WORDS = len(voynich)
CORPORA = {
    'Voynich (STA1)': lambda: voynich,
    'Hebrew (Torah)': lambda: C.subsample(C.torah_hebrew(), N_WORDS),
    'Hebrew (Moreh, Tibbonid)': lambda: C.subsample(C.tibbonid(), N_WORDS),
    'Judeo-Arabic (Quran)': lambda: C.subsample(C.judeo_arabic(), N_WORDS),
    "Ge'ez": lambda: C.subsample(C.geez_clean(), N_WORDS),
}


def pairs_nb36(clase, words_syl):
    """2-syllable O-C words only (body §5, 166 x 85, 6.7 %)."""
    cls = lambda s: clase.get(s, 'free')  # noqa: E731
    return [(w[0], w[1]) for w in words_syl if len(w) == 2 and cls(w[0]) == 'onset' and cls(w[1]) == 'coda']


def pairs_nb48(clase, words_syl):
    """First syllable onset and last syllable coda, any word >= 2 syllables (Fig. 5, 164 x 87)."""
    cls = lambda s: clase.get(s, 'free')  # noqa: E731
    return [(w[0], w[-1]) for w in words_syl if len(w) >= 2 and cls(w[0]) == 'onset' and cls(w[-1]) == 'coda']


def pairs_nb44(clase, words_syl):
    """Every onset x every coda co-occurring in a word (Suppl., 148 x 83 after row/col >= 5)."""
    out = []
    for w in words_syl:
        os_ = [s for s in w if clase.get(s) == 'onset']
        cs = [s for s in w if clase.get(s) == 'coda']
        out += [(o, c) for o in os_ for c in cs]
    return out


def test(pairs, rng):
    on = np.array([hash(o) for o, _ in pairs])
    co = np.array([hash(c) for _, c in pairs])
    n_on, n_co = len(set(on)), len(set(co))
    obs = len(set(zip(on, co)))
    null = np.empty(B, dtype=np.int64)
    for b in range(B):
        null[b] = len(set(zip(on, rng.permutation(co))))
    cells = n_on * n_co
    return {'tokens': len(pairs), 'onsets': n_on, 'codas': n_co, 'cells': cells,
            'observed_pairs': obs, 'observed_util': obs / cells,
            'null_mean_pairs': float(null.mean()), 'null_sd_pairs': float(null.std(ddof=1)),
            'null_util_mean': float(null.mean() / cells),
            'null_util_q025_q975': [float(np.quantile(null, .025) / cells), float(np.quantile(null, .975) / cells)],
            'z': float((obs - null.mean()) / null.std(ddof=1)),
            'p_lower': float((1 + (null <= obs).sum()) / (B + 1)),
            'observed_over_null': float(obs / null.mean())}


if __name__ == '__main__':
    res = {'B': B, 'n_words': N_WORDS, 'corpora': {}}
    for cname, load in CORPORA.items():
        clase, words_syl = pipeline([list(w) for w in load()])
        n_cls = dict(Counter(clase.values()))
        print(f'== {cname}: {n_cls}', flush=True)
        res['corpora'][cname] = {'classes': n_cls, 'definitions': {}}
        for name, fn in (('nb36_2syl_OC', pairs_nb36), ('nb48_first_last', pairs_nb48), ('nb44_cooccur', pairs_nb44)):
            pairs = fn(clase, words_syl)
            if len(pairs) < 50:
                print(f'   {name:16s} too few pairs ({len(pairs)})')
                continue
            r = test(pairs, np.random.default_rng(42))
            res['corpora'][cname]['definitions'][name] = r
            print(f"   {name:16s} {r['onsets']}x{r['codas']} tokens={r['tokens']:,} obs={r['observed_pairs']} "
                  f"({r['observed_util']:.1%}) null={r['null_mean_pairs']:.0f}±{r['null_sd_pairs']:.0f} "
                  f"({r['null_util_mean']:.1%}) obs/null={r['observed_over_null']:.2f} z={r['z']:+.1f} "
                  f"p={r['p_lower']:.4f}", flush=True)
    (HERE / 'results' / 'utilization_null.json').write_text(json.dumps(res, indent=1, ensure_ascii=False),
                                                            encoding='utf-8')

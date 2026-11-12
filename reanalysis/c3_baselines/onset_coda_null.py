"""C3: is the onset/coda asymmetry (Voynich 166 onsets / 85 codas; every natural control has
more codas) a property of the text, or of the pipeline / alphabet size / encoding?

For each corpus, the nb 36 pipeline (TP-P20 + positional classifier) gives two ratios:
  pair   distinct onsets / distinct codas in 2-syllable O-C words (body Table, 166/85)
  class  syllable types classified onset / classified coda
Conditions:
  observed     + word-bootstrap 95 % CI (B_BOOT resamples of words with replacement)
  reversed     every word reversed: a direction effect (prefixing vs suffixing) should flip the ratio
  shuffled     glyphs permuted inside each word (B_SHUF reps): positional order destroyed, marginals kept
Controls for alphabet size / encoding: Torah and Moreh homophonic L1 (C2 data, ~150 symbols, same
size as the Voynich inventory) and Torah verbose ciphers (h1_verbose.verbose_cipher).

Usage: python onset_coda_null.py  -> results/onset_coda_null.json
"""
import json
import sys
from collections import Counter

import numpy as np

import utilization_null as U
from utilization_null import C, HERE, N_WORDS, voynich

sys.path.insert(0, str(HERE.parent / 'h1_verbose'))
from verbose_merge import verbose_cipher, geez_consonants  # noqa: E402

C2 = HERE.parent / 'c2_benchmark' / 'data'
B_BOOT, B_SHUF = 100, 20


def c2(name):
    return json.loads((C2 / f'{name}.json').read_text(encoding='utf-8'))['cipher_words']


def ratios(words):
    clase, words_syl = U.pipeline([list(w) for w in words])
    pairs = U.pairs_nb36(clase, words_syl)
    n_on, n_co = len({o for o, _ in pairs}), len({c for _, c in pairs})
    cls = Counter(clase.values())
    return {'pair_onsets': n_on, 'pair_codas': n_co, 'pair': n_on / n_co if n_co else float('nan'),
            'class_onsets': cls['onset'], 'class_codas': cls['coda'],
            'class': cls['onset'] / cls['coda'] if cls['coda'] else float('nan')}


def summary(vals):
    a = np.array(vals, dtype=float)
    return {'mean': float(np.nanmean(a)), 'q025': float(np.nanquantile(a, .025)),
            'q975': float(np.nanquantile(a, .975))}


def corpora():
    torah = C.subsample(C.torah_hebrew(), N_WORDS)
    return {
        'Voynich STA1': voynich,
        'Voynich EVA': C.subsample(C.voynich_eva(), N_WORDS),
        'Torah': torah,
        'Moreh': C.subsample(C.tibbonid(), N_WORDS),
        'Judeo-Arabic': C.subsample(C.judeo_arabic(), N_WORDS),
        "Ge'ez fidel": C.subsample(C.geez_clean(), N_WORDS),
        "Ge'ez consonants": C.subsample(geez_consonants(), N_WORDS),
        'Torah homophonic L1': C.subsample(c2('torah_holdout_L1'), N_WORDS),
        'Moreh homophonic L1': C.subsample(c2('moreh_L1'), N_WORDS),
        'Torah verbose-fixed': verbose_cipher(torah, 'fixed')[0],
        'Torah verbose-homoph': verbose_cipher(torah, 'homoph')[0],
    }


if __name__ == '__main__':
    res = {'B_boot': B_BOOT, 'B_shuf': B_SHUF, 'corpora': {}}
    for name, words in corpora().items():
        words = [list(w) for w in words if w]
        rng = np.random.default_rng(42)
        obs = ratios(words)
        rev = ratios([w[::-1] for w in words])
        shuf = [ratios([list(rng.permutation(w)) for w in words]) for _ in range(B_SHUF)]
        boot = [ratios([words[i] for i in rng.integers(len(words), size=len(words))]) for _ in range(B_BOOT)]
        r = {'n_symbols': len({c for w in words for c in w}), 'observed': obs, 'reversed': rev,
             'shuffled': {k: summary([s[k] for s in shuf]) for k in ('pair', 'class')},
             'bootstrap': {k: summary([b[k] for b in boot]) for k in ('pair', 'class')}}
        res['corpora'][name] = r
        print(f"{name:22s} V={r['n_symbols']:4d} | pair {obs['pair_onsets']}/{obs['pair_codas']}={obs['pair']:.2f} "
              f"[{r['bootstrap']['pair']['q025']:.2f},{r['bootstrap']['pair']['q975']:.2f}] "
              f"rev {rev['pair']:.2f} shuf {r['shuffled']['pair']['mean']:.2f} "
              f"[{r['shuffled']['pair']['q025']:.2f},{r['shuffled']['pair']['q975']:.2f}] | "
              f"class {obs['class_onsets']}/{obs['class_codas']}={obs['class']:.2f} rev {rev['class']:.2f} "
              f"shuf {r['shuffled']['class']['mean']:.2f}", flush=True)
    (HERE / 'results' / 'onset_coda_null.json').write_text(json.dumps(res, indent=1, ensure_ascii=False),
                                                           encoding='utf-8')

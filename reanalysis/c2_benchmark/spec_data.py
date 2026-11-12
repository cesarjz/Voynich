"""Specificity control for the calibrated Hebrew test (critique 2026-11-10): does any structured text that is NOT
Hebrew reach the Voynich's RI (STA1 +0.149) when decoded with the free pipelines against the full-Torah LM?

  ctl_LATIN  Caesar, De bello Gallico (Gutenberg), letters as opaque symbols: natural, non-Hebrew, simple substitution.
  ctl_LATL1  the same Latin enciphered at L1 (homophonic, STA1 glyph curve): ~166 symbols, like STA1.
  ctl_GEEZN  Ge'ez fidel from TraCES v1 (clean extraction), opaque: natural, non-Hebrew (replaces old ctl_GEEZ).
  ctl_SELF   copy-and-modify generator (c3_baselines.self_citation, Timm & Schinner style) on STA1 glyphs:
             meaningless, Voynich-like words.
  ctl_NAIB   Naibbe cipher (Greshko 2025; common/ciphers.py) of Pliny's Natural History (Latin):
             a verbose cipher of a real non-Hebrew text, EVA characters as opaque symbols.
Each is cut to N_WORDS words of length >= 2, as voy_STA.

Usage: python spec_data.py  (then run_c2.py --spec)
"""
import json
import sys
from collections import Counter

import numpy as np

import cipher as K
from cipher import C, DATA, HERE, N_WORDS
from voynich_data import opaque

sys.path.insert(0, str(HERE.parent / 'common'))
sys.path.insert(0, str(HERE.parent / 'c3_baselines'))
from control_texts import GB, GUT, text_lines  # noqa: E402
from self_citation import copy_modify  # noqa: E402
import ciphers as CI  # noqa: E402


def cut(words):
    return [list(w) for w in words if len(w) >= 2][:N_WORDS]


def main():
    latin = cut(w for f in ('pg218.txt', 'pg18837.txt') for ln in text_lines(GUT / f) for w in ln)
    classes, weights, key = K.build_key('L1', Counter(c for w in latin for c in w), K.sta_glyph_freqs(),
                                        np.random.default_rng(2052))
    sta, _ = C.voynich_sta()
    pliny = (GB / 'meaningful' / 'texts' / "Historical - Latin - Technical - Pliny's Natural History.txt"
             ).read_text(encoding='utf-8', errors='replace').splitlines()
    naib = cut(w for ln in CI.naibbe_lines(pliny, np.random.default_rng(2055)) for w in ln)
    sets = {
        'ctl_LATIN': (latin, None, None),
        'ctl_LATL1': (K.encipher(latin, classes, weights, np.random.default_rng(2053)), key, latin),
        'ctl_GEEZN': (cut(C.geez_clean()), None, None),
        'ctl_SELF': (cut(copy_modify(sta, 2 * N_WORDS, seed=2054)), None, None),
        'ctl_NAIB': (naib, None, None),
    }
    for n, (k, (words, key, plain_words)) in enumerate(sets.items()):
        plain, level = k.split('_')
        cw, names = opaque(words, seed=2060 + n) if key is None else (words, None)
        used = Counter(s for w in cw for s in w)
        print(f'{k:10s} {len(cw):,} words, {sum(used.values()):,} tokens, {len(used)} symbols')
        (DATA / f'{plain}_{level}.json').write_text(json.dumps({
            'plain': plain, 'level': level, 'cipher_words': cw, 'plain_words': plain_words,
            'key': key, 'symbol_names': names,
        }, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    main()

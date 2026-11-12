"""Calibrated stage-1 test: Voynich inputs and controls for the free M1/M7 pipelines.

All runs decode against the full-Torah LM, as in the Moreh benchmark condition (unknown text,
genre-shifted Hebrew LM), so their realism index is directly comparable with moreh L0-L2.

  voy_STA    STA1 Voynich words (166 glyphs), as in the paper.
  voy_EVA    EVA Voynich words (multi-character EVA tokens), second transcription.
  voy_SHUF   STA1 glyph tokens permuted across the whole corpus; word lengths and glyph
             frequencies kept, sequence destroyed (structureless negative control).
  ctl_GEEZ   Ge'ez text (188 fidel signs used as opaque symbols): a natural language
             that is not Hebrew (wrong-language negative control).
  ctl_JARAB  Judeo-Arabic enciphered at L1 (homophonic, STA1 curve): related Semitic
             language in the same alphabet (near-miss control).

Usage: python voynich_data.py
"""
import json
from collections import Counter

import numpy as np

import cipher as K
from cipher import C, DATA, N_WORDS


def opaque(words, seed):
    """Rename symbols to S000... so nothing about the source alphabet reaches the pipeline."""
    syms = sorted({g for w in words for g in w})
    perm = np.random.default_rng(seed).permutation(len(syms))
    name = {g: f'S{perm[i]:03d}' for i, g in enumerate(syms)}
    return [[name[g] for g in w] for w in words], {v: k for k, v in name.items()}


def main():
    sta, _ = C.voynich_sta()
    sta = [w for w in sta if len(w) >= 2]
    rng = np.random.default_rng(2031)
    toks = np.array([g for w in sta for g in w], dtype=object)
    rng.shuffle(toks)
    shuf, i = [], 0
    for w in sta:
        shuf.append(list(toks[i:i + len(w)]))
        i += len(w)

    jarab = C.judeo_arabic()[:N_WORDS]
    classes, weights, key = K.build_key('L1', Counter(c for w in jarab for c in w), K.sta_glyph_freqs(),
                                        np.random.default_rng(2032))
    sets = {
        'voy_STA': (sta, None, None),
        'voy_EVA': ([w for w in C.voynich_eva() if len(w) >= 2], None, None),
        'voy_SHUF': (shuf, None, None),
        'ctl_GEEZ': None,
        'ctl_JARAB': (K.encipher(jarab, classes, weights, np.random.default_rng(2033)), key, jarab),
    }
    # ctl_GEEZ used the earlier Ge'ez export (corpus/geez_processed.json), removed from the public repository
    # (TraCES licence; layered annotations). It is built only if that file is present; no other set depends on it.
    if (C.VOYNICH_DIR / 'corpus' / 'geez_processed.json').exists():
        sets['ctl_GEEZ'] = (C.geez()[:N_WORDS], None, None)
    else:
        print('ctl_GEEZ skipped: corpus/geez_processed.json not available')
    for n, (k, spec) in enumerate(sets.items()):
        if spec is None:
            continue
        words, key, plain_words = spec
        plain, level = k.split('_')
        cw, names = opaque(words, seed=2040 + n) if key is None else (words, None)
        used = Counter(s for w in cw for s in w)
        print(f'{k:10s} {len(cw):,} words, {sum(used.values()):,} tokens, {len(used)} symbols')
        (DATA / f'{plain}_{level}.json').write_text(json.dumps({
            'plain': plain, 'level': level, 'cipher_words': cw, 'plain_words': plain_words,
            'key': key, 'symbol_names': names,
        }, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    main()

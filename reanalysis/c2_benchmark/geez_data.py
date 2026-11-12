"""Calibrated Ge'ez test: the Torah design of cipher.py, with Ge'ez (TraCES v1).

  gkn_L0      positive control: Kebra Nagast (first 37,087 words of its graphic units),
              simple substitution onto opaque symbols; the LM never sees the Kebra Nagast.
  voyg_STA    STA1 Voynich words  } same inputs as voynich_data.py, decoded against the
  voyg_EVA    EVA Voynich words   } Ge'ez LM instead of the Hebrew one
  voyg_SHUF   STA1 tokens shuffled (structureless negative control)
  gkc_L0, voygc_*   the same with every fidel sign reduced to its consonant (first sign of its row
              of eight, U+1200-U+137F; other blocks kept): the vowel order is dropped, ~37 signs,
              the effective-alphabet profile closest to the Voynich's.
LM corpus (gkn_lm_corpus.json): the other ten TraCES texts (~76k words); train_lm subsamples
37,087 words, as for Hebrew. Kebra Nagast has 36.8k units, so the plaintext is all of it.

Usage: python geez_data.py
"""
import json
from collections import Counter

import numpy as np

import cipher as K
from cipher import C, DATA, N_WORDS


def consonant(ch):
    cp = ord(ch)
    return chr(0x1200 + (cp - 0x1200) // 8 * 8) if 0x1200 <= cp <= 0x137F else ch


def write_condition(plain, lm, name, seed):
    letter_freq = Counter(c for w in plain for c in w)
    rng = np.random.default_rng(seed)
    classes, weights, key = K.build_key('L0', letter_freq, None, rng)
    cw = K.encipher(plain, classes, weights, rng)
    (DATA / f'{name}_L0.json').write_text(json.dumps({'plain': name, 'level': 'L0', 'cipher_words': cw,
                                                      'plain_words': plain, 'key': key}, ensure_ascii=False),
                                          encoding='utf-8')
    (DATA / f'{name}_lm_corpus.json').write_text(json.dumps(lm, ensure_ascii=False), encoding='utf-8')
    print(f'{name}_L0: {len(cw):,} words, {len({s for w in cw for s in w})} symbols; LM corpus {len(lm):,} words, '
          f'{len({c for w in lm for c in w})} signs; plaintext signs unseen by LM: '
          f'{sorted(set(letter_freq) - {c for w in lm for c in w})}')


def main():
    texts = C.geez_texts()
    keep = lambda ws: [list(w) for w in ws if 2 <= len(w) <= 15]  # noqa: E731
    plain = keep([w for k, ws in texts.items() if k.startswith('KebraNagast/') for w in ws])[:N_WORDS]
    lm = keep([w for k, ws in texts.items() if not k.startswith('KebraNagast/') for w in ws])
    write_condition(plain, lm, 'gkn', 2050)
    cons = lambda ws: [[consonant(c) for c in w] for w in ws]  # noqa: E731
    write_condition(cons(plain), cons(lm), 'gkc', 2051)
    for pl in ('voyg', 'voygc'):
        for lv in ('STA', 'EVA', 'SHUF'):
            d = json.loads((DATA / f'voy_{lv}.json').read_text(encoding='utf-8'))
            d['plain'] = pl
            (DATA / f'{pl}_{lv}.json').write_text(json.dumps(d, ensure_ascii=False), encoding='utf-8')
        print(f'{pl}_STA/EVA/SHUF written')


if __name__ == '__main__':
    main()

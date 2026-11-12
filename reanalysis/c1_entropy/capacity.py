"""B7: what does "10.5 bits/word, 48 KB" measure?

nb 44 cell 9: bits/word = log2(#types) (uniform-choice upper bound), times words per page,
times pages. Here the same quantity is computed for every corpus at the Voynich word count,
next to two estimates that respect the actual frequency distribution and word order:
  - unigram Shannon entropy of word types (plug-in, bits/word);
  - LZMA-compressed size of the word sequence (each type -> one opaque symbol id, so the
    script's spelling does not matter), an upper bound on the information content.

Usage: python capacity.py  -> results/capacity.json
"""
import json
import lzma
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / 'reeval'))
import corpora as C  # noqa: E402

PAGES = 226  # STA1 pages, as in nb 44


def measures(words):
    words = [tuple(w) for w in words]
    n = len(words)
    cnt = Counter(words)
    p = np.array(list(cnt.values()), dtype=float) / n
    ids = {w: i for i, w in enumerate(cnt)}
    seq = b''.join(ids[w].to_bytes(2, 'little') for w in words)
    lz_bits = 8 * len(lzma.compress(seq, preset=9 | lzma.PRESET_EXTREME))
    return {'words': n, 'types': len(cnt),
            'log2_types': math.log2(len(cnt)),
            'unigram_H': float(-(p * np.log2(p)).sum()),
            'lzma_bits_per_word': lz_bits / n,
            'nb44_style_KB': n * math.log2(len(cnt)) / 8 / 1000,
            'unigram_KB': n * float(-(p * np.log2(p)).sum()) / 8 / 1000,
            'lzma_KB': lz_bits / 8 / 1000}


if __name__ == '__main__':
    voy, _ = C.voynich_sta()
    N = len(voy)
    rng = np.random.default_rng(0)
    corpora = {
        'Voynich STA1': voy,
        'Voynich EVA': C.voynich_eva(),
        'Voynich STA1, word order shuffled': [voy[i] for i in rng.permutation(N)],
        'Hebrew Torah': C.subsample(C.torah_hebrew(), N),
        'Hebrew Moreh (Tibbonid)': C.subsample(C.tibbonid(), N),
        'Judeo-Arabic (Quran)': C.subsample(C.judeo_arabic(), N),
        "Ge'ez": C.subsample(C.geez_clean(), N),
    }
    res = {}
    print(f"{'corpus':36s} {'words':>6} {'types':>6} {'log2V':>6} {'H1':>6} {'LZMA':>6}   KB: nb44 / H1 / LZMA")
    for k, w in corpora.items():
        r = res[k] = measures(w)
        print(f"{k:36s} {r['words']:6d} {r['types']:6d} {r['log2_types']:6.2f} {r['unigram_H']:6.2f} "
              f"{r['lzma_bits_per_word']:6.2f}   {r['nb44_style_KB']:5.1f} / {r['unigram_KB']:5.1f} / {r['lzma_KB']:5.1f}")
    (HERE / 'results' / 'capacity.json').write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding='utf-8')

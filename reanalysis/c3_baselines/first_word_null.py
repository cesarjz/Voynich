"""C3: is first-T2-word uniqueness per page higher than for any T2 word of the page?

nb 43 reports ~99 % of pages start with a distinct first Tier-2 word ("unique identifiers").
Null: for each page take a random T2 token from that page instead of the first; repeat B times.
Also the T2 word at position 2, 5 and 10 of the page (by T2 order). Pages = STA1 loci (nb 76 parser),
tiers from the nb 76 TP-P20 pipeline (T1 = single free syllable).

Usage: python first_word_null.py  -> results/first_word_null.json
"""
import contextlib
import io
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / 'reeval'))
from nbcode import VOYNICH_DIR  # noqa: E402

B = 2000
nb = json.loads((VOYNICH_DIR / '76_role_grammar_and_sections.ipynb').read_text(encoding='utf-8'))
os.chdir(VOYNICH_DIR)
ns = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(''.join(nb['cells'][1]['source']), ns)
recs = ns['parsear_sta_con_folios'](ns['STA_PATH'])
pal = [r['glyphs'] for r in recs]  # per-page records; same TP-P20 pipeline run on them
M, Mp, _, idx = ns['construir_matriz_transicion'](pal)
flat, _ = ns['segmentar_silabas_tp'](pal, Mp, idx, 20)
cls, words = ns['clasificar_silabas'](flat, 5)
assert len(words) == len(pal)

page_t2 = defaultdict(list)
for r, ws in zip(recs, words):
    tier = 'T1' if len(ws) == 1 and cls.get(ws[0], 'free') == 'free' else 'T2'
    if tier == 'T2':
        page_t2[r['folio']].append('.'.join(r['glyphs']))
pages = [p for p in page_t2 if page_t2[p]]


def uniq(words):
    return len(set(words)) / len(words)


res = {'pages': len(pages)}
for k in (0, 1, 4, 9):
    ws = [page_t2[p][k] for p in pages if len(page_t2[p]) > k]
    res[f'T2_position_{k + 1}'] = {'n': len(ws), 'uniqueness': uniq(ws)}
rng = np.random.default_rng(42)
null = np.array([uniq([page_t2[p][rng.integers(len(page_t2[p]))] for p in pages]) for _ in range(B)])
res['random_T2_token'] = {'mean': float(null.mean()), 'q025': float(np.quantile(null, .025)),
                          'q975': float(np.quantile(null, .975))}
res['p_first_ge_random'] = float((1 + (null >= res['T2_position_1']['uniqueness']).sum()) / (B + 1))
print(json.dumps(res, indent=1))
(HERE / 'results' / 'first_word_null.json').write_text(json.dumps(res, indent=1), encoding='utf-8')

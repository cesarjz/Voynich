"""B4/B5/B6 + C5: re-run the nb 76 leave-one-out section classifier.

1. verbatim (folio-number ranges, as published: 150/226 = 66.4 %);
2. with sections taken from the STA1 page metadata ($I illustration type, Zandbergen),
   text-only pages ($I=T) excluded.
Cells 1 and 4 of nb 76 are executed verbatim; only `classify_folio` is swapped.

Usage: python sections_rerun.py  -> results/sections_rerun.json
"""
import contextlib
import io
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use('Agg')

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / 'reeval'))
from nbcode import VOYNICH_DIR  # noqa: E402

NB = json.loads((VOYNICH_DIR / '76_role_grammar_and_sections.ipynb').read_text(encoding='utf-8'))
CELL1, CELL4 = (''.join(NB['cells'][i]['source']) for i in (1, 7))
STA = VOYNICH_DIR / 'corpus' / 'voynich_sta.txt'

I_TO_SECTION = {'H': 'herbal', 'A': 'astro', 'C': 'cosmo', 'Z': 'zodiac', 'B': 'bio', 'P': 'pharma', 'S': 'recipe'}


def page_I():
    out = {}
    for line in STA.read_text(encoding='utf-8').splitlines():
        m = re.match(r'^<(f\d+[rv]\d*)>\s*<!(.*)>', line.strip())
        if m:
            out[m.group(1)] = dict(re.findall(r'\$(\w)=(\w+)', m.group(2))).get('I', '?')
    return out


def run(patch=None):
    os.chdir(VOYNICH_DIR)
    ns = {}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(CELL1, ns)
        if patch:
            for rec in ns['records']:
                rec['section'] = patch(rec['folio'])
            ns['SECTIONS'] = sorted({r['section'] for r in ns['records'] if r['section'] != 'unknown'})
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(CELL4, ns)
    n_by = Counter(ns['folio_sections'].values())
    return {'sections': list(ns['SECTIONS']), 'n_core_glyphs': len(ns['core_glyph_list']),
            'correct': ns['correct'], 'total': ns['total'], 'accuracy': ns['accuracy'],
            'largest_class': max(n_by.values()) / ns['total'], 'pages_per_section': dict(n_by),
            'confusion': {t: dict(c) for t, c in ns['confusion'].items()}, 'stdout': buf.getvalue()}


if __name__ == '__main__':
    I = page_I()
    res = {'published_ranges': run(),
           'sta_I_metadata': run(lambda f: I_TO_SECTION.get(I.get(f, '?'), 'unknown'))}
    for k, r in res.items():
        print(f"== {k}: {r['correct']}/{r['total']} = {r['accuracy']:.1%} (largest class {r['largest_class']:.1%}), "
              f"features = {r['n_core_glyphs']} core glyphs\n   pages/section {r['pages_per_section']}")
        print('\n'.join(r['stdout'].splitlines()[2:]))
    (HERE / 'results' / 'sections_rerun.json').write_text(json.dumps(res, indent=1), encoding='utf-8')

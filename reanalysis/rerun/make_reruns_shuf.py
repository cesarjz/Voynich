"""Capacity control for Models 12/13 (2026-11-10): the R1 copies of nb 20 / 21 run on STA1 glyphs permuted across
the whole corpus (word lengths and glyph frequencies kept, sequence destroyed; seed 2031 as c2 voy_SHUF).
If the shuffled input reaches a realism index similar to the real one (12: 0.287, 13: 0.126), those values come
from the models' capacity / frequency matching, not from the text.
Writes 20_..._R1shuf.ipynb / 21_..._R1shuf.ipynb; outputs syl2syl_shuf_* / nucleus_shuf_*.
Run: jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 <nb>
then ../reeval: add 'stored' specs syl2syl_shuf / nucleus_shuf (see reeval/shuf_models.py).
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
SHUF = """
# ── R1 capacity control: glyphs permuted across the corpus (lengths kept) ──
import numpy as _np
_r = _np.random.default_rng(2031)
_toks = [g for w in {var} for g in w]
_r.shuffle(_toks)
_out, _i = [], 0
for _w in {var}:
    _out.append(type(_w)(_toks[_i:_i + len(_w)]) if not isinstance(_w, str) else ''.join(_toks[_i:_i + len(_w)]))
    _i += len(_w)
{var} = _out
"""
SPECS = {'20_syllable_to_syllable_R1.ipynb': ('palabras = tokens_a_palabras(tokens_v)', 'palabras', 'syl2syl'),
         '21_nucleus_only_R1.ipynb': ('words = tokens_to_words(tokens)', 'words', 'nucleus')}
for nb, (anchor, var, name) in SPECS.items():
    d = json.loads((HERE / nb).read_text(encoding='utf-8'))
    hits = 0
    for c in d['cells']:
        if c['cell_type'] != 'code':
            continue
        c['outputs'], c['execution_count'] = [], None
        t = ''.join(c['source'])
        if anchor in t:
            t = t.replace(anchor, anchor + '\n' + SHUF.format(var=var))
            hits += 1
        t = t.replace(f'{name}_mapping.json', f'{name}_shuf_mapping.json').replace(
            f'{name}_resultados.json', f'{name}_shuf_resultados.json')
        c['source'] = t
    assert hits == 1, (nb, hits)
    out = HERE / nb.replace('_R1.ipynb', '_R1shuf.ipynb')
    out.write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding='utf-8')
    print('wrote', out.name)

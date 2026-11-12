"""Build patched copies of nb 20 / 21 for the R1 n-gram re-evaluation.

Patches (public notebooks are left untouched):
  1. Hebrew Torah read from the frozen Sefaria copy (original URLs are dead).
  2. Voynich STA path made absolute (notebooks run from this folder).
  3. nb 20 only: n-gram percentile bug (`np.mean([1 ...]) / len` -> fraction), and
     `batch_log_prob` restored to iterate over its `words` argument (the 2026-03-13
     translation pass renamed it to the global `palabras`; results were produced before).
  4. Store the decoding input + learned mapping for reeval/.
"""
import json
from pathlib import Path

VOY = Path(__file__).resolve().parents[2]
SEF = str(VOY / 'corpus' / 'sefaria' / 'torah_hebrew')
HERE = Path(__file__).parent

FETCH = [
    ("resp = requests.get(url, timeout=30)\n        resp.raise_for_status()\n        data = resp.json()",
     f"data = json.load(open(f'{SEF}/{{libro}}.json', encoding='utf-8'))"),
    ("resp = requests.get(url, timeout=30)\n        resp.raise_for_status()\n        data = resp.json()",
     f"data = json.load(open(f'{SEF}/{{book}}.json', encoding='utf-8'))"),
]
STA = ("'corpus/voynich_sta.txt'", f"'{VOY}/corpus/voynich_sta.txt'")

SAVE = """
# ── R1: store decoding input + mapping for the unified n-gram re-evaluation ──
_j = lambda u: list(u) if isinstance(u, (tuple, list)) else [u]
with open('{name}_mapping.json', 'w') as f:
    json.dump({{'units': 'syllables' if {syl} else 'glyphs',
               'words': [[_j(k) for k in w] for w in {words}],
               'mapping': [[_j(k), _j(v)] for k, v in mapping_final.items()]}},
              f, ensure_ascii=False)
print('Mapping saved to {name}_mapping.json')
"""

SPECS = {
    '20_syllable_to_syllable.ipynb': dict(
        fetch=FETCH[0], name='syl2syl', syl=True, words='words_syl_v',
        extra=[("ngram_pct = 100 * np.mean([1 for x in null_ngrams if real_ngram > x]) / len(null_ngrams)",
                "ngram_pct = 100 * np.mean([real_ngram > x for x in null_ngrams])  # R1 fix"),
               ("return np.zeros(len(palabras))", "return np.zeros(len(words))"),
               ("word_lps = np.zeros(len(palabras))\n            for wi in range(len(palabras)):",
                "word_lps = np.zeros(len(words))\n            for wi in range(len(words)):")]),
    '21_nucleus_only.ipynb': dict(
        fetch=FETCH[1], name='nucleus', syl=False, words='words_content', extra=[]),
}

import sys
for nb, s in SPECS.items():
    if len(sys.argv) > 1 and nb[:2] not in sys.argv[1:]:
        continue
    d = json.loads((VOY / nb).read_text(encoding='utf-8'))
    for c in d['cells']:
        if c['cell_type'] == 'code':
            c['outputs'], c['execution_count'] = [], None
    src = ['' .join(c['source']) for c in d['cells']]
    for old, new in [s['fetch'], STA] + s['extra']:
        hits = [i for i, t in enumerate(src) if old in t]
        assert len(hits) == 1, (nb, old[:40], hits)
        src[hits[0]] = src[hits[0]].replace(old, new)
    last = max(i for i, t in enumerate(src) if 'json.dump(results' in t)
    src[last] += SAVE.format(**s)
    for c, t in zip(d['cells'], src):
        c['source'] = t
    out = HERE / nb.replace('.ipynb', '_R1.ipynb')
    out.write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding='utf-8')
    print('wrote', out.name)

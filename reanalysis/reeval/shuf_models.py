"""Score the capacity-control re-runs of Models 12/13 (rerun/make_reruns_shuf.py: shuffled STA1 input) with the
same RI as run_ngram_reeval.py, next to the real-input values.
Usage: python shuf_models.py -> results/shuf_models.json
"""
import json

import corpora as C
from run_ngram_reeval import MODELS, OUT, run_model

SPECS = {'12': MODELS[12], '12-shuf': {'name': 'Syllable-to-syllable, shuffled input', 'stored': 'syl2syl_shuf',
                                       'target': 'hebrew'},
         '13': MODELS[13], '13-shuf': {'name': 'Nucleus-only, shuffled input', 'stored': 'nucleus_shuf',
                                       'target': 'hebrew'}}
sta, syl_words = C.voynich_sta()
eva = C.voynich_eva()
_heb = C.torah_hebrew()   # load once: the ceiling's disjointness check relies on object identity (fix 2026-11-11)
targets = {'hebrew': lambda: _heb}
rows = []
for k, spec in SPECS.items():
    r = run_model(k, spec, sta, syl_words, eva, targets, 1000)
    rows.append(r)
    print(f"{k:8s} {spec['name']:38s} RI={r['realism_index']:+.3f} p={r['p_value']:.4f}", flush=True)
(OUT / 'shuf_models.json').write_text(json.dumps(rows, indent=1), encoding='utf-8')

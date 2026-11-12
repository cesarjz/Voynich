"""EVA row of body Table 2 (same nb 36 pipeline as comparison_table.py, ZL EVA characters as units).
Usage: python comparison_table_eva.py -> results/comparison_table_eva.json
"""
import json

from comparison_table import metrics
from utilization_null import C, HERE, N_WORDS

m = metrics(C.subsample(C.voynich_eva(), N_WORDS))
print(f"Voynich EVA {m['n_words']} words {m['n_chars']} chars %F {m['pct_F']:.1%} %O-C {m['pct_OC']:.1%} "
      f"util {m['util']:.1%} obs/null {m['util_obs_over_null']:.2f} O->C {m['oc_transition']:.1%} "
      f"on/co {m['onsets']}/{m['codas']}")
(HERE / 'results' / 'comparison_table_eva.json').write_text(json.dumps(m, indent=1), encoding='utf-8')

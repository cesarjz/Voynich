"""Load function/class definitions verbatim from the original notebooks.

The re-evaluation must use exactly the same corpus parsing and syllable
segmentation as the published runs, so instead of re-implementing them we
pull the top-level definitions out of the notebook source and exec them.
"""
import ast
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

VOYNICH_DIR = Path(__file__).resolve().parents[2]      # repository root (notebooks, corpus/)
REANALYSIS_DIR = VOYNICH_DIR / 'reanalysis'
EXTERNAL_DIR = REANALYSIS_DIR / 'external'             # third-party data fetched by fetch_external.sh


def _notebook_source(nb_name):
    nb = json.loads((VOYNICH_DIR / nb_name).read_text(encoding='utf-8'))
    src = '\n'.join(''.join(c['source']) for c in nb['cells'] if c['cell_type'] == 'code')
    # Drop IPython magics / shell escapes so the source parses as plain Python.
    return '\n'.join(l for l in src.splitlines() if not l.lstrip().startswith(('%', '!')))


def load_defs(nb_name, names):
    """Return a namespace holding the named top-level defs from a notebook."""
    src = _notebook_source(nb_name)
    tree = ast.parse(src)
    found = {}
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names:
            found[n.name] = n
        elif isinstance(n, ast.Assign):  # module-level constants, e.g. EVA_MULTI
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id in names:
                    found[t.id] = n
    missing = set(names) - set(found)
    if missing:
        raise KeyError(f'{nb_name}: definitions not found: {sorted(missing)}')
    ns = {'re': re, 'json': json, 'math': math, 'np': np,
          'Counter': Counter, 'defaultdict': defaultdict}
    for name in names:  # keep caller's order so dependencies resolve
        exec(compile(ast.Module([found[name]], []), f'{nb_name}:{name}', 'exec'), ns)
    return ns

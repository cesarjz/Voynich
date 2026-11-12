"""Print text outputs of a re-run notebook pair, cell by cell, filtered by a regex."""
import json
import re
import sys

name, pat = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else '.'
for v in ('orig', 'I'):
    nb = json.load(open(f'out/{name}_{v}.ipynb'))
    print(f'################ {v}')
    for i, c in enumerate(nb['cells']):
        txt = ''.join(''.join(o.get('text', '')) for o in c.get('outputs', []))
        lines = [l for l in txt.splitlines() if re.search(pat, l)]
        if lines:
            print(f'--- cell {i}')
            print('\n'.join(lines[:40]))

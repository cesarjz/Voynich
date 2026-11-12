"""Re-evaluate the n-gram realism test for every stored decipherment mapping.

Usage:  .venv/bin/python run_ngram_reeval.py [--B 1000]
Writes results/ngram_reeval.json and results/ngram_reeval.md.
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np

import corpora as C
import ngram as N

RESULTS_DIR = Path(__file__).parent / 'stored_results'   # original notebook outputs (Zenodo v1, results/)
OUT = Path(__file__).parent / 'results'
RERUN_DIR = Path(__file__).parent.parent / 'rerun'
THRESH = json.loads((Path(__file__).parent / 'thresholds.json').read_text())['ngram']

# Values reported in the earlier versions (Paper 1, Table 2).
OLD = {1: '24%', 2: '5%', 3: '28%', 5: '38%', 6: '12%', 7: '68%', 8: '14%', 9: '6%', 12: '0.1%', 13: '100%',
       10: '23%', 11: '22%', 14: '0%', 15: '16%', 16: '0%', 17: '13%', 18: '12%', 19: '0%'}


def load(name):
    return json.loads((RESULTS_DIR / f'{name}_resultados.json').read_text(encoding='utf-8'))


def verdict(p):
    return 'PASS' if p < 0.05 else ('MARGINAL' if p < 0.20 else 'FAIL')


def positional_keys(words, syl_words, glyph_id, G):
    """Key = table*G + glyph, table from intra-syllable position (nb 15 logic)."""
    table = {'onset': 0, 'nucleus': 1, 'coda': 2}
    out = []
    for w, syls in zip(words, syl_words):
        pos = []
        for syl in syls:
            n = len(syl)
            for i in range(n):
                if n == 1:
                    pos.append('nucleus')
                elif n == 2:
                    pos.append('onset' if i == 0 else 'coda')
                else:
                    pos.append('onset' if i == 0 else ('coda' if i == n - 1 else 'nucleus'))
        out.append([table[pos[i] if i < len(pos) else 'nucleus'] * G + glyph_id[g]
                    for i, g in enumerate(w)])
    return out


def build(spec, sta, syl_words, eva, targets):
    """Return words-as-keys, list of tables {glyph: unit}, glyph vocabulary, target words."""
    if 'stored' in spec:
        # nb 20/21 R1 re-runs: decoding input (syllables or nucleus glyphs) stored with the mapping.
        res = json.loads((RERUN_DIR / f"{spec['stored']}_mapping.json").read_text(encoding='utf-8'))
        words = [[tuple(k) for k in w] for w in res['words']]
        tables = [{tuple(k): v for k, v in res['mapping']}]
        vocab = sorted({k for w in words for k in w})
        gid = {k: i for i, k in enumerate(vocab)}
        keys = [[gid[k] for k in w] for w in words]
        target = C.subsample(targets[spec['target']](), len(words))
        return keys, tables, vocab, target, targets[spec['target']]()
    res = load(spec['json'])
    words = eva if spec.get('eva') else sta
    if 'tables' in spec:
        tables = [res[t] for t in spec['tables']]
    elif spec.get('allograph'):
        words = C.allograph_rewrite(sta, res['clustering']['cluster_map'])
        tables = [res['mapping']]
    else:
        m = res['mapping']
        tables = [m[spec['sub']] if 'sub' in spec else m]
    vocab = sorted({g for w in words for g in w})
    G = len(vocab)
    gid = {g: i for i, g in enumerate(vocab)}
    if len(tables) == 3:
        keys = positional_keys(words, syl_words, gid, G)
    else:
        keys = [[gid[g] for g in w] for w in words]
    target = C.subsample(targets[spec['target']](), len(words))
    return keys, tables, vocab, target, targets[spec['target']]()


def run_model(num, spec, sta, syl_words, eva, targets, B):
    keys, tables, vocab, target, target_full = build(spec, sta, syl_words, eva, targets)
    G = len(vocab)
    units = sorted({tuple(v) for t in tables for v in t.values()})
    uid = {u: i for i, u in enumerate(units)}
    enc = N.Encoder({c for w in target_full for c in w} | {c for u in units for c in u})
    key_to_unit = np.zeros(G * len(tables), dtype=np.int64)
    groups = []
    for ti, t in enumerate(tables):
        missing = [g for g in vocab if g not in t]
        if missing:
            raise ValueError(f'model {num}: table {ti} lacks {len(missing)} glyphs, e.g. {missing[:3]}')
        idx = np.array([ti * G + i for i in range(G)])
        key_to_unit[idx] = [uid[tuple(t[g])] for g in vocab]
        groups.append(idx)
    corpus = N.DecodedCorpus(keys, units, enc)
    ref = N.corpus_dist(target, enc)
    real, null, p = N.permutation_test(corpus, key_to_unit, groups, ref, B=B, seed=42)

    # Ceiling: genuine target text vs the reference sample (disjoint words).
    chosen = set(map(id, target))
    rest = [w for w in target_full if id(w) not in chosen]
    assert len(rest) == len(target_full) - len(target), 'ceiling sample not disjoint (target not drawn from target_full)'
    ceiling = N.jsd(N.corpus_dist(C.subsample(rest, len(target), seed=7), enc), ref)
    null_mean = float(null.mean())
    return {
        'model': num, 'name': spec['name'], 'target': spec['target'],
        'n_voynich_words': len(keys), 'n_target_words': len(target),
        'jsd_real': real, 'jsd_null_mean': null_mean, 'jsd_null_sd': float(null.std(ddof=1)),
        'jsd_ceiling': ceiling,
        'z': (real - null_mean) / float(null.std(ddof=1)),
        'realism_index': (null_mean - real) / (null_mean - ceiling),
        'p_value': p, 'verdict': verdict(p), 'old_reported': OLD.get(num),
    }


MODELS = {
    1: {'name': 'Compositional', 'json': 'composicional', 'sub': 'Hebreo', 'target': 'hebrew'},
    2: {'name': 'Constrained EM', 'json': 'constrained', 'target': 'hebrew'},
    3: {'name': 'Homophonic positional', 'json': 'homofonico', 'target': 'hebrew'},
    5: {'name': 'Neural v1', 'json': 'neural', 'target': 'hebrew'},
    6: {'name': 'Lexical S_root', 'json': 'lexical', 'target': 'hebrew'},
    7: {'name': 'Neural v2', 'json': 'neural_v2', 'target': 'hebrew'},
    8: {'name': 'Syllabic-positional (Heb)', 'json': 'syllabic', 'target': 'hebrew',
        'tables': ['mapping_onset', 'mapping_nucleus', 'mapping_coda']},
    9: {'name': 'Syllabic-positional (Ara)', 'json': 'syllabic_arameo', 'target': 'aramaic',
        'tables': ['mapping_onset', 'mapping_nucleus', 'mapping_coda']},
    10: {'name': 'Allograph collapse', 'json': 'allograph', 'target': 'hebrew', 'allograph': True},
    11: {'name': 'Syllabic homophonic', 'json': 'syllabic_homophonic', 'target': 'hebrew'},
    12: {'name': 'Syllable-to-syllable', 'stored': 'syl2syl', 'target': 'hebrew'},
    13: {'name': 'Nucleus-only', 'stored': 'nucleus', 'target': 'hebrew'},
    14: {'name': 'Neural v2 (EVA)', 'json': 'neural_v2_eva', 'target': 'hebrew', 'eva': True},
    15: {'name': 'Morphological', 'json': 'morphological', 'target': 'hebrew'},
    16: {'name': 'Morphological (Zohar)', 'json': 'morphological_zohar', 'target': 'zohar'},
    17: {'name': 'Tibbonid Hebrew', 'json': 'tibbonid', 'target': 'tibbonid'},
    18: {'name': 'Judeo-Arabic', 'json': 'judeo_arabic', 'target': 'judeo_arabic'},
    19: {'name': "Ge'ez", 'json': 'geez', 'target': 'geez'},
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--B', type=int, default=THRESH['B'])
    ap.add_argument('--only', type=int, nargs='*')
    args = ap.parse_args()

    sta, syl_words = C.voynich_sta()
    eva = C.voynich_eva()
    cache = {}

    def cached(fn):
        return lambda: cache.setdefault(fn.__name__, fn())

    targets = {'hebrew': cached(C.torah_hebrew), 'aramaic': cached(C.onkelos_aramaic),
               'zohar': cached(C.zohar_nb26), 'tibbonid': cached(C.tibbonid),
               'judeo_arabic': cached(C.judeo_arabic), 'geez': cached(C.geez)}

    OUT.mkdir(exist_ok=True)
    rows = []
    for num, spec in MODELS.items():
        if args.only and num not in args.only:
            continue
        t0 = time.time()
        r = run_model(num, spec, sta, syl_words, eva, targets, args.B)
        rows.append(r)
        print(f"M{num:<2} {spec['name']:28s} JSD={r['jsd_real']:.4f} null={r['jsd_null_mean']:.4f}"
              f"±{r['jsd_null_sd']:.4f} ceil={r['jsd_ceiling']:.4f} RI={r['realism_index']:+.3f}"
              f" p={r['p_value']:.4f} {r['verdict']:8s} (old {r['old_reported']})"
              f"  [{time.time() - t0:.0f}s]", flush=True)

    meta = {'protocol': THRESH, 'B': args.B,
            'not_reevaluated': {'4': 'semantic cross-validation, no mapping',
},
            'rerun': {'12': 'notebook 20 re-run for R1 (rerun/20_syllable_to_syllable_R1.ipynb)',
                      '13': 'notebook 21 re-run for R1 (rerun/21_nucleus_only_R1.ipynb)'}}
    (OUT / 'ngram_reeval.json').write_text(json.dumps({'meta': meta, 'rows': rows}, indent=1, ensure_ascii=False))
    lines = ['| # | Model | Target | JSD real | Null mean ± sd | Ceiling | Realism idx | p | Verdict | Old reported |',
             '|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        lines.append(f"| {r['model']} | {r['name']} | {r['target']} | {r['jsd_real']:.4f} | "
                     f"{r['jsd_null_mean']:.4f} ± {r['jsd_null_sd']:.4f} | {r['jsd_ceiling']:.4f} | "
                     f"{r['realism_index']:+.3f} | {r['p_value']:.4f} | {r['verdict']} | {r['old_reported']} |")
    (OUT / 'ngram_reeval.md').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()

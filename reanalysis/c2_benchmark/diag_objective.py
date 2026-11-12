"""C2 diagnostic: does the pipeline objective prefer the true key over the found mapping?

If score(true key) > score(found) the failure is in the search; if score(true key) < score(found)
the objective itself rewards wrong solutions. Scores use exactly the objective each pipeline
optimises (nb 07 score_total_comp_fast; nb 14 score_total_neural with SCORE_KW), on the same
word sample, with every component reported separately.

Usage: python diag_objective.py   → results/diag_objective.json
"""
import json
import os

os.environ['CUDA_VISIBLE_DEVICES'] = ''
import numpy as np  # noqa: E402
import torch  # noqa: E402

import run_c2 as R  # noqa: E402

torch.set_num_threads(8)


def found_mapping(r):
    tag = r.replace(':', '_')
    chains = [R.load_job(f'{tag}_{"m1c" if r.startswith("M1") else "m7c"}{i}') for i in range(4)]
    return max(chains, key=lambda x: x['best_score'])['mapping']


def m7_T(r):
    tag = r.replace(':', '_')
    ems = [R.load_job(p.stem) for p in R.JOBS.glob(f'{tag}_*.json')
           if p.stem[len(tag) + 1] in 'AB' and not p.stem.endswith(('_cal',))]
    return R.m7_select(ems)['T']


def score(r, c, mapping, T=None):
    ns = c['ns']
    st = ns['GlyphMappingState'](c['VOCAB'], c['target_chars'], c['glyph_role'], c['char_role'])
    st.set_mapping(mapping)
    if r.startswith('M1'):
        rng = np.random.default_rng(42)  # em_glyph_decipher sample
        idx = rng.choice(len(c['palabras']), size=3000, replace=False)
        ws = [c['palabras'][i] for i in idx]
        lm = float(np.mean([c['lm'].log_prob(st.apply_word(w)) for w in ws]))
        pos = float(ns['score_positional'](st, c['glyph_role'], c['char_role']))
        return {'total': 2.0 * lm + 0.5 * pos, 'lm': lm, 'pos': pos}
    kw = R.M7_KW
    lm, _ = ns['score_neural_lm_batch'](st, c['words_em'], c['lm'], T)
    comp = {'lm': float(lm),
            'pos': float(ns['score_positional'](st, c['glyph_role'], c['char_role'])),
            'card': float(ns['score_cardinality'](st, kw['K_max'])),
            'ent': float(ns['score_entropy'](st)),
            'gram': float(ns['score_grammar'](st, c['anchors']))}
    total, _ = ns['score_total_neural'](st, c['words_em'], c['lm'], T, c['glyph_role'], c['char_role'],
                                        c['anchors'], **kw)
    return {'total': float(total), **comp}


def main():
    R.CTX_ROOTS = None
    out = []
    for m in ('M1', 'M7'):
        for p in R.PLAINS:
            for lv in R.LEVELS:
                r = f'{m}:{p}:{lv}'
                c = R.build_ctx(m, p, lv)
                T = m7_T(r) if m == 'M7' else None
                key = c['key']
                roles = {g: c['glyph_role'].get(g, '?') for g in c['VOCAB']}
                role_ok = float(np.mean([roles[g] == c['char_role'][key[g]] for g in c['VOCAB']
                                         if roles[g] in 'CV']))
                row = {'run': r, 'T': T, 'key': score(r, c, key, T), 'found': score(r, c, found_mapping(r), T),
                       'key_role_agreement': role_ok, 'glyph_roles': dict(__import__('collections').Counter(roles.values()))}
                row['key_beats_found'] = row['key']['total'] > row['found']['total']
                out.append(row)
                k, f = row['key'], row['found']
                print(f"{r:20s} key={k['total']:+9.3f} found={f['total']:+9.3f} "
                      f"{'SEARCH' if row['key_beats_found'] else 'OBJECTIVE'} failure | "
                      + ' '.join(f"{x}:{k[x]:+.2f}/{f[x]:+.2f}" for x in k if x != 'total')
                      + f" | roles-consistent-with-key {role_ok:.0%} {row['glyph_roles']}", flush=True)
    (R.HERE / 'results' / 'diag_objective.json').write_text(json.dumps(out, indent=1, ensure_ascii=False),
                                                            encoding='utf-8')


if __name__ == '__main__':
    main()

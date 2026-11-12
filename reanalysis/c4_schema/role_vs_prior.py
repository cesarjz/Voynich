"""C4c: the C3 role grammar vs Stolfi's and Zattera's models (and positional / five-slot / glyph bigram),
same domain and surrogates as prior_models.py (ZL EVA -> Zattera Slot alphabet, 26 units).

Roles are re-derived on Slot units with the nb 76 rules (role_transition_null.assign_roles) inside each
training fold. Probabilistic word models (bits include a length model P(L) where needed):
  positional  P(L) * prod P(u | pos, L)
  five-slot   P(L) * prod P(u | slot)
  roles       P(L) * prod P(role_i | role_{i-1}, pos, L) * P(u | role_i, pos, L)      (C3 model 'R')
  bigram      Witten-Bell glyph bigram with BOS/EOS (interpolated with unigram)
  Stolfi      P(word | NormalWord) from word.grx (probabilities fitted on the full text: in-sample)
  Zattera     REG acceptor (binary score)
Measures (random 10-fold, pooled):
  AUC real held-out words vs each surrogate type (positional, shuffled-in-word, unigram)
  matched-coverage specificity: threshold each probabilistic model so that it accepts 94.6 % of the
  TRAINING words (Stolfi-normal's coverage); report acceptance of real held-out words and surrogates
  held-out bits per word (on words Stolfi accepts, so that Stolfi is finite)

Usage: python role_vs_prior.py external/v4j/word.grx  -> results/role_vs_prior.json
"""
import json
import math
import sys
from collections import Counter, defaultdict

import numpy as np

from prior_models import HERE, Stolfi, load_grammar, load_eva, eva_to_slot, slot_to_eva, zattera, surrogates
from slot_schema import slot_of, auc

sys.path.insert(0, str(HERE.parent / 'c3_baselines'))
from role_transition_null import assign_roles  # noqa: E402

TARGET_COVERAGE = 0.946
ALPHA = 0.1


def fit(train, V):
    roles = assign_roles(train)
    lens = Counter(len(w) for w in train)
    nL = sum(lens.values())
    pos, slot_c, rtr, emit, big = (defaultdict(Counter) for _ in range(5))
    uni = Counter()
    rset = set(roles.values()) | {'?'}
    role_units = defaultdict(set)
    for u in V:
        role_units[roles.get(u, '?')].add(u)
    for w in train:
        L = len(w)
        pr, pg = '<w>', '<w>'
        for i, u in enumerate(w):
            c = (min(i, 7), min(L, 8))
            r = roles.get(u, '?')
            pos[c][u] += 1
            slot_c[slot_of(i, L)][u] += 1
            rtr[(pr,) + c][r] += 1
            emit[(r,) + c][u] += 1
            big[pg][u] += 1
            uni[u] += 1
            pr, pg = r, u
        big[pg]['</w>'] += 1
        uni['</w>'] += 1
    nV, nR, n_uni = len(V) + 1, len(rset), sum(uni.values())

    def p(cnt, x, k):
        return (cnt[x] + ALPHA) / (sum(cnt.values()) + ALPHA * k)

    def score(w):
        L = len(w)
        lp_len = math.log2((lens.get(L, 0) + ALPHA) / (nL + ALPHA * 20))
        out = {'positional': lp_len, 'five_slot': lp_len, 'roles': lp_len, 'bigram': 0.0}
        pr, pg = '<w>', '<w>'
        for i, u in enumerate(list(w) + ['</w>']):
            if u != '</w>':
                c = (min(i, 7), min(L, 8))
                r = roles.get(u, '?')
                out['positional'] += math.log2(p(pos[c], u, nV))
                out['five_slot'] += math.log2(p(slot_c[slot_of(i, L)], u, nV))
                out['roles'] += math.log2(p(rtr[(pr,) + c], r, nR)) + \
                    math.log2(p(emit[(r,) + c], u, max(1, len(role_units[r]))))
                pr = r
            h = big[pg]
            pu = (uni[u] + ALPHA) / (n_uni + ALPHA * nV)
            pb = (h[u] + len(h) * pu) / (sum(h.values()) + len(h)) if h else pu
            out['bigram'] += math.log2(pb)
            pg = u
        return out
    return score, roles


if __name__ == '__main__':
    gram = Stolfi(load_grammar(sys.argv[1]))

    def stolfi_lp(w):
        pw = gram.p('NormalWord', slot_to_eva(''.join(w)))
        return math.log2(pw) if pw > 0 else -math.inf

    recs = [r for r in load_eva() if r['eva']]
    words = [list(s) for s in (eva_to_slot(r['eva']) for r in recs) if s]
    V = sorted({u for w in words for u in w})
    rng = np.random.default_rng(42)
    folds = rng.permutation(len(words)) % 10
    PROB = ['positional', 'five_slot', 'roles', 'bigram', 'stolfi']
    ALL = PROB + ['zattera_REG']
    pooled_scores = {c: defaultdict(list) for c in ('real', 'positional', 'shuffled', 'unigram')}
    accept = {c: Counter() for c in pooled_scores}
    n_cond = Counter()
    bits_tot, bits_n = Counter(), 0
    roles_fold0 = None

    def all_scores(w, score):
        s = score(w)
        s['stolfi'] = stolfi_lp(w)
        s['zattera_REG'] = 1.0 if zattera(''.join(w)) == 'REGULAR' else 0.0
        return s

    for k in range(10):
        train = [w for w, f in zip(words, folds) if f != k]
        test = [w for w, f in zip(words, folds) if f == k]
        score, roles = fit(train, V)
        if k == 0:
            roles_fold0 = roles
        # matched-coverage thresholds from (a sample of) the training words
        sample = [train[i] for i in rng.choice(len(train), size=min(5000, len(train)), replace=False)]
        tr_scores = [all_scores(w, score) for w in sample]
        thr = {}
        for m in PROB:
            v = np.array([s[m] for s in tr_scores])
            fin = v[np.isfinite(v)]
            # a model whose own coverage is below the target (Stolfi) accepts every finite score
            thr[m] = (np.quantile(fin, 1 - TARGET_COVERAGE * len(v) / len(fin))
                      if len(fin) / len(v) > TARGET_COVERAGE else -np.inf)
        thr_inclusive = {m: thr[m] == -np.inf for m in PROB}
        conds = {'real': test, **{n: [w for w in ws if w] for n, ws in surrogates(train, test, rng).items()}}
        for cname, ws in conds.items():
            for w in ws:
                s = all_scores(w, score)
                for m in ALL:
                    pooled_scores[cname][m].append(s[m])
                for m in PROB:
                    accept[cname][m] += (s[m] > -np.inf) if thr_inclusive[m] else (s[m] >= thr[m])
                accept[cname]['zattera_REG'] += s['zattera_REG'] > 0
                n_cond[cname] += 1
                if cname == 'real' and s['stolfi'] > -math.inf:
                    for m in PROB:
                        bits_tot[m] -= s[m]
                    bits_n += 1
        print(f'  fold {k} done', flush=True)

    res = {'n_words': len(words), 'target_coverage': TARGET_COVERAGE, 'roles_fold0': roles_fold0,
           'role_counts_fold0': dict(Counter(roles_fold0.values())),
           'acceptance_matched_coverage': {c: {m: accept[c][m] / n_cond[c] for m in ALL} for c in accept},
           'auc_real_vs': {}, 'bits_per_word_on_stolfi_accepted': {m: bits_tot[m] / bits_n for m in PROB},
           'n_stolfi_accepted_real': bits_n}
    for sname in ('positional', 'shuffled', 'unigram'):
        res['auc_real_vs'][sname] = {}
        for m in ALL:
            a = np.array(pooled_scores['real'][m], dtype=float)
            b = np.array(pooled_scores[sname][m], dtype=float)
            fin = np.concatenate([a, b])
            lo = np.nanmin(fin[np.isfinite(fin)]) - 1 if np.isfinite(fin).any() else 0
            res['auc_real_vs'][sname][m] = auc(np.where(np.isfinite(a), a, lo), np.where(np.isfinite(b), b, lo))

    print(f"\nroles on Slot units (fold 0): {res['role_counts_fold0']}")
    print(f"{'model':12s} | accept @cov {TARGET_COVERAGE}: real  posit  shuf  unig | AUC vs posit  shuf  unig | bits/word")
    for m in ALL:
        a = res['acceptance_matched_coverage']
        au = res['auc_real_vs']
        bw = res['bits_per_word_on_stolfi_accepted'].get(m)
        print(f"{m:12s} | {a['real'][m]:.3f} {a['positional'][m]:.3f} {a['shuffled'][m]:.3f} {a['unigram'][m]:.3f} | "
              f"{au['positional'][m]:.3f} {au['shuffled'][m]:.3f} {au['unigram'][m]:.3f} | "
              f"{'' if bw is None else f'{bw:.2f}'}")
    (HERE / 'results' / 'role_vs_prior.json').write_text(json.dumps(res, indent=1, ensure_ascii=False),
                                                         encoding='utf-8')

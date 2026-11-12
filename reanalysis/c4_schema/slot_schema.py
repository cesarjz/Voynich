"""C4: coverage, exceptions and out-of-sample prediction of the five-slot schema.

nb 77 builds glyph inventories for absolute positions p1..p6 and overlays five slots by hand
("p1 + p2 + [p3] + [p4+] + pN"); the paper places FINIS at "p5-p6"; words longer than 6 glyphs
are ignored; "closed inventories" and "~87 % of words follow the grammar" are not operationalized.
Operational definition used here (stated in the paper):
  slot(i, L): L = 1 -> DOMINIUM; i = 0 -> DOMINIUM; i = L-1 -> FINIS; i = 1 -> GENUS;
              i = 2 -> SPECIES; otherwise CORPUS (positions 4 .. L-1)
  inventory(slot) = glyphs holding >= 0.5 % of the slot's tokens in the TRAINING words
                    (the threshold of the exported voynich_structural_dictionary.json)
  a word is accepted iff every glyph is in its slot's inventory.
Also reported: the nb 77 literal reading (absolute p1..p6 inventories, positions >= 7 free).

Measures, for every split (random 10-fold; leave-one-section-out with STA1 $I; Currier A <-> B):
  coverage     acceptance of real held-out words (tokens and types), exceptions by length and slot
  specificity  acceptance of surrogate words built from the training words with held-out lengths:
               positional (glyph at i drawn from P(g | i, L)), shuffled-in-word, unigram i.i.d.
  bits/glyph   held-out cross-entropy of slot model P(g | slot), positional P(g | pos, len),
               glyph bigram (Witten-Bell, interpolated with positional)
  AUC          real held-out words vs shuffled-in-word surrogates, scored by mean log-prob per glyph
               (slot model vs bigram): can the schema tell real words from scrambled ones?

Usage: python slot_schema.py  -> results/slot_schema.json
"""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / 'reeval'))
sys.path.insert(0, str(HERE.parent / 'sections_I'))
from nbcode import VOYNICH_DIR, load_defs  # noqa: E402
from sections import META, section_of, SECTIONS_I  # noqa: E402

ns = load_defs('77_minimal_dictionary.ipynb', ['parsear_sta_con_folios'])
SLOTS = ['DOMINIUM', 'GENUS', 'SPECIES', 'CORPUS', 'FINIS']
INV_MIN = 0.005
ALPHA = 0.1
POS_CAP, LEN_CAP = 7, 8


def slot_of(i, L):
    if L == 1 or i == 0:
        return 'DOMINIUM'
    if i == L - 1:
        return 'FINIS'
    return 'GENUS' if i == 1 else 'SPECIES' if i == 2 else 'CORPUS'


def abs_of(i, L):
    return f'p{i + 1}' if i < 6 else None  # nb 77 literal: p1..p6, positions >= 7 unconstrained


def inventories(words, fn):
    cnt = defaultdict(Counter)
    for w in words:
        for i, g in enumerate(w):
            s = fn(i, len(w))
            if s:
                cnt[s][g] += 1
    return {s: {g for g, c in cc.items() if c / sum(cc.values()) >= INV_MIN} for s, cc in cnt.items()}, cnt


def first_violation(w, inv, fn):
    for i, g in enumerate(w):
        s = fn(i, len(w))
        if s and g not in inv.get(s, ()):
            return s
    return None


def lp_models(train, V):
    _, slot_cnt = inventories(train, slot_of)
    pos, big = defaultdict(Counter), defaultdict(Counter)
    for w in train:
        prev = '<w>'
        for i, g in enumerate(w):
            pos[min(i, POS_CAP), min(len(w), LEN_CAP)][g] += 1
            big[prev][g] += 1
            prev = g
    nV = len(V)

    def score(w):
        """log2-probs per glyph under slot / positional / bigram models."""
        out = {'slot': 0.0, 'pos': 0.0, 'bigram': 0.0}
        prev = '<w>'
        for i, g in enumerate(w):
            sc = slot_cnt[slot_of(i, len(w))]
            ps = (sc[g] + ALPHA) / (sum(sc.values()) + ALPHA * nV)
            pc = pos[min(i, POS_CAP), min(len(w), LEN_CAP)]
            pa = (pc[g] + ALPHA) / (sum(pc.values()) + ALPHA * nV)
            h = big[prev]
            pb = (h[g] + len(h) * pa) / (sum(h.values()) + len(h)) if h else pa
            out['slot'] += math.log2(ps)
            out['pos'] += math.log2(pa)
            out['bigram'] += math.log2(pb)
            prev = g
        return out
    return score


def surrogates(train, test, rng):
    pools = defaultdict(list)
    for w in train:
        for i, g in enumerate(w):
            pools[len(w), i].append(g)
    flat = [g for w in train for g in w]
    posit = []
    for w in test:
        L = len(w)
        if all((L, i) in pools for i in range(L)):
            posit.append([pools[L, i][rng.integers(len(pools[L, i]))] for i in range(L)])
        else:  # length unseen in training: fall back to the capped length
            posit.append([flat[rng.integers(len(flat))] for _ in range(L)])
    shuf = [list(rng.permutation(w)) for w in test]
    unig = [[flat[rng.integers(len(flat))] for _ in range(len(w))] for w in test]
    return {'positional': posit, 'shuffled': shuf, 'unigram': unig}


def auc(pos_scores, neg_scores):
    s = np.concatenate([pos_scores, neg_scores])
    ranks = s.argsort().argsort() + 1.0
    n1, n0 = len(pos_scores), len(neg_scores)
    return float((ranks[:n1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def evaluate(train, test, V, rng):
    inv, _ = inventories(train, slot_of)
    inv_abs, _ = inventories(train, abs_of)
    acc = lambda ws, iv, fn: float(np.mean([first_violation(w, iv, fn) is None for w in ws]))  # noqa: E731
    sur = surrogates(train, test, rng)
    score = lp_models(train, V)
    real_scores = [score(w) for w in test]
    shuf_scores = [score(w) for w in sur['shuffled'] if w]
    n_glyphs = sum(len(w) for w in test)
    viol = Counter(first_violation(w, inv, slot_of) for w in test)
    by_len = defaultdict(lambda: [0, 0])
    for w in test:
        b = min(len(w), 8)
        by_len[b][0] += first_violation(w, inv, slot_of) is None
        by_len[b][1] += 1
    test_types = sorted({tuple(w) for w in test})
    return {
        'n_test_words': len(test),
        'inventory_sizes': {s: len(inv.get(s, ())) for s in SLOTS},
        'accept_real_tokens': acc(test, inv, slot_of),
        'accept_real_types': acc([list(t) for t in test_types], inv, slot_of),
        'accept_real_nb77_literal': acc(test, inv_abs, abs_of),
        'accept_surrogate': {k: acc(v, inv, slot_of) for k, v in sur.items()},
        'first_violation_slot': {str(k): v / len(test) for k, v in viol.items() if k},
        'accept_by_length': {str(k): v[0] / v[1] for k, v in sorted(by_len.items())},
        'n_by_length': {str(k): v[1] for k, v in sorted(by_len.items())},
        'bits_per_glyph': {m: -sum(s[m] for s in real_scores) / n_glyphs for m in ('slot', 'pos', 'bigram')},
        'auc_real_vs_shuffled': {m: auc(np.array([s[m] / len(w) for s, w in zip(real_scores, test)]),
                                        np.array([s[m] / len(w) for s, w in zip(shuf_scores,
                                                                                [w for w in sur['shuffled'] if w])]))
                                 for m in ('slot', 'pos', 'bigram')},
    }


def pooled(results):
    """Word-weighted mean of every numeric leaf over folds."""
    W = sum(r['n_test_words'] for r in results)

    def rec(key_path):
        vals = []
        for r in results:
            x = r
            for k in key_path:
                x = x.get(k) if isinstance(x, dict) else None
            vals.append(x)
        if all(isinstance(v, (int, float)) for v in vals):
            return sum(v * r['n_test_words'] for v, r in zip(vals, results)) / W
        return None
    out = {}
    for k in ('accept_real_tokens', 'accept_real_types', 'accept_real_nb77_literal'):
        out[k] = rec([k])
    for grp in ('accept_surrogate', 'bits_per_glyph', 'auc_real_vs_shuffled'):
        out[grp] = {k: rec([grp, k]) for k in results[0][grp]}
    return out


def load():
    recs = ns['parsear_sta_con_folios'](str(VOYNICH_DIR / 'corpus' / 'voynich_sta.txt'))
    for r in recs:
        r['section'] = section_of(r['folio'])
        page = r['folio']
        r['currier'] = META.get(page, {}).get('L', '?')
    return recs


def line(name, r):
    s = r['accept_surrogate']
    b, a = r['bits_per_glyph'], r['auc_real_vs_shuffled']
    return (f"{name:28s} accept real {r['accept_real_tokens']:.3f} (types {r['accept_real_types']:.3f}, "
            f"nb77-literal {r['accept_real_nb77_literal']:.3f}) | surrogates pos {s['positional']:.3f} "
            f"shuf {s['shuffled']:.3f} unig {s['unigram']:.3f} | bits slot {b['slot']:.3f} pos {b['pos']:.3f} "
            f"bigram {b['bigram']:.3f} | AUC slot {a['slot']:.3f} pos {a['pos']:.3f} bigram {a['bigram']:.3f}")


if __name__ == '__main__':
    recs = load()
    words = [r['glyphs'] for r in recs]
    V = sorted({g for w in words for g in w})
    rng = np.random.default_rng(42)
    res = {'n_words': len(words), 'definition': 'see module docstring', 'splits': {}}

    folds = rng.permutation(len(words)) % 10
    rs = [evaluate([w for w, f in zip(words, folds) if f != k], [w for w, f in zip(words, folds) if f == k], V, rng)
          for k in range(10)]
    res['splits']['random_10fold'] = {'pooled': pooled(rs), 'folds': rs}
    print(line('random 10-fold', res['splits']['random_10fold']['pooled']), flush=True)
    f0 = rs[0]
    print(f"  inventory sizes (fold 0): {f0['inventory_sizes']}")
    print(f"  acceptance by length (fold 0): " +
          ' '.join(f"L{k}={v:.2f}(n={f0['n_by_length'][k]})" for k, v in f0['accept_by_length'].items()))
    print(f"  first violating slot (fold 0, share of words): " +
          ' '.join(f'{k}={v:.3f}' for k, v in sorted(f0['first_violation_slot'].items())), flush=True)

    loso = {}
    for sec in SECTIONS_I:
        tr = [r['glyphs'] for r in recs if r['section'] != sec]
        te = [r['glyphs'] for r in recs if r['section'] == sec]
        if len(te) < 200:
            continue
        loso[sec] = evaluate(tr, te, V, rng)
        print(line(f'  held-out section {sec}', loso[sec]), flush=True)
    res['splits']['leave_one_section_out'] = {'pooled': pooled(list(loso.values())), 'sections': loso}
    print(line('leave-one-section-out', res['splits']['leave_one_section_out']['pooled']), flush=True)

    cur = {}
    for a, b in (('A', 'B'), ('B', 'A')):
        cur[f'{a}->{b}'] = evaluate([r['glyphs'] for r in recs if r['currier'] == a],
                                    [r['glyphs'] for r in recs if r['currier'] == b], V, rng)
        print(line(f'Currier {a} -> {b}', cur[f'{a}->{b}']), flush=True)
    res['splits']['currier'] = cur

    (HERE / 'results').mkdir(exist_ok=True)
    (HERE / 'results' / 'slot_schema.json').write_text(json.dumps(res, indent=1, ensure_ascii=False),
                                                       encoding='utf-8')

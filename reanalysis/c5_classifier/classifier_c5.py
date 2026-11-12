"""C5: what the section classifier demonstrates.

Unit: STA1 page/locus (226 pages with text; foldout panels separate). Labels: shared $I section
function (sections_I/sections.py; text-only pages take their quire's majority illustration type).
Classifier: nb 76 cell 4 rule — leave-one-out nearest section centroid, cosine similarity, centroid
computed without the test page. Feature sets:
  glyphs34   relative frequencies of the 34 core glyphs (>= 100 tokens; label-free) — what nb 76 uses
  roles6     proportions of the six roles among core-glyph tokens — what the paper text claims;
             roles re-derived with the nb 76 rules from the training pages only (per left-out page)
             and, for comparison, from the whole corpus
Uncertainty: page bootstrap 95 % CI (B_BOOT) for accuracy and balanced accuracy; label-permutation
null (B_PERM) for both.
Confounds (STA1 $L Currier language, $H hand):
  * the same features predicting Currier language and hand
  * section predicted from (language, hand) alone: LOO majority section of the other pages with the
    same (L, H) — how much section information the scribal variables already carry
  * section classification within Currier A pages and within Currier B pages

Usage: python classifier_c5.py  -> results/classifier_c5.json
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / 'reeval'))
sys.path.insert(0, str(HERE.parent / 'sections_I'))
sys.path.insert(0, str(HERE.parent / 'c3_baselines'))
from nbcode import VOYNICH_DIR, load_defs  # noqa: E402
from sections import META, PAGE_SECTION  # noqa: E402
from role_transition_null import assign_roles  # noqa: E402

ns = load_defs('77_minimal_dictionary.ipynb', ['parsear_sta_con_folios'])
ROLES6 = ['OPENER', 'ENCODER', 'CLOSER', 'BODY', 'SCAFFOLD', 'MIXED']
B_BOOT, B_PERM = 2000, 1000


def load_pages():
    recs = ns['parsear_sta_con_folios'](str(VOYNICH_DIR / 'corpus' / 'voynich_sta.txt'))
    pages = defaultdict(list)
    for r in recs:
        pages[r['folio']].append(r['glyphs'])
    return dict(pages)


def loo_centroid(X, y):
    """Predictions of the nb 76 rule; X rows are feature vectors, y integer labels."""
    k = y.max() + 1
    S = np.zeros((k, X.shape[1]))
    n = np.zeros(k)
    for c in range(k):
        S[c] = X[y == c].sum(0)
        n[c] = (y == c).sum()
    pred = np.empty(len(y), dtype=int)
    for i in range(len(y)):
        cent = S.copy()
        cnt = n.copy()
        cent[y[i]] -= X[i]
        cnt[y[i]] -= 1
        cent = cent / np.where(cnt[:, None] > 0, cnt[:, None], 1)
        valid = cnt > 0
        sim = cent @ X[i] / (np.linalg.norm(cent, axis=1) * np.linalg.norm(X[i]) + 1e-12)
        sim[~valid] = -np.inf
        pred[i] = int(np.argmax(sim))
    return pred


def scores(y, pred):
    acc = float((y == pred).mean())
    bal = float(np.mean([(pred[y == c] == c).mean() for c in np.unique(y)]))
    return acc, bal


def evaluate(X, y, rng):
    pred = loo_centroid(X, y)
    acc, bal = scores(y, pred)
    boot = np.array([scores(y[idx], pred[idx]) for idx in (rng.integers(len(y), size=len(y)) for _ in range(B_BOOT))])
    perm = np.array([scores(yp, loo_centroid(X, yp)) for yp in (rng.permutation(y) for _ in range(B_PERM))])
    return {'accuracy': acc, 'balanced_accuracy': bal,
            'acc_ci': np.quantile(boot[:, 0], [.025, .975]).tolist(),
            'bal_ci': np.quantile(boot[:, 1], [.025, .975]).tolist(),
            'majority': float(Counter(y).most_common(1)[0][1] / len(y)), 'chance_balanced': 1 / len(set(y)),
            'perm_acc_mean': float(perm[:, 0].mean()), 'perm_bal_mean': float(perm[:, 1].mean()),
            'p_acc': float((1 + (perm[:, 0] >= acc).sum()) / (B_PERM + 1)),
            'p_bal': float((1 + (perm[:, 1] >= bal).sum()) / (B_PERM + 1)), 'pred': pred.tolist()}


def glyph_features(pages, names, core):
    ix = {g: j for j, g in enumerate(core)}
    X = np.zeros((len(names), len(core)))
    for i, p in enumerate(names):
        for w in pages[p]:
            for g in w:
                if g in ix:
                    X[i, ix[g]] += 1
    return X / np.maximum(X.sum(1, keepdims=True), 1)


def role_features(pages, names, roles):
    ix = {r: j for j, r in enumerate(ROLES6)}
    X = np.zeros((len(names), len(ROLES6)))
    for i, p in enumerate(names):
        for w in pages[p]:
            for g in w:
                r = roles.get(g)
                if r in ix:
                    X[i, ix[r]] += 1
    return X / np.maximum(X.sum(1, keepdims=True), 1)


def roles6_fold_derived(pages, names, y):
    """LOO with roles re-derived from the training pages each time (no information from the test page)."""
    X_all = None
    pred = np.empty(len(names), dtype=int)
    for i in range(len(names)):
        train_words = [w for j, p in enumerate(names) if j != i for w in pages[p]]
        roles = assign_roles(train_words)
        X = role_features(pages, names, roles)
        # nb 76 rule for page i only
        k = y.max() + 1
        cent = np.array([X[(y == c) & (np.arange(len(y)) != i)].mean(0) if ((y == c) & (np.arange(len(y)) != i)).any()
                         else np.full(X.shape[1], np.nan) for c in range(k)])
        sim = cent @ X[i] / (np.linalg.norm(cent, axis=1) * np.linalg.norm(X[i]) + 1e-12)
        sim[np.isnan(sim)] = -np.inf
        pred[i] = int(np.argmax(sim))
        X_all = X
    return pred


def encode(labels):
    cats = sorted(set(labels))
    return np.array([cats.index(x) for x in labels]), cats


def line(name, r):
    return (f"{name:42s} acc {r['accuracy']:.3f} [{r['acc_ci'][0]:.3f},{r['acc_ci'][1]:.3f}] "
            f"(majority {r['majority']:.3f}, perm {r['perm_acc_mean']:.3f}, p {r['p_acc']:.4f}) | "
            f"bal {r['balanced_accuracy']:.3f} [{r['bal_ci'][0]:.3f},{r['bal_ci'][1]:.3f}] "
            f"(chance {r['chance_balanced']:.3f}, perm {r['perm_bal_mean']:.3f}, p {r['p_bal']:.4f})")


if __name__ == '__main__':
    rng = np.random.default_rng(42)
    pages = load_pages()
    names = sorted(p for p in pages if PAGE_SECTION.get(p, 'unknown') != 'unknown')
    sec = [PAGE_SECTION[p] for p in names]
    lang = [META.get(p, {}).get('L', '?') for p in names]
    hand = [META.get(p, {}).get('H', '?') for p in names]
    y, cats = encode(sec)
    all_words = [w for p in names for w in pages[p]]
    core = sorted(g for g, c in Counter(g for w in all_words for g in w).items() if c >= 100)
    X34 = glyph_features(pages, names, core)
    roles_global = assign_roles(all_words)
    X6 = role_features(pages, names, roles_global)
    print(f'pages {len(names)}, sections {dict(Counter(sec))}, core glyphs {len(core)}')
    print(f'Currier {dict(Counter(lang))}, hands {dict(Counter(hand))}', flush=True)

    res = {'n_pages': len(names), 'sections': cats, 'section_counts': dict(Counter(sec)),
           'currier_counts': dict(Counter(lang)), 'hand_counts': dict(Counter(hand)), 'tasks': {}}

    def run(name, X, labels, mask=None):
        m = np.ones(len(names), bool) if mask is None else np.asarray(mask)
        yy, cc = encode([l for l, k in zip(labels, m) if k])
        r = evaluate(X[m], yy, rng)
        r['classes'] = cc
        res['tasks'][name] = r
        print(line(name, r), flush=True)
        return r

    run('section | glyphs34', X34, sec)
    run('section | roles6 (global roles)', X6, sec)
    pred_fd = roles6_fold_derived(pages, names, y)
    acc, bal = scores(y, pred_fd)
    res['tasks']['section | roles6 (fold-derived roles)'] = {'accuracy': acc, 'balanced_accuracy': bal}
    print(f"{'section | roles6 (fold-derived roles)':42s} acc {acc:.3f} | bal {bal:.3f}", flush=True)

    known_L = [l in ('A', 'B') for l in lang]
    run('Currier language | glyphs34', X34, lang, known_L)
    run('Currier language | roles6', X6, lang, known_L)
    known_H = [h != '?' for h in hand]
    run('hand | glyphs34', X34, hand, known_H)
    run('hand | roles6', X6, hand, known_H)

    # section from (language, hand) alone: LOO majority
    key = list(zip(lang, hand))
    pred = []
    for i in range(len(names)):
        c = Counter(sec[j] for j in range(len(names)) if j != i and key[j] == key[i])
        pred.append(c.most_common(1)[0][0] if c else Counter(sec).most_common(1)[0][0])
    yp = np.array([cats.index(p) for p in pred])
    acc, bal = scores(y, yp)
    res['tasks']['section | (language, hand) LOO majority'] = {'accuracy': acc, 'balanced_accuracy': bal}
    print(f"{'section | (language, hand) LOO majority':42s} acc {acc:.3f} | bal {bal:.3f}", flush=True)

    for L in ('A', 'B'):
        m = [l == L for l in lang]
        if len(set(s for s, k in zip(sec, m) if k)) > 1:
            run(f'section within Currier {L} | glyphs34', X34, sec, m)
            run(f'section within Currier {L} | roles6', X6, sec, m)

    for t in res['tasks'].values():
        t.pop('pred', None)
    res['roles_global'] = roles_global
    (HERE / 'results' / 'classifier_c5.json').write_text(json.dumps(res, indent=1), encoding='utf-8')

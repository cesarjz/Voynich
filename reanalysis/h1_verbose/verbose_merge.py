"""Hypothesis 1 (verbose script: one plaintext letter = a group of glyphs) — merge test.

Prediction: if Voynich glyph groups stand for letters, merging the most frequent adjacent glyph
pairs inside words (BPE) should move the stream toward natural-language letter statistics:
conditional redundancy H1/H0 up, effective alphabet up to ~20-30, word length down to natural
letter counts. Natural plain text should instead be pushed away (merging letters into syllables).

Calibration on known truth:
  positive controls  Torah / Moreh enciphered verbosely (each letter -> a 1-3 glyph string over an
                     18-glyph alphabet; 'fixed' = one string per letter, 'homoph' = two strings per
                     letter chosen at random). True group boundaries are known -> boundary F1.
  negative controls  plain natural texts; Voynich STA1 with glyphs shuffled inside each word.

Measures at each merge checkpoint (merges learned on 90 % of words, applied to the held-out 10 %):
  H0      plug-in unigram entropy of units (train), bits
  H1      held-out cross-entropy, interpolated Witten-Bell bigram over units with word boundaries
  R       H1/H0 (conditional redundancy; scale-free across alphabet sizes)
  eff     2^H0 (effective alphabet)
  len     mean units per word
  bF1     (synthetic only) F1 of word-internal unit boundaries vs the true code boundaries

Usage: python verbose_merge.py  -> results/verbose_merge.json
"""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / 'reeval'))
sys.path.insert(0, str(HERE.parent / 'c3_baselines'))
import corpora as C  # noqa: E402
from utilization_null import voynich, N_WORDS  # noqa: E402  (nb 36 STA1 parse, 37,087 words)

CHECKPOINTS = [0, 5, 10, 20, 30, 40, 60, 80, 100, 150, 200, 300]
N_GLYPHS_SYN = 18
BOS, EOS = '<w>', '</w>'


# ---------------------------------------------------------------- synthetic verbose cipher
def slot_cipher(words, seed=42):
    """Structured verbose cipher: codes are built from slot inventories (slot 1, 2, 3 each a small
    glyph set, Voynich-like ordering) and each letter has initial / medial / final forms."""
    rng = np.random.default_rng(seed)
    glyphs = [f'g{i:02d}' for i in range(N_GLYPHS_SYN)]
    slots = [glyphs[0:6], glyphs[6:12], glyphs[12:18]]
    letters = [c for c, _ in Counter(c for w in words for c in w).most_common()]
    code = {}
    for pos in ('i', 'm', 'f'):
        used = set()
        for rank, c in enumerate(letters):
            length = 1 if rank < 4 else 2 if rank < 16 else 3
            first = 3 - length  # short codes use the later slots (like word-final glyph groups)
            while True:
                s = tuple(rng.choice(slots[first + j]) for j in range(length))
                if s not in used:
                    used.add(s)
                    code[c, pos] = s
                    break
    out, bounds = [], []
    for w in words:
        gw, b, p = [], set(), 0
        for j, c in enumerate(w):
            s = code[c, 'i' if j == 0 else 'f' if j == len(w) - 1 else 'm']
            gw += s
            p += len(s)
            b.add(p)
        b.discard(p)
        out.append(gw)
        bounds.append(b)
    return out, bounds


def verbose_cipher(words, mode, seed=42):
    """Return (glyph words, true boundary sets). Frequent letters get shorter codes."""
    if mode == 'slot':
        return slot_cipher(words, seed)
    rng = np.random.default_rng(seed)
    glyphs = [f'g{i:02d}' for i in range(N_GLYPHS_SYN)]
    letters = [c for c, _ in Counter(c for w in words for c in w).most_common()]
    n_alt = 2 if mode == 'homoph' else 1
    used, code = set(), {}
    for rank, c in enumerate(letters):
        length = 1 if rank < 6 else 2 if rank < 16 else 3
        alts = []
        while len(alts) < n_alt:
            s = tuple(rng.choice(glyphs, size=length))
            if s not in used:  # every code string is unique (decodable as a set, not prefix-free)
                used.add(s)
                alts.append(s)
        code[c] = alts
    out, bounds = [], []
    for w in words:
        gw, b, pos = [], set(), 0
        for c in w:
            s = code[c][rng.integers(len(code[c]))]
            gw += s
            pos += len(s)
            b.add(pos)
        b.discard(pos)
        out.append(gw)
        bounds.append(b)
    return out, bounds


# ---------------------------------------------------------------- BPE inside words
def pair_counts(words):
    pc = Counter()
    for w in words:
        for a, b in zip(w, w[1:]):
            pc[a, b] += 1
    return pc


def apply_merge(words, pair, new):
    a, b = pair
    out = []
    for w in words:
        if len(w) < 2:
            out.append(w)
            continue
        nw, i = [], 0
        while i < len(w):
            if i + 1 < len(w) and w[i] == a and w[i + 1] == b:
                nw.append(new)
                i += 2
            else:
                nw.append(w[i])
                i += 1
        out.append(nw)
    return out


# ---------------------------------------------------------------- measures
def h0(words):
    cnt = Counter(u for w in words for u in w)
    n = sum(cnt.values())
    return -sum(c / n * math.log2(c / n) for c in cnt.values())


def heldout_h1(train, test):
    """Interpolated Witten-Bell bigram; unigram level add-one over train vocab + <unk>."""
    uni, big = Counter(), defaultdict(Counter)
    for w in train:
        seq = [BOS] + w + [EOS]
        uni.update(seq[1:])
        for a, b in zip(seq, seq[1:]):
            big[a][b] += 1
    V = len(uni) + 1
    N = sum(uni.values())
    tot, n = 0.0, 0
    for w in test:
        seq = [BOS] + w + [EOS]
        for a, b in zip(seq, seq[1:]):
            p_uni = (uni.get(b, 0) + 1) / (N + V)
            h = big.get(a)
            if h:
                c_h, t_h = sum(h.values()), len(h)
                p = (h.get(b, 0) + t_h * p_uni) / (c_h + t_h)
            else:
                p = p_uni
            tot -= math.log2(p)
            n += 1
    return tot / n


def boundary_f1(words_units, true_bounds):
    tp = fp = fn = 0
    for w, tb in zip(words_units, true_bounds):
        pos, pb = 0, set()
        for u in w[:-1]:
            pos += len(u)
            pb.add(pos)
        tp += len(pb & tb)
        fp += len(pb - tb)
        fn += len(tb - pb)
    p = tp / (tp + fp) if tp + fp else 1.0
    r = tp / (tp + fn) if tp + fn else 1.0
    return 2 * p * r / (p + r) if p + r else 0.0


def run(words, true_bounds=None, seed=42):
    """BPE on 90 % of words; every unit is a tuple of original symbols so lengths are recoverable."""
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(words))
    n_te = len(words) // 10
    te_i, tr_i = idx[:n_te], idx[n_te:]
    tr = [[(s,) for s in words[i]] for i in tr_i]
    te = [[(s,) for s in words[i]] for i in te_i]
    tb_tr = [true_bounds[i] for i in tr_i] if true_bounds else None
    rows = []
    for k in range(max(CHECKPOINTS) + 1):
        if k in CHECKPOINTS:
            H0 = h0(tr)
            H1 = heldout_h1(tr, te)
            row = {'k': k, 'types': len({u for w in tr for u in w}), 'H0': H0, 'H1': H1, 'R': H1 / H0,
                   'eff': 2 ** H0, 'len': float(np.mean([len(w) for w in tr]))}
            if tb_tr is not None:
                row['bF1'] = boundary_f1(tr, tb_tr)
            rows.append(row)
        if k == max(CHECKPOINTS):
            break
        pc = pair_counts(tr)
        if not pc:
            break
        pair = pc.most_common(1)[0][0]
        new = pair[0] + pair[1]
        tr = apply_merge(tr, pair, new)
        te = apply_merge(te, pair, new)
    return rows


def geez_consonants():
    base = lambda ch: chr(0x1200 + (ord(ch) - 0x1200) // 8 * 8) if 0x1200 <= ord(ch) <= 0x137F else ch  # noqa: E731
    return [[base(c) for c in w] for w in C.geez_clean()]


def corpora():
    rng = np.random.default_rng(7)
    torah = C.subsample(C.torah_hebrew(), N_WORDS)
    moreh = C.subsample(C.tibbonid(), N_WORDS)
    shuf = [list(rng.permutation(w)) for w in voynich]
    out = {
        'Voynich STA1': (voynich, None),
        'Voynich EVA': (C.subsample(C.voynich_eva(), N_WORDS), None),
        'Voynich STA1 shuffled-in-word': (shuf, None),
        'Torah plain': (torah, None),
        'Moreh plain': (moreh, None),
        'Judeo-Arabic plain': (C.subsample(C.judeo_arabic(), N_WORDS), None),
        "Ge'ez fidel plain": (C.subsample(C.geez_clean(), N_WORDS), None),
        "Ge'ez consonants plain": (C.subsample(geez_consonants(), N_WORDS), None),
    }
    for name, w in (('Torah', torah), ('Moreh', moreh)):
        for mode in ('fixed', 'homoph', 'slot'):
            out[f'{name} verbose-{mode}'] = verbose_cipher(w, mode)
    return out


if __name__ == '__main__':
    # optional substring filter: run only matching corpora and merge into the existing results
    only = sys.argv[1] if len(sys.argv) > 1 else None
    out_path = HERE / 'results' / 'verbose_merge.json'
    res = json.loads(out_path.read_text(encoding='utf-8')) if only and out_path.exists() else {}
    for name, (words, tb) in corpora().items():
        if only and only not in name:
            continue
        words = [list(w) for w in words if w]
        rows = run(words, tb)
        res[name] = rows
        print(f'== {name} ({len(words):,} words)', flush=True)
        for r in rows:
            extra = f"  bF1={r['bF1']:.3f}" if 'bF1' in r else ''
            print(f"  k={r['k']:3d} types={r['types']:5d} H0={r['H0']:.3f} H1={r['H1']:.3f} R={r['R']:.3f} "
                  f"eff={r['eff']:6.1f} len={r['len']:.2f}{extra}", flush=True)
    (HERE / 'results').mkdir(exist_ok=True)
    out_path.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding='utf-8')

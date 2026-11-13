"""C4b: the five-slot schema vs
Stolfi's crust-mantle-core grammar and Zattera's slot alphabet, on the same words and surrogates.

Common domain: ZL EVA words (Voynich/corpus/voynich_eva.txt), first reading of [a:b] alternatives,
words with unreadable / rare characters dropped, converted to Zattera's Slot alphabet
(ckh K, cth T, cph P, cfh F, ch C, sh S, eee B, ee E, iii U, ii J; stray c / h -> unreadable).
Units for positional models = Slot characters.

Models (sources: github.com/mzattera/v4j, SlotAlphabet.java and resources/Stolfi/word.grx):
  Zattera REG     greedy left-to-right parse into 12 ordered slots, <= 1 element per slot
                  (SlotAlphabet.internalDecompose); accepted iff fully consumed
  Zattera REG+SEP also accept words splitting into two REG parts of length > 1 (decompose)
  Stolfi normal   probabilistic CFG 'NormalWord' (crust-mantle-core, 96.4 % of tokens in his counts);
                  chart recognizer, P(word | NormalWord)
  Stolfi full     'Word' = NormalWord + AbnormalWord (his catch-all lists)
  Five-slot       our schema (slot_schema.slot_of), inventories >= 0.5 % from the training fold
Surrogates as in slot_schema (positional P(u | i, L), shuffled-in-word, unigram), built in Slot units.
Language size: number of derivations each model generates (>= distinct strings).
Probabilistic comparison on held-out words accepted by Stolfi-normal: bits per word of
  Stolfi P(w | NormalWord), positional and five-slot P(u | ...) x P(L), glyph bigram with BOS/EOS.

Usage: python prior_models.py <path/to/word.grx>  -> results/prior_models.json
"""
import json
import math
import re
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

import numpy as np

from slot_schema import HERE, VOYNICH_DIR, section_of, slot_of, inventories, first_violation, surrogates, INV_MIN

# ---------------------------------------------------------------- EVA -> Slot alphabet
SLOT_TO_EVA = {'K': 'ckh', 'T': 'cth', 'P': 'cph', 'F': 'cfh', 'C': 'ch', 'S': 'sh',
               'B': 'eee', 'E': 'ee', 'U': 'iii', 'J': 'ii'}
EVA_OK = set('qoylrkptfcshedainmg')  # Basic EVA letters that can survive the conversion


def eva_to_slot(w):
    """Zattera's fromEva for a clean word; None if it becomes unreadable."""
    if not set(w) <= EVA_OK:
        return None
    for a, b in (('ckh', 'K'), ('cfh', 'F'), ('cth', 'T'), ('cph', 'P'), ('ch', 'C'), ('sh', 'S'),
                 ('eee', 'B'), ('ee', 'E'), ('iii', 'U'), ('ii', 'J')):
        w = w.replace(a, b)
    return None if ('c' in w or 'h' in w or 'g' in w) else w


def slot_to_eva(s):
    return ''.join(SLOT_TO_EVA.get(c, c) for c in s)


def load_eva():
    words = []
    for line in (VOYNICH_DIR / 'corpus' / 'voynich_eva.txt').read_text(encoding='utf-8').splitlines():
        m = re.match(r'^<([^.>]+)\.[^>]*>\s+(.*)', line.strip())  # text loci only (2026-11-13 fix, see reeval/corpora.py)
        if not m:
            continue
        folio, txt = m.group(1), m.group(2)
        txt = re.sub(r'\{[^}]*\}', '', txt)
        txt = re.sub(r'<[^>]*>', '', txt)
        txt = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', txt)  # first reading of alternatives
        for raw in re.split(r'[.,]', txt):
            raw = raw.strip()
            if not raw:
                continue
            ok = re.fullmatch(r'[a-z]+', raw) is not None
            words.append({'folio': folio, 'eva': raw if ok else None})
    return words


# ---------------------------------------------------------------- Zattera
ZSLOTS = [['q', 's', 'd'], ['o', 'y'], ['l', 'r'], ['k', 'p', 't', 'f'], ['S', 'C'], ['K', 'P', 'T', 'F'],
          ['e', 'E', 'B'], ['s', 'd'], ['o', 'a'], ['i', 'J', 'U'], ['d', 'l', 'r', 'm', 'n'], ['y']]


def z_internal(s):
    """Greedy decomposition; returns (consumed part, remainder)."""
    part, rest = '', s
    for combos in ZSLOTS:
        for c in combos:
            if rest.startswith(c):
                part += c
                rest = rest[len(c):]
                break
        if not rest:
            break
    return part, rest


def zattera(s):
    part1, rest = z_internal(s)
    if not rest:
        return 'REGULAR'
    if len(part1) > 1 and len(rest) > 1 and not z_internal(rest)[1]:
        return 'SEPARABLE'
    return 'UNSTRUCTURED'


def zattera_language_size():
    n = 1
    for combos in ZSLOTS:
        n *= len(combos) + 1
    return n - 1  # REG words (empty excluded); greedy parsing can make some strings unreachable


# ---------------------------------------------------------------- Stolfi
def load_grammar(path):
    rules, cur = defaultdict(list), None
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        line = line.split('#')[0].rstrip()
        if not line.strip():
            continue
        m = re.match(r'^(\w+):\s*$', line)
        if m:
            cur = m.group(1)
            continue
        parts = line.split()
        if cur and len(parts) == 4:
            prob, exp = float(parts[1]), parts[3]
            syms = [] if exp == '.' else exp.split('.')
            rules[cur].append((prob, syms))
    return dict(rules)


class Stolfi:
    def __init__(self, rules):
        self.rules = rules
        # within-rule probabilities: column 2 is P(expansion | rule) already
        self.cache = {}

    def p(self, sym, s):
        key = (sym, s)
        if key in self.cache:
            return self.cache[key]
        self.cache[key] = 0.0  # guards accidental recursion
        if sym not in self.rules:          # terminal
            val = 1.0 if s == sym else 0.0
        else:
            val = sum(pr * self.pseq(tuple(syms), s) for pr, syms in self.rules[sym] if pr > 0)
        self.cache[key] = val
        return val

    def pseq(self, syms, s):
        if not syms:
            return 1.0 if s == '' else 0.0
        if len(syms) == 1:
            return self.p(syms[0], s)
        head, tail = syms[0], syms[1:]
        tot = 0.0
        for k in range(len(s) + 1):
            ph = self.p(head, s[:k])
            if ph:
                tot += ph * self.pseq(tail, s[k:])
        return tot

    def size(self, sym):
        @lru_cache(None)
        def n(x):
            if x not in self.rules:
                return 1
            return sum(math.prod(n(y) for y in syms) for pr, syms in self.rules[x] if pr > 0)
        return n(sym)


# ---------------------------------------------------------------- five-slot language size
def fiveslot_size(inv, max_len=10):
    tot = 0
    for L in range(1, max_len + 1):
        tot += math.prod(len(inv.get(slot_of(i, L), ())) for i in range(L))
    return tot


# ---------------------------------------------------------------- probabilistic models
def prob_models(train, V, alpha=0.1):
    lens = Counter(len(w) for w in train)
    nL = sum(lens.values())
    slot_cnt, pos, big = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    for w in train:
        prev = '<w>'
        for i, u in enumerate(w):
            slot_cnt[slot_of(i, len(w))][u] += 1
            pos[min(i, 7), min(len(w), 8)][u] += 1
            big[prev][u] += 1
            prev = u
        big[prev]['</w>'] += 1
    nV = len(V) + 1
    uni = Counter()
    for h in big.values():
        uni.update(h)
    n_uni = sum(uni.values())

    def bits(w):
        pl = (lens.get(len(w), 0) + alpha) / (nL + alpha * 20)
        out = {'five_slot': -math.log2(pl), 'positional': -math.log2(pl), 'bigram': 0.0}
        prev = '<w>'
        for i, u in enumerate(list(w) + ['</w>']):
            if u != '</w>':
                sc = slot_cnt[slot_of(i, len(w))]
                out['five_slot'] -= math.log2((sc[u] + alpha) / (sum(sc.values()) + alpha * nV))
                pc = pos[min(i, 7), min(len(w), 8)]
                out['positional'] -= math.log2((pc[u] + alpha) / (sum(pc.values()) + alpha * nV))
            h = big[prev]
            pu = (uni[u] + alpha) / (n_uni + alpha * nV)
            pb = (h[u] + len(h) * pu) / (sum(h.values()) + len(h)) if h else pu
            out['bigram'] -= math.log2(pb)
            prev = u
        return out
    return bits


# ---------------------------------------------------------------- main
def accept_all(slot_words, inv, st_normal, st_full):
    z = [zattera(''.join(w)) for w in slot_words]
    return {
        'zattera_REG': float(np.mean([c == 'REGULAR' for c in z])),
        'zattera_REG+SEP': float(np.mean([c != 'UNSTRUCTURED' for c in z])),
        'stolfi_normal': float(np.mean([st_normal(slot_to_eva(''.join(w))) > 0 for w in slot_words])),
        'stolfi_full': float(np.mean([st_full(slot_to_eva(''.join(w))) > 0 for w in slot_words])),
        'five_slot': float(np.mean([first_violation(w, inv, slot_of) is None for w in slot_words])),
    }


if __name__ == '__main__':
    gram = Stolfi(load_grammar(sys.argv[1]))
    st_normal = lambda e: gram.p('NormalWord', e)  # noqa: E731
    st_full = lambda e: gram.p('Word', e)  # noqa: E731

    recs = load_eva()
    n_raw = len(recs)
    for r in recs:
        r['slot'] = eva_to_slot(r['eva']) if r['eva'] else None
    recs = [r for r in recs if r['slot']]
    for r in recs:
        r['section'] = section_of(r['folio'])
    words = [list(r['slot']) for r in recs]
    V = sorted({u for w in words for u in w})
    print(f'EVA tokens {n_raw:,}; readable in Slot alphabet {len(words):,} ({len(words) / n_raw:.1%}); units {len(V)}')

    rng = np.random.default_rng(42)
    folds = rng.permutation(len(words)) % 10
    per_fold, prob_rows = [], []
    for k in range(10):
        train = [w for w, f in zip(words, folds) if f != k]
        test = [w for w, f in zip(words, folds) if f == k]
        inv, _ = inventories(train, slot_of)
        sur = surrogates(train, test, rng)
        row = {'real': accept_all(test, inv, st_normal, st_full)}
        for name, sw in sur.items():
            row[name] = accept_all([w for w in sw if w], inv, st_normal, st_full)
        row['n'] = len(test)
        row['inv_sizes'] = {s: len(v) for s, v in inv.items()}
        per_fold.append(row)
        if k == 0:
            bits = prob_models(train, V)
            acc = [w for w in test if st_normal(slot_to_eva(''.join(w))) > 0]
            tot = Counter()
            for w in acc:
                b = bits(w)
                for m, v in b.items():
                    tot[m] += v
                tot['stolfi_normal'] -= math.log2(st_normal(slot_to_eva(''.join(w))))
            n_units = sum(len(w) for w in acc)
            prob_rows = {'n_words': len(acc), 'bits_per_word': {m: v / len(acc) for m, v in tot.items()},
                         'bits_per_unit': {m: v / n_units for m, v in tot.items()}}
            five_size = fiveslot_size(inv)
        print(f'  fold {k} done', flush=True)

    models = list(per_fold[0]['real'])
    pooled = {cond: {m: sum(r[cond][m] * r['n'] for r in per_fold) / sum(r['n'] for r in per_fold) for m in models}
              for cond in ('real', 'positional', 'shuffled', 'unigram')}
    sizes = {'zattera_REG (upper bound)': zattera_language_size(),
             'stolfi_normal (derivations)': gram.size('NormalWord'),
             'stolfi_full (derivations)': gram.size('Word'),
             'five_slot (L<=10, fold 0)': five_size}
    print(f"\n{'model':16s} {'real':>6s} {'posit':>6s} {'shuf':>6s} {'unig':>6s}   language size")
    size_key = {'zattera_REG': 'zattera_REG (upper bound)', 'zattera_REG+SEP': None,
                'stolfi_normal': 'stolfi_normal (derivations)', 'stolfi_full': 'stolfi_full (derivations)',
                'five_slot': 'five_slot (L<=10, fold 0)'}
    for m in models:
        sz = sizes.get(size_key[m]) if size_key[m] else None
        print(f"{m:16s} {pooled['real'][m]:6.3f} {pooled['positional'][m]:6.3f} {pooled['shuffled'][m]:6.3f} "
              f"{pooled['unigram'][m]:6.3f}   {'' if sz is None else f'{sz:.3g}'}")
    print(f"\nheld-out words accepted by Stolfi-normal (fold 0, n={prob_rows['n_words']:,}) bits/word: " +
          ' '.join(f'{m} {v:.2f}' for m, v in prob_rows['bits_per_word'].items()))
    print(f"five-slot inventory sizes (fold 0, Slot units): {per_fold[0]['inv_sizes']}")
    out = {'n_tokens_raw': n_raw, 'n_readable': len(words), 'units': V, 'pooled_acceptance': pooled,
           'language_size': {k: float(v) for k, v in sizes.items()}, 'probabilistic_fold0': prob_rows,
           'folds': per_fold}
    (HERE / 'results' / 'prior_models.json').write_text(json.dumps(out, indent=1, ensure_ascii=False),
                                                        encoding='utf-8')

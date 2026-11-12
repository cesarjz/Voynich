"""Known-plaintext benchmark: plaintexts and enciphered corpora.

Plaintexts (37,087 words each, the size of the STA1 Voynich corpus):
  torah_holdout  Genesis + Exodus, contiguous; the LM is trained on Leviticus-Deuteronomy.
  moreh          Moreh Nevuchim (Ibn Tibbon), first words; the LM is trained on the full Torah.

Cipher levels (symbols are opaque names S000...; nothing about them leaks the key):
  L0  simple substitution, one symbol per letter (27 -> 27).
  L1  homophonic, 27 -> 166 symbols. Homophones are allotted so that the symbol
      rank-frequency curve follows the STA1 glyph curve: glyphs are taken from
      most to least frequent and each goes to the letter with the largest unmet
      share of its frequency. Each token draws a homophone with probability
      proportional to the STA1 frequency of the glyph slot it occupies.
  L2  positional homophonic: as L1, but each letter's homophones are dealt into
      initial / medial / final classes (letters with >= 3 homophones) and a token
      draws only from the class of its position in the word, mimicking STA1's
      position-locked glyph variants.
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / 'reeval'))
import corpora as C  # noqa: E402

DATA = HERE / 'data'
N_WORDS = 37087
LEVELS = ('L0', 'L1', 'L2')
PLAINS = ('torah_holdout', 'moreh')


def torah_books():
    """Torah words per book, same extraction as corpora.torah_hebrew()."""
    out = {}
    for book in C.TORAH:
        data = json.loads((C.SEFARIA / 'torah_hebrew' / f'{book}.json').read_text(encoding='utf-8'))
        words = []
        for chapter in data['text']:
            for verse in chapter:
                C._keep(C.NIKKUD.sub('', verse), words)
        out[book] = words
    return out


def plaintext_and_lm_corpus(plain):
    """Return (plaintext words, full LM training corpus) for a plaintext condition."""
    if plain == 'torah_holdout':
        books = torah_books()
        plain_words = (books['Genesis'] + books['Exodus'])[:N_WORDS]
        lm_words = books['Leviticus'] + books['Numbers'] + books['Deuteronomy']
        assert len(plain_words) == N_WORDS, len(plain_words)
        return plain_words, lm_words
    if plain == 'moreh':
        return C.tibbonid()[:N_WORDS], C.torah_hebrew()
    raise ValueError(plain)


def sta_glyph_freqs():
    sta, _ = C.voynich_sta()
    return np.array(sorted(Counter(g for w in sta for g in w).values(), reverse=True), dtype=float)


def allot_homophones(letter_freq, glyph_freq):
    """Greedy allotment of glyph slots (descending frequency) to letters.

    Returns {letter: [slot indices]}; every letter gets at least one slot.
    """
    letters = sorted(letter_freq, key=letter_freq.get, reverse=True)
    p = np.array([letter_freq[c] for c in letters], dtype=float)
    p /= p.sum()
    q = glyph_freq / glyph_freq.sum()
    assigned = np.zeros(len(letters))
    slots = {c: [] for c in letters}
    for j, qj in enumerate(q):
        empty = [i for i, c in enumerate(letters) if not slots[c]]
        if len(empty) >= len(q) - j:   # just enough slots left: one per empty letter
            i = empty[0]
        else:
            i = int(np.argmax(p - assigned))
        slots[letters[i]].append(j)
        assigned[i] += qj
    return slots


def build_key(level, letter_freq, glyph_freq, rng):
    """Return (classes, weights, symbol->letter key).

    classes[letter][pos] = list of symbols usable at pos in {0: initial, 1: medial, 2: final};
    weights[symbol] = draw weight.
    """
    letters = sorted(letter_freq)
    if level == 'L0':
        slots = {c: [i] for i, c in enumerate(sorted(letters, key=letter_freq.get, reverse=True))}
        n_sym = len(letters)
        w_slot = np.ones(n_sym)
    else:
        slots = allot_homophones(letter_freq, glyph_freq)
        n_sym = len(glyph_freq)
        w_slot = glyph_freq
    names = [f'S{i:03d}' for i in rng.permutation(n_sym)]  # opaque, shuffled names
    classes, weights, key = {}, {}, {}
    for c, js in slots.items():
        syms = [names[j] for j in js]
        for j, s in zip(js, syms):
            weights[s] = float(w_slot[j])
            key[s] = c
        if level == 'L2' and len(syms) >= 3:
            dealt = [syms[k::3] for k in range(3)]   # syms are in descending frequency
            classes[c] = {pos: dealt[pos] for pos in range(3)}
        else:
            classes[c] = {pos: syms for pos in range(3)}
    return classes, weights, key


def encipher(words, classes, weights, rng):
    out = []
    for w in words:
        enc = []
        for i, c in enumerate(w):
            pos = 0 if i == 0 else (2 if i == len(w) - 1 else 1)
            syms = classes[c][pos]
            p = np.array([weights[s] for s in syms])
            enc.append(syms[rng.choice(len(syms), p=p / p.sum())])
        out.append(enc)
    return out


def main():
    DATA.mkdir(exist_ok=True)
    glyph_freq = sta_glyph_freqs()
    print(f'STA1 glyph types: {len(glyph_freq)}')
    for plain in PLAINS:
        plain_words, lm_words = plaintext_and_lm_corpus(plain)
        letter_freq = Counter(c for w in plain_words for c in w)
        for li, level in enumerate(LEVELS):
            rng = np.random.default_rng(2026 + 10 * li + PLAINS.index(plain))
            classes, weights, key = build_key(level, letter_freq, glyph_freq, rng)
            cipher_words = encipher(plain_words, classes, weights, rng)
            used = Counter(s for w in cipher_words for s in w)
            print(f'{plain:14s} {level}: {len(cipher_words):,} words, {sum(used.values()):,} tokens, '
                  f'{len(used)} symbols used / {len(key)}')
            (DATA / f'{plain}_{level}.json').write_text(json.dumps({
                'plain': plain, 'level': level, 'cipher_words': cipher_words,
                'plain_words': plain_words, 'key': key,
            }, ensure_ascii=False), encoding='utf-8')
        (DATA / f'{plain}_lm_corpus.json').write_text(
            json.dumps(lm_words, ensure_ascii=False), encoding='utf-8')
        print(f'{plain:14s} LM corpus: {len(lm_words):,} words')


if __name__ == '__main__':
    main()

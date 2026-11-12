"""Unified trigram-realism test with a permutation null.

Statistic (unchanged from the original notebooks): Jensen-Shannon distance
(scipy, natural log) between the word-internal trigram distribution of the
decoded Voynich text and that of the target corpus, with each word padded as
<w> <w> c1 ... cn </w> and 1e-12 added to every cell before normalising.

Null (new, applied to every model): permutation of the learned mapping. The
values of each mapping table are shuffled across its keys, which preserves the
exact multiset of target units (and hence collapse and cardinality) and breaks
only *which* glyph receives *which* unit.

p-value: (1 + #{null JSD <= real JSD}) / (B + 1). Lower is better.
"""
import numpy as np
from scipy.spatial.distance import jensenshannon


class Encoder:
    """Maps target units (characters) to contiguous integer ids."""

    def __init__(self, chars):
        self.chars = sorted(set(chars))
        self.idx = {c: i for i, c in enumerate(self.chars)}
        self.BOS = len(self.chars)
        self.EOS = len(self.chars) + 1
        self.K = len(self.chars) + 2


def _trigram_codes(flat_chars, word_lens, enc):
    """Trigram codes of a corpus given as a flat char-id array + word lengths."""
    n_words = len(word_lens)
    padded_lens = word_lens + 3
    total = int(padded_lens.sum())
    seq = np.empty(total, dtype=np.int64)
    starts = np.concatenate(([0], np.cumsum(padded_lens)[:-1]))
    seq[starts] = enc.BOS
    seq[starts + 1] = enc.BOS
    seq[starts + 2 + word_lens] = enc.EOS
    body = np.ones(total, dtype=bool)
    body[starts] = body[starts + 1] = body[starts + 2 + word_lens] = False
    seq[body] = flat_chars
    # Trigram j starts at seq[j]; valid j are starts..starts+word_len for each word.
    n_tri = word_lens + 1
    first = np.repeat(starts, n_tri)
    offs = np.arange(int(n_tri.sum())) - np.repeat(np.cumsum(n_tri) - n_tri, n_tri)
    j = first + offs
    K = enc.K
    return seq[j] * K * K + seq[j + 1] * K + seq[j + 2]


def trigram_dist(flat_chars, word_lens, enc):
    codes, counts = np.unique(_trigram_codes(flat_chars, word_lens, enc), return_counts=True)
    return codes, counts / counts.sum()


def jsd(dist_a, dist_b):
    """Same computation as the notebooks' trigram_jsd, on sparse code arrays."""
    ca, pa = dist_a
    cb, pb = dist_b
    keys = np.union1d(ca, cb)
    p = np.zeros(len(keys))
    q = np.zeros(len(keys))
    p[np.searchsorted(keys, ca)] = pa
    q[np.searchsorted(keys, cb)] = pb
    p = p + 1e-12
    q = q + 1e-12
    return float(jensenshannon(p / p.sum(), q / q.sum()))


def corpus_dist(words, enc):
    """Trigram distribution of a list of words (each a sequence of chars)."""
    flat = np.array([enc.idx[c] for w in words for c in w], dtype=np.int64)
    lens = np.array([len(w) for w in words], dtype=np.int64)
    return trigram_dist(flat, lens, enc)


class DecodedCorpus:
    """Voynich corpus as key ids, decodable under any assignment key -> unit.

    keys_per_word: list of words, each a list of integer keys (glyph id, or
        table*G + glyph id for positional models).
    units: list of target units (each a tuple of chars; length 1 for
        character-level models, variable for syllable targets).
    """

    def __init__(self, keys_per_word, units, enc):
        self.flat_keys = np.array([k for w in keys_per_word for k in w], dtype=np.int64)
        self.word_of = np.repeat(np.arange(len(keys_per_word)),
                                 [len(w) for w in keys_per_word])
        self.n_words = len(keys_per_word)
        max_len = max(len(u) for u in units)
        self.unit_chars = np.full((len(units), max_len), -1, dtype=np.int64)
        for i, u in enumerate(units):
            self.unit_chars[i, :len(u)] = [enc.idx[c] for c in u]
        self.unit_len = np.array([len(u) for u in units], dtype=np.int64)
        self.enc = enc

    def decode(self, key_to_unit):
        """key_to_unit: int array, unit index for every key id."""
        u = key_to_unit[self.flat_keys]
        chars = self.unit_chars[u]
        flat = chars[chars >= 0]  # row-major, so token order is preserved
        word_lens = np.bincount(self.word_of, weights=self.unit_len[u],
                                minlength=self.n_words).astype(np.int64)
        return flat, word_lens


def permutation_test(corpus, key_to_unit, groups, ref_dist, B=1000, seed=42):
    """Real JSD, null JSDs and p-value under within-group permutation."""
    flat, lens = corpus.decode(key_to_unit)
    real = jsd(trigram_dist(flat, lens, corpus.enc), ref_dist)
    rng = np.random.default_rng(seed)
    null = np.empty(B)
    for b in range(B):
        perm = key_to_unit.copy()
        for g in groups:
            perm[g] = key_to_unit[rng.permutation(g)]
        f, l = corpus.decode(perm)
        null[b] = jsd(trigram_dist(f, l, corpus.enc), ref_dist)
    p = (1 + int(np.sum(null <= real))) / (B + 1)
    return real, null, p

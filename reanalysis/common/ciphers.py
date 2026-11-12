"""Naibbe cipher (Greshko 2025), used for the specificity control ctl_NAIB.

Re-implementation of Greshko (2025) naibbe.py (github.com/greshko/naibbe-cipher, commit 5145f52, MIT licence;
cite Greshko 2025, Cryptologia, doi 10.1080/01611194.2025.2566408) with a seeded rng instead of the global
`random`; tables read from its references/naibbe_tables.csv, fetched into reanalysis/external/naibbe-cipher/ by
fetch_external.sh. Defaults as in the repo: RESPACING=17, 52-card deck, UNAMBIGUOUS=True, no space removal.
"""
import csv
import unicodedata
from pathlib import Path

NAIBBE_DIR = Path(__file__).resolve().parents[1] / 'external' / 'naibbe-cipher'


# ---------------------------------------------------------------- Naibbe (Greshko 2025)
_NB = {}


def _naibbe_tables():
    if not _NB:
        with open(NAIBBE_DIR / 'references' / 'naibbe_tables.csv', encoding='utf-8-sig') as f:
            _NB['glyph'] = {r['code']: r['glyphs'] for r in csv.DictReader(f)}
        _NB['unigrams'] = {g for c, g in _NB['glyph'].items() if c.startswith('unigram_')}
    return _NB


NAIBBE_WEIGHTS = {'alpha': 20, 'beta1': 8, 'beta2': 8, 'beta3': 8, 'gamma1': 4, 'gamma2': 4}


def naibbe_clean(text):
    """As naibbe.clean_line: strip diacritics, keep letters, W->UU, J->I, K->C, lower case. Deviation: letters
    outside a-z (e.g. Greek in Pliny) are dropped; the original would emit the raw placeholder code for them."""
    nfd = unicodedata.normalize('NFD', text)
    s = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    rep = {'æ': 'ae', 'Æ': 'ae', 'œ': 'oe', 'Œ': 'oe', 'ð': 'd', 'Ð': 'd', 'þ': 'th', 'Þ': 'th', 'ł': 'l',
           'Ł': 'l', 'ß': 'ss', 'ø': 'o', 'Ø': 'o'}
    s = ''.join(c for c in ''.join(rep.get(c, c) for c in s) if c.isalpha()).upper()
    s = s.replace('W', 'UU').replace('J', 'I').replace('K', 'C').lower()
    return ''.join(c for c in s if 'a' <= c <= 'z')


def naibbe_line(text, rng, respacing=17):
    """Encrypt one cleaned line (no spaces) -> list of EVA-string tokens; mirrors naibbe.encrypt_naibbe."""
    nb = _naibbe_tables()
    chunks, i = [], 0
    while i < len(text):
        if i == len(text) - 1 or rng.random() < respacing / 36:
            chunks.append(text[i])
            i += 1
        else:
            chunks.append(text[i:i + 2])
            i += 2
    state = {'deck': [], 'i': 0}

    def draw():
        if state['i'] >= len(state['deck']):
            d = [t for t, c in NAIBBE_WEIGHTS.items() for _ in range(c)]
            state['deck'] = [d[j] for j in rng.permutation(len(d))]
            state['i'] = 0
        state['i'] += 1
        return state['deck'][state['i'] - 1]

    out = []
    for ch in chunks:
        if len(ch) == 1:
            out.append(nb['glyph'][f'unigram_{draw()}_{ch}'])
        else:
            while True:
                pre = nb['glyph'][f'prefix_{draw()}_{ch[0]}']
                suf = nb['glyph'][f'suffix_{draw()}_{ch[1]}']
                if pre + suf not in nb['unigrams']:
                    out.append(pre + suf)
                    break
    return out


def naibbe_lines(raw_lines, rng):
    """raw_lines: plaintext lines (strings). Returns list of lines of tokens (tuples of EVA characters).
    Note: as in the original, the card deck is reshuffled at the start of every line."""
    out = []
    for s in raw_lines:
        c = naibbe_clean(s)
        if c:
            out.append([tuple(t) for t in naibbe_line(c, rng)])
    return out

"""Natural-language control texts for the onset/coda comparison and the specificity controls.

Verbatim copy of the loaders used in the analysis (constants FULL / GUTENBERG and functions tokenize_line /
text_lines), so that the published scripts do not depend on unpublished code.

  GB   Gaskell & Bowern (2022) 'meaningful' corpus, github.com/danielgaskell/voynich (data/meaningful.zip),
       fetched into reanalysis/external/gaskell_bowern/ by fetch_external.sh (licences per meaningful_sources.txt).
  GUT  Project Gutenberg texts (public domain), frozen in corpus/gutenberg/.

Tokenisation: lower case; a word is a maximal run of Unicode letters and combining marks (categories L*, M*),
1-15 units; units are code points.
"""
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GB = ROOT / 'reanalysis' / 'external' / 'gaskell_bowern'
GUT = ROOT / 'corpus' / 'gutenberg'

FULL = {  # name -> file (Part A); only texts with >= 40k words
    'Latin Vulgate NT': 'Historical - Latin - Literary - NT (Vulgate).txt',
    'Latin Pliny NH': "Historical - Latin - Technical - Pliny's Natural History.txt",
    'Italian Diodati NT': 'Historical - Italian - Literary - NT - Diodati.txt',
    'German Luther NT': 'Historical - German - Literary - NT - Luther.txt',
    'French Martin NT': 'Historical - French - Literary - NT - Martin.txt',
    'Spanish NT': 'Historical - Spanish - Literary - NT - Sagradas Escrituras.txt',
    'English KJV NT': 'Historical - English - Literary - NT (KJV).txt',
    'Anglo-Saxon Hatton': 'Historical - Anglo-Saxon - Literary - NT - Hatton Gospels.txt',
    'Greek NT': 'Historical - Greek - Literary - NT - Textus Receptus.txt',
    'Russian Codex Marianus': 'Historical - Russian - Literary - NT - Codex Marianus.txt',
    'Sanskrit Mahabharata': 'Historical - Sanskrit - Literary - Mahabharata.txt',
    'Arabic Quran': 'Historical - Arabic - Literary - Quran.txt',
    'Arabic Avicenna': 'Historical - Arabic - Technical - Avicenna.txt',
}
GUTENBERG = {'Latin Caesar BG': ['pg218.txt', 'pg18837.txt'], 'Italian Dante': ['pg1012.txt'],
             'German Simplicissimus': ['pg55171.txt']}

def tokenize_line(s):
    out, cur = [], []
    for ch in s.lower():
        if unicodedata.category(ch)[0] in 'LM':
            cur.append(ch)
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return [tuple(w) for w in out if len(w) <= 15]


def text_lines(path):
    txt = path.read_text(encoding='utf-8', errors='replace')
    if '*** START' in txt:
        txt = txt.split('*** START', 1)[1].split('\n', 1)[1].split('*** END', 1)[0]
    return [ln for ln in (tokenize_line(s) for s in txt.splitlines()) if ln]

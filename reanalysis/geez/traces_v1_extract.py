"""Ge'ez control corpus from the TraCES v1 TEI export (doi:10.25592/uhhfdm.707, CC BY-NC-ND 4.0).

One word per <fs type="graphunit">, its <f name="fidäl"> text (the graphic unit as written),
Ethiopic syllables only (U+1200-U+137F minus punctuation/numerals, plus supplements); documents
in folder order. ND licence: the corpus cannot be redistributed, so only this script is shared.
Download the TraCES v1 export yourself and unpack it as reanalysis/external/traces/traces_v1_raw/TraCES_corpus/.

Usage: python traces_v1_extract.py
  → reanalysis/external/traces/traces_v1_words.json ({'texts': {name: [words]}, 'stats'})
"""
import json
import re
from collections import Counter
from pathlib import Path

GEEZ = Path(__file__).resolve().parents[1] / 'external' / 'traces'
RAW = GEEZ / 'traces_v1_raw' / 'TraCES_corpus'
OUT = GEEZ / 'traces_v1_words.json'
SYL = re.compile(r'[ሀ-ፚᎀ-ᎏⶀ-⷟꬀-꬯]')


GU = re.compile(r'<fs type="graphunit"[^>]*>\s*<f name="fidäl">([^<]*)</f>')


def words_of(path):
    """Regex, not an XML parser: some exported files are not well-formed."""
    out = []
    for m in GU.finditer(path.read_text(encoding='utf-8')):
        w = ''.join(SYL.findall(m.group(1)))
        if w:
            out.append(w)
    return out


def main():
    texts = {}
    for d in sorted(RAW.iterdir()):
        for x in sorted(d.rglob('TEI/*.xml')):  # some texts are split into chapter folders
            texts[f'{d.name}/{x.stem}'] = words_of(x)
    allw = [w for ws in texts.values() for w in ws]
    stats = {'texts': {k: len(v) for k, v in texts.items()}, 'words': len(allw), 'types': len(set(allw)),
             'signs': len({c for w in allw for c in w}),
             'adjacent_identical': sum(a == b for a, b in zip(allw, allw[1:])) / max(len(allw) - 1, 1),
             'mean_len': sum(map(len, allw)) / len(allw),
             'top_signs': Counter(c for w in allw for c in w).most_common(5)}
    for k, v in stats['texts'].items():
        print(f'  {k:60s} {v:7,d}')
    print({k: v for k, v in stats.items() if k != 'texts'})
    OUT.write_text(json.dumps({'texts': texts, 'stats': stats,
                               'source': 'TraCES Corpus v1, doi:10.25592/uhhfdm.707, CC BY-NC-ND 4.0'},
                              ensure_ascii=False), encoding='utf-8')
    print('written', OUT)


if __name__ == '__main__':
    main()

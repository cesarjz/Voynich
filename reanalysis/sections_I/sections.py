"""One shared page -> section function for R1: STA1 page metadata $I (illustration type).

H herbal, A astro, C cosmo, Z zodiac, B bio, P pharma, S recipe (stars).
Text-only pages ($I=T, 7 pages) take the majority illustration type of their quire ($Q).
"""
import re
from collections import Counter
from pathlib import Path

STA = Path(__file__).resolve().parents[2] / 'corpus' / 'voynich_sta.txt'
I_TO_SECTION = {'H': 'herbal', 'A': 'astro', 'C': 'cosmo', 'Z': 'zodiac', 'B': 'bio', 'P': 'pharma', 'S': 'recipe'}
SECTIONS_I = ['herbal', 'astro', 'cosmo', 'zodiac', 'bio', 'pharma', 'recipe']


def page_meta(path=STA):
    out = {}
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        m = re.match(r'^<(f\d+[rv]\d*)>\s*<!(.*)>', line.strip())
        if m:
            out[m.group(1)] = dict(re.findall(r'\$(\w)=(\w+)', m.group(2)))
    return out


def page_sections(meta):
    quire_major = {}
    for q in {m.get('Q') for m in meta.values()}:
        c = Counter(m['I'] for m in meta.values() if m.get('Q') == q and m.get('I') in I_TO_SECTION)
        quire_major[q] = c.most_common(1)[0][0] if c else None
    return {p: I_TO_SECTION.get(m.get('I')) or I_TO_SECTION.get(quire_major.get(m.get('Q')), 'unknown')
            for p, m in meta.items()}


META = page_meta()
PAGE_SECTION = page_sections(META)


def section_of(tag):
    m = re.match(r'(f\d+[rv]\d*)', str(tag))
    return PAGE_SECTION.get(m.group(1), 'unknown') if m else 'unknown'


if __name__ == '__main__':
    for p, m in META.items():
        if m.get('I') == 'T':
            print(p, 'quire', m.get('Q'), '->', PAGE_SECTION[p])
    print(Counter(PAGE_SECTION.values()))

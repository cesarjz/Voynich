"""Voynich and target-language corpora, extracted exactly as in the notebooks.

Sefaria texts: the Torah (public domain) is frozen in corpus/sefaria/; Onkelos and the Zohar are fetched
into reanalysis/external/sefaria/ by fetch_external.sh.
(the original raw.githubusercontent URLs died in September 2026).
"""
import json
import re

import numpy as np

from nbcode import VOYNICH_DIR, EXTERNAL_DIR, load_defs

SEFARIA = VOYNICH_DIR / 'corpus' / 'sefaria'
SEFARIA_EXT = EXTERNAL_DIR / 'sefaria'
TORAH = ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy']
NIKKUD = re.compile(r'[֑-ׇ]')
HEB_WORD = re.compile(r'[א-ת]+')


def _keep(text, out):
    for p in HEB_WORD.findall(text):
        if 2 <= len(p) <= 15:
            out.append(list(p))


def torah_hebrew():
    """nb 08/14 `descargar_hebreo`: 80,051 words."""
    words = []
    for book in TORAH:
        data = json.loads((SEFARIA / 'torah_hebrew' / f'{book}.json').read_text(encoding='utf-8'))
        for chapter in data['text']:
            for verse in chapter:
                _keep(NIKKUD.sub('', verse), words)
    return words


def onkelos_aramaic():
    """nb 16 `descargar_arameo`."""
    words = []
    for book in TORAH:
        data = json.loads((SEFARIA_EXT / 'onkelos_aramaic' / f'Onkelos_{book}.json').read_text(encoding='utf-8'))
        for verse in data.get('text', {}).values():
            _keep(NIKKUD.sub('', re.sub(r'<[^>]*>', '', str(verse))), words)
    return words


def zohar_nb26():
    """nb 26 `descargar_zohar` (full recursive walk): 807,843 words."""
    data = json.loads((SEFARIA_EXT / 'zohar_sulam' / 'Zohar_Sulam_1945.json').read_text(encoding='utf-8'))
    words = []

    def walk(obj):
        if isinstance(obj, str):
            t = re.sub(r'\([^)]*\)', '', re.sub(r'<[^>]*>', '', obj))
            _keep(NIKKUD.sub('', t), words)
        elif isinstance(obj, list):
            for x in obj:
                walk(x)
        elif isinstance(obj, dict):
            for x in obj.values():
                walk(x)

    walk(data['text'])
    return words


def _processed(name, key):
    data = json.loads((VOYNICH_DIR / 'corpus' / name).read_text(encoding='utf-8'))
    return [list(w) for w in data[key] if 2 <= len(w) <= 15]


def tibbonid(key='words_full'):
    return _processed('moreh_nevuchim_processed.json', key)


def judeo_arabic(key='words_full'):
    return _processed('judeo_arabic_processed.json', key)


def geez(key='words_full'):
    return _processed('geez_processed.json', key)


def subsample(words, n, seed=42):
    """Notebook subsampling: n words without replacement, original order kept."""
    if len(words) <= n:
        return list(words)
    idx = np.random.default_rng(seed).choice(len(words), size=n, replace=False)
    return [words[i] for i in sorted(idx)]


def voynich_sta():
    """STA1 words + TP-P20 syllable segmentation (nb 08/15)."""
    ns = load_defs('08_validation.ipynb', [
        'parsear_sta_completo', 'tokens_a_palabras',
        'construir_matriz_transicion_intrapalabra', 'segmentar_silabas_tp', 'syls_to_words'])
    words = ns['tokens_a_palabras'](ns['parsear_sta_completo'](str(VOYNICH_DIR / 'corpus' / 'voynich_sta.txt')))
    _, m_prob, toks, index = ns['construir_matriz_transicion_intrapalabra'](words)
    syls, _, _ = ns['segmentar_silabas_tp'](words, m_prob, toks, index, threshold_percentile=20)
    return words, ns['syls_to_words'](syls)


def voynich_eva():
    ns = load_defs('24_neural_v2_eva.ipynb', ['EVA_MULTI', 'tokenize_eva_word', 'parse_eva_ivtff'])
    words, _ = ns['parse_eva_ivtff']((VOYNICH_DIR / 'corpus' / 'voynich_eva.txt').read_text(encoding='utf-8'))
    return words


def allograph_rewrite(words, cluster_map):
    ns = load_defs('17_allograph.ipynb', ['rewrite_word'])
    return [ns['rewrite_word'](w, cluster_map) for w in words]


def geez_clean():
    """Ge'ez from the TraCES v1 TEI export (geez/traces_v1_extract.py): 113,386 graphic units,
    11 texts, no layer duplication. Use this for controls; `geez()` reproduces what the notebooks
    used (the v0.1 export with interleaved annotation layers)."""
    return [list(w) for ws in geez_texts().values() for w in ws if 2 <= len(w) <= 15]


def geez_texts():
    path = EXTERNAL_DIR / 'traces' / 'traces_v1_words.json'
    return json.loads(path.read_text(encoding='utf-8'))['texts']

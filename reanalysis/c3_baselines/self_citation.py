"""Hypothesis test: self-citation / copy-and-modify generation (Timm & Schinner 2020).

Prediction of the self-citation method: each word is a (modified) copy of a word written
shortly before, preferably in the line above. So near-identical words should cluster at short
distance on the page, beyond what the page's own vocabulary explains.

Statistic, for every token: does an exact copy / a one-edit variant (Levenshtein 1 over glyphs)
occur among the previous W tokens of the same page? Compared with a null that shuffles the
words within each page (keeps the page vocabulary, destroys order); effect = obs / null.
Also: lag profile (k = 1..40) and the 'line above' test (same position vs other positions).

Every corpus is poured into the STA1 page and line skeleton (same words per line, lines per
page), so window and line effects are measured on the same geometry:
  Voynich STA1, Voynich EVA; natural controls Torah, Moreh (Ibn Tibbon), Judeo-Arabic, Ge'ez;
  positive control: a synthetic copy-and-modify text over the STA1 glyph inventory.

Usage: python self_citation.py → results/self_citation.json
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / 'reeval'))
import corpora as C  # noqa: E402
from nbcode import VOYNICH_DIR  # noqa: E402

W = 10          # ~ one STA1 line (mean 8.6 words/line)
LAGS = 40
N_NULL = 20


def sta_lines():
    """STA1 parsed as in nb 03 `parsear_sta_completo`, keeping page and line; P = paragraph line."""
    pages = []
    for line in (VOYNICH_DIR / 'corpus' / 'voynich_sta.txt').read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or re.match(r'^<[^>]+>\s*<!', line):
            continue
        m = re.match(r'^<([^.>]+)\.[^,>]*,(.)(\w)[^>]*>\s+(.*)', line)
        if not m:
            continue
        page, _, ltype, text = m.groups()
        text = re.sub(r'-', '.', re.sub(r'<[^>]*>', '', re.sub(r'\{[^}]*\}', '', text))).strip()
        words = [tuple(re.findall(r'[A-Z][0-9a-z]', w)) for w in text.split('.') if w.strip()]
        words = [w for w in words if w]
        if not words:
            continue
        if not pages or pages[-1]['page'] != page:
            pages.append({'page': page, 'lines': [], 'para': []})
        pages[-1]['lines'].append(words)
        pages[-1]['para'].append(ltype == 'P')
    return pages


def pour(words, skeleton):
    """Fill the STA1 page/line skeleton with a word stream (truncates or cycles as needed)."""
    out, i = [], 0
    for pg in skeleton:
        lines = []
        for ln in pg['lines']:
            lines.append([tuple(words[(i + k) % len(words)]) for k in range(len(ln))])
            i += len(ln)
        out.append({'page': pg['page'], 'lines': lines, 'para': pg['para']})
    return out


def copy_modify(sta_words, n, seed=5):
    """Positive control: 85 % of words copy one of the previous 20 and apply 0-2 glyph edits."""
    rng = np.random.default_rng(seed)
    g = Counter(x for w in sta_words for x in w)
    gs, gp = list(g), np.array(list(g.values()), float) / sum(g.values())
    vocab = sorted({tuple(w) for w in sta_words})  # sorted: set order varies with PYTHONHASHSEED (fix 2026-11-11)
    out = []
    for _ in range(n):
        if len(out) < 20 or rng.random() > 0.85:
            out.append(vocab[rng.integers(len(vocab))])
            continue
        w = list(out[-rng.integers(1, 21)])
        for _ in range(rng.choice(3, p=[0.25, 0.5, 0.25])):
            op, j = rng.integers(3), rng.integers(len(w))
            new = gs[rng.choice(len(gs), p=gp)]
            if op == 0:
                w[j] = new
            elif op == 1:
                w.insert(j, new)
            elif len(w) > 1:
                del w[j]
        out.append(tuple(w))
    return out


_cache = {}


def lev(a, b):
    if a == b:
        return 0
    key = (a, b) if a < b else (b, a)
    d = _cache.get(key)
    if d is None:
        prev = list(range(len(b) + 1))
        for i, x in enumerate(a, 1):
            cur = [i]
            for j, y in enumerate(b, 1):
                cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
            prev = cur
        d = _cache[key] = prev[-1]
    return d


def page_stats(pages):
    """Exact / one-edit rates within the previous W tokens, and per-lag rates."""
    exact = near = n = 0
    lag_hits, lag_n = np.zeros(LAGS + 1), np.zeros(LAGS + 1)
    for pg in pages:
        toks = [w for ln in pg['lines'] for w in ln]
        for i, w in enumerate(toks):
            win = toks[max(0, i - W):i]
            if not win:
                continue
            n += 1
            ds = [lev(w, v) for v in win]
            exact += min(ds) == 0
            near += min(ds) == 1
            for k in range(1, min(LAGS, i) + 1):
                lag_hits[k] += lev(w, toks[i - k]) <= 1
                lag_n[k] += 1
    return {'exact': exact / n, 'near': near / n, 'lag': (lag_hits[1:] / np.maximum(lag_n[1:], 1)).tolist()}


def line_above(pages):
    """P(lev <= 1) between word j of a paragraph line and word j of the line above,
    versus words at other positions of the line above."""
    same = other = 0.0
    ns = no = 0
    for pg in pages:
        for (a, pa), (b, pb) in zip(zip(pg['lines'], pg['para']), zip(pg['lines'][1:], pg['para'][1:])):
            if not (pa and pb):
                continue
            for j, w in enumerate(b):
                for i, v in enumerate(a):
                    hit = lev(w, v) <= 1
                    if i == j:
                        same += hit
                        ns += 1
                    else:
                        other += hit
                        no += 1
    return {'same_position': same / ns, 'other_positions': other / no}


def shuffled(pages, rng):
    out = []
    for pg in pages:
        toks = [w for ln in pg['lines'] for w in ln]
        perm = [toks[i] for i in rng.permutation(len(toks))]
        lines, i = [], 0
        for ln in pg['lines']:
            lines.append(perm[i:i + len(ln)])
            i += len(ln)
        out.append({**pg, 'lines': lines})
    return out


def analyse(name, pages):
    obs = page_stats(pages)
    obs['line_above'] = line_above(pages)
    rng = np.random.default_rng(11)
    nulls = [page_stats(shuffled(pages, rng)) for _ in range(N_NULL)]
    res = {'obs': obs}
    for k in ('exact', 'near'):
        v = np.array([x[k] for x in nulls])
        res[k] = {'obs': obs[k], 'null_mean': float(v.mean()), 'null_sd': float(v.std(ddof=1)),
                  'ratio': obs[k] / v.mean(), 'z': (obs[k] - v.mean()) / v.std(ddof=1)}
    lag_null = np.mean([x['lag'] for x in nulls], axis=0)
    res['lag_ratio'] = (np.array(obs['lag']) / lag_null).tolist()
    la = obs['line_above']
    print(f"{name:26s} exact {obs['exact']:.3f} (x{res['exact']['ratio']:.2f}, z={res['exact']['z']:+.1f}) | "
          f"1-edit {obs['near']:.3f} (x{res['near']['ratio']:.2f}, z={res['near']['z']:+.1f}) | "
          f"lag1-3 x{np.mean(res['lag_ratio'][:3]):.2f} lag20-40 x{np.mean(res['lag_ratio'][19:]):.2f} | "
          f"line above same/other {la['same_position']:.3f}/{la['other_positions']:.3f}", flush=True)
    return res


def main():
    sk = sta_lines()
    sta_words = [w for pg in sk for ln in pg['lines'] for w in ln]
    print(f'STA1: {len(sk)} pages, {sum(len(p["lines"]) for p in sk)} lines, {len(sta_words)} words', flush=True)
    corp = {
        'Voynich STA1': sk,
        'Voynich EVA': pour(C.voynich_eva(), sk),
        'Torah (Hebrew)': pour(C.torah_hebrew(), sk),
        'Moreh (Hebrew, Tibbon)': pour(C.tibbonid(), sk),
        'Judeo-Arabic': pour(C.judeo_arabic(), sk),
        "Ge'ez": pour(C.geez_clean(), sk),
        'Copy-and-modify (synthetic)': pour(copy_modify(sta_words, len(sta_words)), sk),
    }
    out = {name: analyse(name, pages) for name, pages in corp.items()}
    (HERE / 'results').mkdir(exist_ok=True)
    (HERE / 'results' / 'self_citation.json').write_text(json.dumps(out, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()

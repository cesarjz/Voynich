"""C1: is the entropy 'bounce' a property of the text or of the estimator?

The paper's estimator (nb 03/04 `entropia_condicional_n`) gives every context Witten-Bell
escape mass t/(c+t) and spreads it uniformly over the whole alphabet V. In sparse contexts
that term contributes about e*log2(V/e) bits, so the estimate can rise with order n, and
more so for large V. The true conditional entropy of a stationary source cannot rise.

Checks, all on flat symbol streams without word boundaries, as in nb 04:
  1. The verbatim notebook estimator (`wb_nb`) is reproduced exactly by the fast form
     (`wb_fast`) on the Voynich (H0..H4 = 4.141 2.961 2.990 3.317 3.774).
  2. Calibration corpora with known structure: Hebrew plaintext and its C2 ciphers at
     27 / 166 / 166-positional symbols, Ge'ez (188 signs), Judeo-Arabic L1, a
     token-shuffled STA1 (true H_n = H_0 for every n), and i.i.d. draws.
  3. Two other estimators: plug-in (maximum likelihood) and held-out cross-entropy
     with interpolated Witten-Bell back-off (train on 90 %, score the last 10 %).
  4. Size dependence (subsamples) and block-bootstrap CIs (200 resamples of 1,000-token
     blocks) of the paper's bounce for STA1 and EVA.

  5. `--decompose`: splits the paper estimate at each order into the part from observed
     continuations and the escape part spread over V, with a figure for the response letter.

Usage: python bounce_calibration.py   → results/bounce_calibration.json
       python bounce_calibration.py --decompose
         → results/bounce_decomposition.json, results/bounce_decomposition.png
"""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / 'reeval'))
import corpora as C  # noqa: E402
from nbcode import load_defs  # noqa: E402

C2 = HERE.parent / 'c2_benchmark' / 'data'
ORDERS = range(5)
N_TOK = 157_254  # STA1 flat stream length in nb 04


def counts(seq, n):
    ctx = defaultdict(Counter)
    for i in range(len(seq) - n):
        ctx[tuple(seq[i:i + n])][seq[i + n]] += 1
    return ctx


def h0(seq):
    f = np.array(list(Counter(seq).values()), dtype=float)
    p = f / f.sum()
    return float(-(p * np.log2(p)).sum())


def wb_fast(seq, n):
    """Same quantity as nb 04 `entropia_condicional_n`, in closed form per context."""
    if n == 0:
        return h0(seq)
    V = len(set(seq))
    ctx = counts(seq, n)
    total = sum(sum(c.values()) for c in ctx.values())
    H = 0.0
    for c in ctx.values():
        k = np.array(list(c.values()), dtype=float)
        cnt, t = k.sum(), len(k)
        d = cnt + t
        p = k / d
        hc = float(-(p * np.log2(p)).sum())
        if V > t:
            e = (t / d) / V
            hc -= (V - t) * e * math.log2(e)
        H += cnt / total * hc
    return H


def wb_parts(seq, n):
    """wb_fast split into (observed-continuation part, escape part, share of tokens in
    contexts seen < 10 times, number of contexts)."""
    V = len(set(seq))
    ctx = counts(seq, n)
    total = sum(sum(c.values()) for c in ctx.values())
    seen = esc = rare = 0.0
    for c in ctx.values():
        k = np.array(list(c.values()), dtype=float)
        cnt, t = k.sum(), len(k)
        d = cnt + t
        p = k / d
        seen += cnt / total * float(-(p * np.log2(p)).sum())
        if V > t:
            e = (t / d) / V
            esc -= cnt / total * (V - t) * e * math.log2(e)
        if cnt < 10:
            rare += cnt / total
    return seen, esc, rare, len(ctx)


def plugin(seq, n):
    if n == 0:
        return h0(seq)
    ctx = counts(seq, n)
    total = sum(sum(c.values()) for c in ctx.values())
    H = 0.0
    for c in ctx.values():
        k = np.array(list(c.values()), dtype=float)
        p = k / k.sum()
        H += k.sum() / total * float(-(p * np.log2(p)).sum())
    return H


def heldout_wb(seq, n, frac=0.9):
    """Cross-entropy (bits/symbol) of the last 10 % under an interpolated Witten-Bell model
    of order n trained on the first 90 %; base distribution is add-one unigram."""
    cut = int(len(seq) * frac)
    tr, te = seq[:cut], seq[cut:]
    V = sorted(set(seq))
    uni = Counter(tr)
    base = {s: (uni[s] + 1) / (len(tr) + len(V)) for s in V}
    tables = [counts(tr, k) for k in range(1, n + 1)]
    stats = [{h: (sum(c.values()), len(c)) for h, c in t.items()} for t in tables]

    def prob(hist, s):
        p = base[s]
        for k in range(1, len(hist) + 1):
            h = hist[-k:]
            st = stats[k - 1].get(h)
            if st is None:
                break
            cnt, t = st
            p = (tables[k - 1][h][s] + t * p) / (cnt + t)
        return p

    lp = [math.log2(prob(tuple(te[max(0, i - n):i]) if n else (), te[i])) for i in range(n, len(te))]
    return float(-np.mean(lp))


def curve(seq, est):
    return [est(seq, n) for n in ORDERS]


def bounce(H):
    return float(H[-1] - min(H))


def flat(words, n=N_TOK):
    return [g for w in words for g in w][:n]


def c2(name):
    return json.loads((C2 / f'{name}.json').read_text(encoding='utf-8'))['cipher_words']


def corpora():
    sta, _ = C.voynich_sta()
    eva = C.voynich_eva()
    torah = C2 / 'torah_holdout_L0.json'
    plain = json.loads(torah.read_text(encoding='utf-8'))['plain_words']
    rng = np.random.default_rng(7)
    s = flat(sta)
    shuf = list(np.array(s, dtype=object)[rng.permutation(len(s))])
    freq = Counter(s)
    syms, p = zip(*freq.items())
    p = np.array(p, dtype=float) / sum(p)
    iid = list(rng.choice(np.array(syms, dtype=object), size=len(s), p=p))
    return {
        'Voynich STA1 (V=166)': flat(sta),
        'Voynich EVA (V=34)': flat(eva),
        'Torah plaintext': flat(plain),
        'Torah L0 cipher': flat(c2('torah_holdout_L0')),
        'Torah L1 homophonic (166)': flat(c2('torah_holdout_L1')),
        'Torah L2 positional (166)': flat(c2('torah_holdout_L2')),
        'Moreh L1 homophonic (166)': flat(c2('moreh_L1')),
        "Ge'ez (188 signs)": flat(C.geez_clean()),
        'Judeo-Arabic L1 (156)': flat(c2('ctl_JARAB')),
        'STA1 token-shuffled': shuf,
        'i.i.d. STA1 unigram': iid,
    }


def block_bootstrap(seq, B=200, block=1000, seed=42):
    rng = np.random.default_rng(seed)
    blocks = [seq[i:i + block] for i in range(0, len(seq), block)]
    out = []
    for _ in range(B):
        s = [g for j in rng.integers(0, len(blocks), len(blocks)) for g in blocks[j]]
        out.append(bounce(curve(s, wb_fast)))
    return [float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))]


DECOMP = ('Voynich STA1 (V=166)', 'Voynich EVA (V=34)', 'Torah L1 homophonic (166)', 'STA1 token-shuffled')


def decompose():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    cs = corpora()
    out = {}
    for name in DECOMP:
        s = cs[name]
        rows = [{'n': 0, 'seen': h0(s), 'escape': 0.0, 'rare_share': 0.0, 'contexts': 1}]
        for n in range(1, 5):
            seen, esc, rare, nctx = wb_parts(s, n)
            rows.append({'n': n, 'seen': seen, 'escape': esc, 'rare_share': rare, 'contexts': nctx})
        out[name] = {'V': len(set(s)), 'orders': rows}
        print(name, 'V =', len(set(s)))
        for r in rows[1:]:
            print(f"  n={r['n']}: contexts {r['contexts']:6d}  tokens in contexts seen <10x {r['rare_share']:5.1%}  "
                  f"seen {r['seen']:.3f} + escape {r['escape']:.3f} = {r['seen'] + r['escape']:.3f}")
    (HERE / 'results').mkdir(exist_ok=True)
    (HERE / 'results' / 'bounce_decomposition.json').write_text(json.dumps(out, indent=1, ensure_ascii=False),
                                                               encoding='utf-8')

    blue, orange, ink, muted, grid = '#2a78d6', '#eb6834', '#1f1f1e', '#6b6a64', '#e6e5e0'
    titles = {DECOMP[0]: 'Voynich, STA1 (166 glyphs)', DECOMP[1]: 'Voynich, EVA (34 glyphs)',
              DECOMP[2]: 'Hebrew Torah, homophonic\ncipher (148 symbols)', DECOMP[3]: 'STA1 glyphs shuffled\n(no structure)'}
    plt.rcParams.update({'font.family': 'sans-serif',
                         'font.sans-serif': ['Nimbus Sans', 'Liberation Sans', 'DejaVu Sans'],  # Helvetica metrics
                         'mathtext.fontset': 'custom', 'mathtext.rm': 'Nimbus Sans',
                         'mathtext.it': 'Nimbus Sans:italic', 'mathtext.bf': 'Nimbus Sans:bold'})
    fig, axes = plt.subplots(2, 2, figsize=(6.4, 6.4), sharey=True)
    axes = axes.ravel()
    for ax, name in zip(axes, DECOMP):
        rows = out[name]['orders']
        x = [r['n'] for r in rows]
        seen = np.array([r['seen'] for r in rows])
        esc = np.array([r['escape'] for r in rows])
        ax.bar(x, seen, width=0.7, color=blue, edgecolor='white', linewidth=2, label='observed continuations')
        ax.bar(x, esc, width=0.7, bottom=seen, color=orange, edgecolor='white', linewidth=2,
               label='escape mass spread over V')
        ax.plot(x, seen + esc, color=ink, marker='o', markersize=4, linewidth=1.5, label='Witten–Bell estimate $H_n$')
        b = bounce(list(seen + esc))
        ax.set_title(f'{titles[name]}\nbounce = {b:.3f}', fontsize=10, color=ink)
        ax.set_xticks(x)
        ax.set_xlabel('context order $n$', fontsize=10, color=muted)
        ax.tick_params(colors=muted, labelsize=9)
        ax.grid(axis='y', color=grid, linewidth=0.8)
        ax.set_axisbelow(True)
        for sp in ('top', 'right'):
            ax.spines[sp].set_visible(False)
        for sp in ('left', 'bottom'):
            ax.spines[sp].set_color(grid)
    for i in (0, 2):
        axes[i].set_ylabel('bits per symbol', fontsize=10, color=muted)
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc='lower center', ncol=2, frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(HERE / 'results' / 'bounce_decomposition.png', dpi=300)
    # article Fig. 1: PNG, TIFF 600 dpi and EPS
    FIG = HERE.parent / 'figures'
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / 'fig_entropy_estimator.png', dpi=300)
    fig.savefig(FIG / 'figure1.tif', dpi=600, pil_kwargs={'compression': 'tiff_lzw'})
    fig.savefig(FIG / 'figure1.eps')
    print('figure: results/bounce_decomposition.png; figures/fig_entropy_estimator.png, figure1.tif, figure1.eps')


def main():
    if '--decompose' in sys.argv:
        decompose()
        return
    cs = corpora()
    sta = cs['Voynich STA1 (V=166)']
    # 1. exact reproduction of the notebook estimator (n <= 2 for speed; it is O(contexts^2))
    nb = load_defs('04_multilingual_controls.ipynb', ['entropia_condicional_n'])
    nb['entropia_condicional_n'].__globals__.update(Counter=Counter, math=math)
    repro = {n: (nb['entropia_condicional_n'](sta, n), wb_fast(sta, n)) for n in (0, 1, 2)}
    for n, (a, b) in repro.items():
        assert abs(a - b) < 1e-9, (n, a, b)
    print('notebook estimator reproduced:', {n: round(a, 4) for n, (a, _) in repro.items()}, flush=True)

    out = {'reproduction': repro, 'corpora': {}}
    print(f"\n{'corpus':28s} {'V':>4s} | {'paper WB: H0..H4':34s} bnc | {'plug-in H4':>9s} bnc | "
          f"{'held-out WB H0..H4':34s} bnc", flush=True)
    for name, s in cs.items():
        r = {'V': len(set(s)), 'tokens': len(s)}
        for k, est in (('wb_paper', wb_fast), ('plugin', plugin), ('heldout_wb', heldout_wb)):
            H = curve(s, est)
            r[k] = {'H': H, 'bounce': bounce(H)}
        out['corpora'][name] = r
        f = lambda H: ' '.join(f'{x:.3f}' for x in H)  # noqa: E731
        print(f"{name:28s} {r['V']:4d} | {f(r['wb_paper']['H'])} {r['wb_paper']['bounce']:.3f} | "
              f"{r['plugin']['H'][-1]:9.3f} {r['plugin']['bounce']:.3f} | "
              f"{f(r['heldout_wb']['H'])} {r['heldout_wb']['bounce']:.3f}", flush=True)

    print('\nSize dependence of the paper bounce', flush=True)
    out['size'] = {}
    for name in ('Voynich STA1 (V=166)', 'Torah L1 homophonic (166)', 'Voynich EVA (V=34)', 'Torah plaintext'):
        row = {n: bounce(curve(cs[name][:n], wb_fast)) for n in (20_000, 40_000, 80_000, N_TOK)}
        if name == 'Torah plaintext':
            row[400_000] = bounce(curve(flat(C.torah_hebrew(), 400_000), wb_fast))
        out['size'][name] = row
        print(f'  {name:28s} ' + ' '.join(f'{n // 1000}k:{b:.3f}' for n, b in row.items()), flush=True)

    print('\nBlock-bootstrap 95 % CI of the paper bounce', flush=True)
    out['bootstrap'] = {}
    for name in ('Voynich STA1 (V=166)', 'Voynich EVA (V=34)', 'Torah L1 homophonic (166)'):
        out['bootstrap'][name] = block_bootstrap(cs[name])
        print(f'  {name:28s} {out["bootstrap"][name]}', flush=True)

    (HERE / 'results').mkdir(exist_ok=True)
    (HERE / 'results' / 'bounce_calibration.json').write_text(json.dumps(out, indent=1, ensure_ascii=False),
                                                             encoding='utf-8')


if __name__ == '__main__':
    main()

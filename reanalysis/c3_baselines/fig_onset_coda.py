"""Figure for the paper: onset/coda type ratio, observed vs words reversed, Voynich vs controls
(Semitic, 16 further historical texts from onset_coda_v2.json, homophonic, verbose).

Reads results/onset_coda_null.json (Voynich, natural, homophonic, verbose seed 42) and
results/onset_coda_factors_seeds.json (5 further codebooks per verbose design).
Usage: python fig_onset_coda.py  -> ../figures/fig_onset_coda.png
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).parent
OUT = HERE.parent / 'figures' / 'fig_onset_coda.png'
INK, MUTED, GRID = '#0b0b0b', '#52514e', '#e4e3df'
COL = {'voynich': '#2a78d6', 'natural': '#eb6834', 'homoph': '#1baf7a', 'verbose': '#eda100', 'nonsem': '#52514e'}

null = json.load(open(HERE / 'results' / 'onset_coda_null.json'))['corpora']
v2 = json.load(open(HERE / 'results' / 'onset_coda_v2.json'))['corpora']
seeds = json.load(open(HERE / 'results' / 'onset_coda_factors_seeds.json'))


def pt(name):
    c = null[name]
    return c['observed']['pair'], c['reversed']['pair']


groups = {
    'natural': ['Torah', 'Moreh', 'Judeo-Arabic', "Ge'ez fidel", "Ge'ez consonants"],
    'homoph': ['Torah homophonic L1', 'Moreh homophonic L1'],
}
verbose = [pt('Torah verbose-fixed'), pt('Torah verbose-homoph')] + [tuple(p) for v in seeds.values() for p in v]

plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Nimbus Sans', 'Liberation Sans', 'DejaVu Sans'],
                     'font.size': 9, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK,
                     'xtick.color': MUTED, 'ytick.color': MUTED})
fig, ax = plt.subplots(figsize=(6.2, 4.6))
ax.set_facecolor('white')
fig.patch.set_facecolor('white')
ax.set_xscale('log')
ax.set_yscale('log')
ax.axvline(1, color=GRID, lw=1, zorder=0)
ax.axhline(1, color=GRID, lw=1, zorder=0)

ax.scatter(*zip(*verbose), s=34, marker='^', color=COL['verbose'], edgecolor='#fcfcfb', lw=1,
           label=f'verbose ciphers of Hebrew ({len(verbose)} codebooks)', zorder=2)
ax.scatter(*zip(*[pt(n) for n in groups['homoph']]), s=40, marker='s', color=COL['homoph'],
           edgecolor='#fcfcfb', lw=1, label='homophonic Hebrew (~150 symbols)', zorder=3)
ax.scatter(*zip(*[pt(n) for n in groups['natural']]), s=44, marker='o', color=COL['natural'],
           edgecolor='#fcfcfb', lw=1, label="Semitic texts (Hebrew, Judeo-Arabic, Ge'ez)", zorder=3)
nonsem = [(v['pair'], v['reversed']) for k, v in v2.items()
          if not k.startswith('Voynich') and k not in groups['natural']]
ax.scatter(*zip(*nonsem), s=40, marker='v', facecolor='none', edgecolor=COL['nonsem'], lw=1.2,
           label=f'other historical texts ({len(nonsem)}, 11 languages)', zorder=3)
vx, vy = zip(*[pt('Voynich STA1'), pt('Voynich EVA')])
ax.scatter(vx, vy, s=70, marker='D', color=COL['voynich'], edgecolor='#fcfcfb', lw=1.2,
           label='Voynich', zorder=4)
ax.annotate('STA1', (vx[0], vy[0]), xytext=(8, -12), textcoords='offset points', color=INK)
ax.annotate('EVA', (vx[1], vy[1]), xytext=(8, 4), textcoords='offset points', color=INK)

ax.set_xlabel('onset/coda type ratio (observed)')
ax.set_ylabel('onset/coda type ratio (words reversed)')
ax.set_xlim(0.25, 4.5)
ax.set_ylim(0.2, 2.6)
ticks = [0.25, 0.5, 1, 2, 4]
ax.set_xticks(ticks, [str(t) for t in ticks])
ax.set_yticks([0.25, 0.5, 1, 2], ['0.25', '0.5', '1', '2'])
ax.minorticks_off()
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
ax.legend(frameon=False, loc='lower left', fontsize=7.5, labelcolor=INK)
fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=300)
fig.savefig(OUT.parent / 'figure2.tif', dpi=600, pil_kwargs={'compression': 'tiff_lzw'})
fig.savefig(OUT.parent / 'figure2.eps')
print(OUT, OUT.parent / 'figure2.tif', OUT.parent / 'figure2.eps')

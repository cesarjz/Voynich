#!/usr/bin/env python3
"""
Generate English-language figures for the DSH paper.
Reproduces the 8 figures from the Spanish notebooks with English labels.
Run from the paper/ directory: python gen_figures_en.py
"""

import sys, os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from collections import Counter

matplotlib.rcParams.update({
    'figure.dpi': 130, 'savefig.dpi': 300,
    'font.size': 10, 'axes.titlesize': 11,
    'axes.labelsize': 11, 'legend.fontsize': 8,
})

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(os.path.dirname(OUT_DIR), 'images')

# ============================================================
# DATA: All values extracted from notebook outputs
# ============================================================

CORPUS_ORDER = ['Voynich', 'Latin', 'Caesar', 'Vigenère', 'Hebrew',
                'Arabic', 'Turkish', 'Finnish']

# H0–H4 entropy curves (from notebook 04 outputs)
H_CURVES = {
    'Voynich':  [4.1408, 2.9608, 2.9898, 3.3165, 3.7739],
    'Latin':    [4.1213, 3.4629, 2.9510, 2.5929, 2.4660],
    'Caesar':   [4.1213, 3.4629, 2.9510, 2.5929, 2.4660],
    'Vigenère': [4.6158, 4.3244, 3.5934, 3.1157, 2.8935],
    'Hebrew':   [4.2302, 3.8846, 3.3792, 3.0772, 2.9642],
    'Arabic':   [4.3698, 3.9223, 3.3614, 3.0295, 2.9116],
    'Turkish':  [4.3505, 3.7456, 3.2649, 2.9562, 2.8631],
    'Finnish':  [3.9536, 3.4475, 3.1251, 2.8484, 2.7459],
}

# MI values (from notebook 04 outputs)
MI_POS = {
    'Voynich': 0.6578, 'Latin': 0.2672, 'Caesar': 0.2672,
    'Vigenère': 0.0531, 'Hebrew': 0.3113, 'Arabic': 0.2340,
    'Turkish': 0.1505, 'Finnish': 0.2054,
}
MI_BIG = {
    'Voynich': 1.6811, 'Latin': 1.0819, 'Caesar': 1.0819,
    'Vigenère': 0.4446, 'Hebrew': 0.6069, 'Arabic': 0.7488,
    'Turkish': 0.8346, 'Finnish': 0.6519,
}

# Full fingerprint (from scorecard output)
FINGERPRINT = {
    'Voynich':  {'H0': 4.141, 'Decay': 0.089, 'Gap': 0.541, 'Bounce': 0.813, 'MI_pos': 0.658, 'MI_big': 1.681},
    'Latin':    {'H0': 4.121, 'Decay': 0.402, 'Gap': 0.658, 'Bounce': 0.000, 'MI_pos': 0.267, 'MI_big': 1.082},
    'Caesar':   {'H0': 4.121, 'Decay': 0.402, 'Gap': 0.658, 'Bounce': 0.000, 'MI_pos': 0.267, 'MI_big': 1.082},
    'Vigenère': {'H0': 4.616, 'Decay': 0.373, 'Gap': 0.855, 'Bounce': 0.000, 'MI_pos': 0.053, 'MI_big': 0.445},
    'Hebrew':   {'H0': 4.230, 'Decay': 0.299, 'Gap': 0.812, 'Bounce': 0.000, 'MI_pos': 0.311, 'MI_big': 0.607},
    'Arabic':   {'H0': 4.370, 'Decay': 0.334, 'Gap': 0.798, 'Bounce': 0.000, 'MI_pos': 0.234, 'MI_big': 0.749},
    'Turkish':  {'H0': 4.351, 'Decay': 0.342, 'Gap': 0.509, 'Bounce': 0.000, 'MI_pos': 0.151, 'MI_big': 0.835},
    'Finnish':  {'H0': 3.954, 'Decay': 0.305, 'Gap': 0.577, 'Bounce': 0.000, 'MI_pos': 0.205, 'MI_big': 0.652},
}

# ── Colour / marker maps ──
COLOR_MAP = {
    'Voynich': '#E53935', 'Latin': '#1E88E5', 'Caesar': '#8E24AA',
    'Vigenère': '#6D4C41', 'Hebrew': '#43A047', 'Arabic': '#FDD835',
    'Turkish': '#00ACC1', 'Finnish': '#FB8C00',
    # Synthetic models
    'Slot': '#7B1FA2', 'Verbose': '#455A64', 'Nomenclator': '#0277BD',
    'Hybrid': '#2E7D32', 'NomPoly': '#EF6C00', 'Silabico': '#AD1457',
    'SilPart': '#D32F2F', 'Cardan': '#5D4037', 'AutoCita': '#00695C',
    'Polyg3': '#283593', 'Naibbe': '#F9A825',
}
MARKER_MAP = {
    'Voynich': 'o', 'Latin': 's', 'Caesar': '^', 'Vigenère': 'D',
    'Hebrew': 'v', 'Arabic': '<', 'Turkish': '>', 'Finnish': 'p',
    'Slot': 's', 'Verbose': '^', 'Nomenclator': 'D', 'Hybrid': 'H',
    'NomPoly': '8', 'Silabico': 'P', 'SilPart': '2',
    'Cardan': 'p', 'AutoCita': '*', 'Polyg3': 'h', 'Naibbe': 'd',
}
LW_MAP = {name: (3 if name == 'Voynich' else 1.5) for name in CORPUS_ORDER}

# ── Generative models data ──
# H0–H6 curves (from notebook 05 outputs)
H_EXT = {
    'Voynich':     [4.1408, 2.9608, 2.9898, 3.3165, 3.7739, 4.1740, 4.4086],
    'Slot':        [3.1511, 2.9407, 3.0170, 3.2664, 3.5977, 3.9323, 4.2229],
    'Verbose':     [4.3025, 2.9142, 2.5626, 2.3381, 2.2595, 2.3122, 2.4282],
    'Nomenclator': [5.3487, 4.1193, 3.8171, 3.8606, 3.9171, 3.9850, 4.0412],
    'Hybrid':      [3.7893, 3.0930, 3.2245, 3.5686, 4.0504, 4.3976, 4.4262],
    'NomPoly':     [7.4604, 5.8694, 5.5439, 4.9525, 4.8378, 4.8045, 4.8010],
    'Silabico':    [5.0858, 3.7727, 3.9832, 4.3809, 4.6793, 4.6055, 4.5149],
    'SilPart':     [5.2484, 3.6707, 3.7100, 4.1789, 4.5799, 4.6558, 4.5658],
    'Cardan':      [5.0235, 1.2753, 1.1186, 1.1607, 1.2311, 1.3471, 1.4931],
    'AutoCita':    [6.8058, 5.3205, 4.5116, 4.2429, 4.3631, 4.4819, 4.5620],
    'Polyg3':      [6.6271, 4.4244, 3.8734, 3.9699, 4.0540, 4.1880, 4.2902],
    'Naibbe':      [7.3162, 5.3289, 4.0876, 4.3185, 4.6412, 4.5998, 4.6245],
}

# Distances (from ranking table)
DISTANCES = {
    'SilPart': 0.445, 'Silabico': 0.506, 'Hybrid': 0.783,
    'Naibbe': 1.028, 'AutoCita': 1.356, 'Nomenclator': 1.389,
    'Slot': 1.410, 'NomPoly': 1.636, 'Polyg3': 1.655,
    'Verbose': 1.748, 'Cardan': 4.485,
}

# All model metrics (5 metrics) — for radar and sensitivity
SYNTH_ORDER = ['Slot', 'Verbose', 'Nomenclator', 'Hybrid', 'NomPoly',
               'Silabico', 'SilPart', 'Cardan', 'AutoCita', 'Polyg3', 'Naibbe']

ALL_METRICS = {
    'Voynich':     {'Decay': 0.089, 'Bounce': 0.813, 'Gap': 0.541, 'MI_pos': 0.658, 'MI_big': 1.681},
    'Slot':        {'Decay':-0.142, 'Bounce': 0.657, 'Gap': 0.378, 'MI_pos': 0.396, 'MI_big': 0.623},
    'Verbose':     {'Decay': 0.475, 'Bounce': 0.000, 'Gap': 0.540, 'MI_pos': 0.000, 'MI_big': 1.390},
    'Nomenclator': {'Decay': 0.268, 'Bounce': 0.100, 'Gap': 0.330, 'MI_pos': 0.246, 'MI_big': 1.846},
    'Hybrid':      {'Decay':-0.069, 'Bounce': 0.957, 'Gap': 0.393, 'MI_pos': 0.400, 'MI_big': 1.178},
    'NomPoly':     {'Decay': 0.352, 'Bounce': 0.000, 'Gap': 0.525, 'MI_pos': 0.122, 'MI_big': 1.968},
    'Silabico':    {'Decay': 0.080, 'Bounce': 0.907, 'Gap': 0.128, 'MI_pos': 0.458, 'MI_big': 1.668},
    'SilPart':     {'Decay': 0.127, 'Bounce': 0.909, 'Gap': 0.264, 'MI_pos': 0.477, 'MI_big': 1.848},
    'Cardan':      {'Decay': 0.755, 'Bounce': 0.112, 'Gap': 0.236, 'MI_pos': 1.075, 'MI_big': 5.087},
    'AutoCita':    {'Decay': 0.359, 'Bounce': 0.120, 'Gap': 0.732, 'MI_pos': 0.312, 'MI_big': 1.836},
    'Polyg3':      {'Decay': 0.388, 'Bounce': 0.181, 'Gap': 0.405, 'MI_pos': 0.001, 'MI_big': 2.362},
    'Naibbe':      {'Decay': 0.366, 'Bounce': 0.554, 'Gap': 0.768, 'MI_pos': 0.001, 'MI_big': 1.725},
    # Languages
    'Latin':       {'Decay': 0.402, 'Bounce': 0.000, 'Gap': 0.658, 'MI_pos': 0.267, 'MI_big': 1.082},
    'Caesar':      {'Decay': 0.402, 'Bounce': 0.000, 'Gap': 0.658, 'MI_pos': 0.267, 'MI_big': 1.082},
    'Vigenère':    {'Decay': 0.373, 'Bounce': 0.000, 'Gap': 0.855, 'MI_pos': 0.053, 'MI_big': 0.445},
    'Hebrew':      {'Decay': 0.299, 'Bounce': 0.000, 'Gap': 0.812, 'MI_pos': 0.311, 'MI_big': 0.607},
    'Arabic':      {'Decay': 0.334, 'Bounce': 0.000, 'Gap': 0.798, 'MI_pos': 0.234, 'MI_big': 0.749},
    'Turkish':     {'Decay': 0.342, 'Bounce': 0.000, 'Gap': 0.509, 'MI_pos': 0.151, 'MI_big': 0.835},
    'Finnish':     {'Decay': 0.305, 'Bounce': 0.000, 'Gap': 0.577, 'MI_pos': 0.205, 'MI_big': 0.652},
}

# Multilingual H0-H4 (for comparison plot panel B)
MULTI_H04 = {
    'Latin':    [4.121, 3.463, 2.951, 2.593, 2.466],
    'Caesar':   [4.121, 3.463, 2.951, 2.593, 2.466],
    'Vigenère': [4.616, 4.324, 3.593, 3.116, 2.894],
    'Hebrew':   [4.230, 3.885, 3.379, 3.077, 2.964],
    'Arabic':   [4.370, 3.922, 3.361, 3.030, 2.912],
    'Turkish':  [4.351, 3.746, 3.265, 2.956, 2.863],
    'Finnish':  [3.954, 3.447, 3.125, 2.848, 2.746],
}

# Semantic enrichment matrix (from notebook 10)
ENRICHMENT = np.array([
    [1.073, 3.884, 1.558, 0.795, 1.535, 0.465],
    [1.149, 3.635, 2.033, 0.238, 1.296, 0.736],
    [1.112, 12.781, 0.000, 0.209, 0.000, 0.266],
    [0.985, 12.116, 0.000, 0.000, 0.000, 0.650],
    [1.051, 3.207, 1.467, 0.400, 0.312, 1.130],
])
SEM_CATEGORIES = ['botany/nature', 'astronomy/time', 'body/biology',
                  'religion/ritual', 'society/material']
SEM_SECTIONS = ['herbal', 'astronomical', 'zodiac', 'biological',
                'pharmaceutical', 'recipes']
# Expected correspondences: (section_idx, category_idx)
EXPECTED = [(0, 0), (1, 1), (2, 1), (3, 2), (4, 3), (5, 4)]

# Sensitivity analysis results (from notebook 05 output)
SENS_TOP1 = {'SilPart': 355, 'Silabico': 97, 'Hybrid': 37, 'Naibbe': 10, 'AutoCita': 1}
SENS_RHO_MEDIAN = 0.9182
SENS_RHO_MEAN = 0.8910
N_MC = 500


# ============================================================
# FIGURE 1: Entropy curves (bloque_C_multilingue.png)
# ============================================================
def fig1_entropy():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    orders = [0, 1, 2, 3, 4]

    for name in CORPUS_ORDER:
        vals = H_CURVES[name]
        ax1.plot(orders, vals, color=COLOR_MAP[name], marker=MARKER_MAP[name],
                 lw=LW_MAP[name], markersize=7, label=name)
    ax1.set_xlabel('Order N')
    ax1.set_ylabel('H(X | context N)')
    ax1.set_title('(A) Conditional entropy (absolute)', fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    for name in CORPUS_ORDER:
        vals = H_CURVES[name]
        norm = [v / vals[0] for v in vals]
        ax2.plot(orders, norm, color=COLOR_MAP[name], marker=MARKER_MAP[name],
                 lw=LW_MAP[name], markersize=7, label=name)
    ax2.set_xlabel('Order N')
    ax2.set_ylabel(r'$H_N\;/\;H_0$')
    ax2.set_title('(B) Conditional entropy (normalised)', fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    fig.suptitle('Multilingual conditional entropy curves', fontsize=13, fontweight='bold')
    plt.tight_layout()
    out = os.path.join(IMG_DIR, 'bloque_C_multilingue.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'  Saved: {out}')


# ============================================================
# FIGURE 2: MI scatter + bars (mi_multilingue.png)
# ============================================================
def fig2_mi():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    x = np.arange(len(CORPUS_ORDER))
    width = 0.35
    vals_pos = [MI_POS[n] for n in CORPUS_ORDER]
    vals_big = [MI_BIG[n] for n in CORPUS_ORDER]
    colors_bar = [COLOR_MAP[n] for n in CORPUS_ORDER]

    ax1.bar(x - width/2, vals_pos, width, label='Positional MI',
            color=colors_bar, alpha=0.85, edgecolor='black')
    ax1.bar(x + width/2, vals_big, width, label='Bigram MI',
            color=colors_bar, alpha=0.4, edgecolor='black', hatch='//')
    ax1.set_xticks(x)
    ax1.set_xticklabels(CORPUS_ORDER, rotation=45, ha='right')
    ax1.set_ylabel('MI (bits)')
    ax1.set_title('(A) Positional MI vs bigram MI', fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')

    for name in CORPUS_ORDER:
        ax2.scatter(MI_POS[name], MI_BIG[name], color=COLOR_MAP[name],
                    marker=MARKER_MAP[name], s=120, label=name,
                    edgecolors='black', zorder=5)
    ax2.set_xlabel('Positional MI (bits)')
    ax2.set_ylabel('Bigram MI (bits)')
    ax2.set_title('(B) Positional MI vs bigram MI', fontweight='bold')
    ax2.legend(fontsize=8, ncol=2)
    ax2.grid(True, alpha=0.3)

    fig.suptitle('Multilingual MI analysis', fontsize=13, fontweight='bold')
    plt.tight_layout()
    out = os.path.join(IMG_DIR, 'mi_multilingue.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'  Saved: {out}')


# ============================================================
# FIGURE 3: Fingerprint heatmap (fingerprint_multilingue.png)
# ============================================================
def fig3_fingerprint():
    import pandas as pd

    cols = ['H0', 'Decay', 'Gap', 'Bounce', 'MI_pos', 'MI_big']
    data_raw = {}
    for name in CORPUS_ORDER:
        data_raw[name] = FINGERPRINT[name]

    df_raw = pd.DataFrame(data_raw).T
    df_raw = df_raw[cols]
    df_norm = (df_raw - df_raw.min()) / (df_raw.max() - df_raw.min())

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(df_norm, annot=df_raw.round(3).values, fmt='', cmap='YlOrRd',
                vmin=0, vmax=1.0, linewidths=0.5, ax=ax,
                xticklabels=cols, yticklabels=CORPUS_ORDER)
    ax.set_title('Multilingual fingerprint (colour = normalised, value = raw)',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    out = os.path.join(IMG_DIR, 'fingerprint_multilingue.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'  Saved: {out}')


# ============================================================
# FIGURE 4: Voynich distributions (voynich_distribuciones.png)
# ============================================================
def fig4_distributions():
    import re

    # Parse STA1 2.0 corpus
    corpus_file = os.path.join(os.path.dirname(OUT_DIR), 'corpus', 'voynich_sta.txt')
    if not os.path.isfile(corpus_file):
        print('  SKIP fig4: corpus/voynich_sta.txt not found')
        return

    words = []       # each word = list of glyph strings
    glyphs_flat = []

    with open(corpus_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if re.match(r'^<[^>]+>\s*<!', line):  # folio metadata
                continue

            match = re.match(r'^<[^>]+>\s+(.*)', line)
            if match:
                glyph_text = match.group(1).strip()
            else:
                continue

            glyph_text = re.sub(r'\{[^}]*\}', '', glyph_text)
            glyph_text = re.sub(r'<[^>]*>', '', glyph_text)
            glyph_text = re.sub(r'-', '.', glyph_text)
            glyph_text = glyph_text.strip()
            if not glyph_text:
                continue

            for word_raw in glyph_text.split('.'):
                word_raw = word_raw.strip()
                if not word_raw:
                    continue
                glyphs = [g for g in re.findall(r'[A-Z][0-9a-z]?', word_raw)
                          if len(g) == 2]
                if glyphs:
                    words.append(glyphs)
                    glyphs_flat.extend(glyphs)

    if not words:
        print('  SKIP fig4: could not parse corpus')
        return

    max_wlen = max(len(w) for w in words)  # w is a list of glyphs
    lens = [len(w) for w in words]

    # Positional distributions
    pos_probs = {}
    for w in words:
        for i, g in enumerate(w):
            pos_probs.setdefault(i, Counter())[g] += 1
    for pos in pos_probs:
        total = sum(pos_probs[pos].values())
        pos_probs[pos] = {g: c/total for g, c in pos_probs[pos].items()}

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel A: Word length histogram
    ax = axes[0, 0]
    ax.hist(lens, bins=range(1, max_wlen + 2), color='#E53935', alpha=0.8,
            edgecolor='black', density=True)
    ax.set_xlabel('Word length (glyphs)')
    ax.set_ylabel('Density')
    ax.set_title('(A) Word length distribution')
    ax.axvline(np.mean(lens), color='black', ls='--', label=f'mean={np.mean(lens):.2f}')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Panel B: Top-20 glyph × position heatmap
    ax = axes[0, 1]
    top_glyphs = [g for g, _ in Counter(glyphs_flat).most_common(20)]
    pos_range = range(min(8, max_wlen))
    heat = np.zeros((len(top_glyphs), len(pos_range)))
    for j, pos in enumerate(pos_range):
        if pos in pos_probs:
            for i, g in enumerate(top_glyphs):
                heat[i, j] = pos_probs[pos].get(g, 0)
    sns.heatmap(heat, ax=ax, xticklabels=[str(p) for p in pos_range],
                yticklabels=top_glyphs, cmap='YlOrRd',
                cbar_kws={'label': 'P(glyph|pos)'})
    ax.set_xlabel('Position in word')
    ax.set_title('(B) Top-20 glyphs × position')

    # Panel C: Zipf
    ax = axes[1, 0]
    freq = Counter(glyphs_flat)
    ranks = range(1, len(freq) + 1)
    freqs_sorted = sorted(freq.values(), reverse=True)
    ax.loglog(list(ranks), freqs_sorted, 'o-', color='#E53935', markersize=3)
    ax.set_xlabel('Rank')
    ax.set_ylabel('Frequency')
    ax.set_title('(C) Glyph Zipf distribution')
    ax.grid(True, alpha=0.3)

    # Panel D: Positional distributions
    ax = axes[1, 1]
    for pos_i, color_i in [(0, '#E53935'), (1, '#1E88E5'), (2, '#43A047')]:
        if pos_i in pos_probs:
            probs = pos_probs[pos_i]
            sorted_probs = sorted(probs.values(), reverse=True)
            ax.plot(range(1, len(sorted_probs) + 1), sorted_probs, 'o-',
                    color=color_i, markersize=3, label=f'pos={pos_i}')
    ax.set_xlabel('Glyph rank')
    ax.set_ylabel('Probability')
    ax.set_title('(D) Distributions by position')
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.suptitle('Voynich Manuscript empirical distributions', fontsize=14, fontweight='bold')
    plt.tight_layout()
    out = os.path.join(IMG_DIR, 'voynich_distribuciones.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'  Saved: {out}')


# ============================================================
# FIGURE 5: Synthetic entropy curves (comparacion_curvas_sinteticos.png)
# ============================================================
def fig5_synthetic_curves():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    orders_ext = [0, 1, 2, 3, 4, 5, 6]
    orders_plot = [0, 1, 2, 3, 4]

    # Panel A: H0–H6 absolute
    ax1.plot(orders_ext, H_EXT['Voynich'], 'o-', color=COLOR_MAP['Voynich'],
             lw=3, markersize=8, label='Voynich', zorder=10)
    for name in SYNTH_ORDER:
        d = DISTANCES[name]
        ax1.plot(orders_ext, H_EXT[name], MARKER_MAP[name] + '--',
                 color=COLOR_MAP[name], lw=2, markersize=7,
                 label=f'{name} (d={d:.2f})')
    ax1.set_xlabel('Order N')
    ax1.set_ylabel('H(X | context N)')
    ax1.set_title('(A) H0–H6: Voynich vs 11 synthetic models (best configs)',
                  fontweight='bold')
    ax1.legend(fontsize=8, ncol=2)
    ax1.grid(True, alpha=0.3)

    # Panel B: H0–H4 normalised (all)
    v_norm = [v / H_EXT['Voynich'][0] for v in H_EXT['Voynich'][:5]]
    ax2.plot(orders_plot, v_norm, 'o-', color=COLOR_MAP['Voynich'], lw=3,
             markersize=8, label='Voynich', zorder=10)

    for name in SYNTH_ORDER:
        h = H_EXT[name]
        norm = [v / h[0] for v in h[:5]]
        ax2.plot(orders_plot, norm, MARKER_MAP[name] + '--',
                 color=COLOR_MAP[name], lw=2, markersize=6, label=name)

    for name, h_vals in MULTI_H04.items():
        norm = [v / h_vals[0] for v in h_vals]
        ax2.plot(orders_plot, norm, MARKER_MAP[name] + ':',
                 color=COLOR_MAP[name], lw=1, markersize=4, alpha=0.6, label=name)

    ax2.set_xlabel('Order N')
    ax2.set_ylabel(r'$H_N\;/\;H_0$')
    ax2.set_title('(B) H0–H4 normalised: 19 corpora', fontweight='bold')
    ax2.legend(fontsize=6, ncol=3, loc='best')
    ax2.grid(True, alpha=0.3)

    fig.suptitle('Comparison: synthetic models vs Voynich and natural languages',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    out = os.path.join(IMG_DIR, 'comparacion_curvas_sinteticos.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'  Saved: {out}')


# ============================================================
# FIGURE 6: Radar plots (radar_sinteticos.png)
# ============================================================
def fig6_radar():
    import pandas as pd

    radar_metrics = ['Decay', 'Bounce', 'Gap', 'MI_pos', 'MI_big']
    n_metrics = len(radar_metrics)
    angles = np.linspace(0, 2 * np.pi, n_metrics, endpoint=False).tolist()
    angles += angles[:1]

    # Build normalised DataFrame
    all_names = ['Voynich'] + SYNTH_ORDER
    data = {n: ALL_METRICS[n] for n in all_names}
    df = pd.DataFrame(data).T
    df = df[radar_metrics]
    df_norm = (df - df.min()) / (df.max() - df.min())

    n_models = len(SYNTH_ORDER)
    n_cols = 4
    n_rows = (n_models + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(24, 6 * n_rows),
                             subplot_kw=dict(polar=True))
    axes = axes.flatten()

    for ax, synth_name in zip(axes[:n_models], SYNTH_ORDER):
        vals_v = [df_norm.loc['Voynich', m] for m in radar_metrics]
        vals_v += vals_v[:1]
        ax.plot(angles, vals_v, 'o-', color=COLOR_MAP['Voynich'], lw=2, label='Voynich')
        ax.fill(angles, vals_v, color=COLOR_MAP['Voynich'], alpha=0.1)

        vals_s = [df_norm.loc[synth_name, m] for m in radar_metrics]
        vals_s += vals_s[:1]
        ax.plot(angles, vals_s, 's--', color=COLOR_MAP[synth_name], lw=2, label=synth_name)
        ax.fill(angles, vals_s, color=COLOR_MAP[synth_name], alpha=0.1)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(radar_metrics, fontsize=9)
        d = DISTANCES.get(synth_name, 0)
        ax.set_title(f'Voynich vs {synth_name} (d={d:.2f})',
                     fontsize=11, fontweight='bold', pad=15)
        ax.legend(loc='upper right', fontsize=8, bbox_to_anchor=(1.3, 1.1))
        ax.set_ylim(0, 1.1)

    for i in range(n_models, len(axes)):
        axes[i].set_visible(False)

    fig.suptitle('Radar: Voynich vs synthetic models (normalised metrics)',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    out = os.path.join(IMG_DIR, 'radar_sinteticos.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'  Saved: {out}')


# ============================================================
# FIGURE 7: Sensitivity analysis (sensibilidad_pesos.png)
# ============================================================
def fig7_sensitivity():
    import math
    from scipy.stats import spearmanr

    WEIGHTS_BASE = {'bounce': 3.0, 'decay': 2.0, 'MI_pos': 1.5, 'MI_big': 1.5, 'gap': 1.0}
    KEYS = list(WEIGHTS_BASE.keys())
    synth_names = SYNTH_ORDER

    VOYNICH_T = {'bounce': 0.813, 'decay': 0.089, 'MI_pos': 0.658, 'MI_big': 1.681, 'gap': 0.541}
    KEY_MAP = {'bounce': 'Bounce', 'decay': 'Decay', 'MI_pos': 'MI_pos',
               'MI_big': 'MI_big', 'gap': 'Gap'}

    def compute_ranking(weights):
        dists = []
        for name in synth_names:
            m = ALL_METRICS[name]
            d2 = sum(weights[k] * (m[KEY_MAP[k]] - VOYNICH_T[k])**2 for k in KEYS)
            dists.append(math.sqrt(d2))
        return dists

    base_dists = compute_ranking(WEIGHTS_BASE)
    base_order = np.argsort(base_dists)
    base_ranks = np.empty_like(base_order)
    base_ranks[base_order] = np.arange(len(base_order))

    # Perturbations
    perturbations = {}
    for key in KEYS:
        for factor, label in [(0.5, f'{key}×0.5'), (1.5, f'{key}×1.5')]:
            p = dict(WEIGHTS_BASE)
            p[key] = WEIGHTS_BASE[key] * factor
            perturbations[label] = p
    perturbations['Uniform'] = {k: 1.0 for k in KEYS}
    perturbations['Bounce only'] = {k: (5.0 if k == 'bounce' else 0.1) for k in KEYS}
    perturbations['MI only'] = {k: (5.0 if k in ('MI_pos', 'MI_big') else 0.1) for k in KEYS}
    perturbations['Inverted'] = {'bounce': 1.0, 'decay': 1.5, 'MI_pos': 2.0, 'MI_big': 3.0, 'gap': 3.0}

    sens_results = []
    for label, weights in perturbations.items():
        dists = compute_ranking(weights)
        order = np.argsort(dists)
        ranks = np.empty_like(order)
        ranks[order] = np.arange(len(order))
        rho, _ = spearmanr(base_ranks, ranks)
        sens_results.append({
            'label': label, 'rho': rho,
            'ranks': {synth_names[i]: int(ranks[i]) + 1 for i in range(len(synth_names))},
        })

    # Monte Carlo
    rng = np.random.RandomState(42)
    mc_rhos = []
    mc_top1 = Counter()
    for _ in range(N_MC):
        raw = rng.dirichlet(np.ones(5))
        weights_mc = {k: float(raw[i] * 5 * len(KEYS)) for i, k in enumerate(KEYS)}
        dists = compute_ranking(weights_mc)
        order = np.argsort(dists)
        ranks = np.empty_like(order)
        ranks[order] = np.arange(len(order))
        rho, _ = spearmanr(base_ranks, ranks)
        mc_rhos.append(rho)
        mc_top1[synth_names[order[0]]] += 1

    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))

    # Panel A: Heatmap
    pert_labels = [r['label'] for r in sens_results]
    rank_data = np.zeros((len(pert_labels), len(synth_names)))
    for i, r in enumerate(sens_results):
        for j, name in enumerate(synth_names):
            rank_data[i, j] = r['ranks'][name]

    ax = axes[0]
    sns.heatmap(rank_data, annot=True, fmt='.0f', cmap='RdYlGn_r',
                xticklabels=synth_names, yticklabels=pert_labels,
                ax=ax, vmin=1, vmax=len(synth_names),
                linewidths=0.5, cbar_kws={'label': 'Rank'})
    ax.set_title('(A) Ranking under each perturbation', fontweight='bold')
    ax.tick_params(axis='x', rotation=45)

    # Panel B: Monte Carlo rho histogram
    ax = axes[1]
    ax.hist(mc_rhos, bins=30, color='steelblue', edgecolor='white', alpha=0.8)
    ax.axvline(np.median(mc_rhos), color='red', lw=2, ls='--',
               label=f'Median={np.median(mc_rhos):.3f}')
    ax.axvline(0.8, color='orange', lw=1.5, ls=':', label='ρ=0.8')
    ax.set_xlabel('Spearman ρ vs base ranking')
    ax.set_ylabel('Frequency')
    ax.set_title(f'(B) Monte Carlo: {N_MC} Dirichlet weight sets', fontweight='bold')
    ax.legend(fontsize=9)

    # Panel C: Top-1 frequency
    ax = axes[2]
    names_sorted = [n for n, _ in mc_top1.most_common()]
    counts_sorted = [mc_top1[n] for n in names_sorted]
    colors = [COLOR_MAP.get(n, '#999999') for n in names_sorted]
    ax.barh(range(len(names_sorted)), counts_sorted, color=colors)
    ax.set_yticks(range(len(names_sorted)))
    ax.set_yticklabels(names_sorted)
    ax.set_xlabel(f'Times ranked #1 (out of {N_MC})')
    ax.set_title('(C) Which model wins with random weights?', fontweight='bold')
    ax.invert_yaxis()
    for i, (n, c) in enumerate(zip(names_sorted, counts_sorted)):
        ax.text(c + 5, i, f'{c/N_MC*100:.0f}%', va='center', fontsize=9)

    fig.suptitle('Sensitivity of the ranking to distance weights',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    out = os.path.join(IMG_DIR, 'sensibilidad_pesos.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'  Saved: {out}')


# ============================================================
# FIGURE 8: Semantic enrichment heatmap
# ============================================================
def fig8_semantic():
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(ENRICHMENT, annot=True, fmt='.2f', cmap='RdYlGn', center=1.0,
                ax=ax, xticklabels=SEM_SECTIONS, yticklabels=SEM_CATEGORIES,
                cbar_kws={'label': 'Enrichment (ratio)'})
    ax.set_title('Semantic enrichment: category × Voynich section', fontsize=13)
    ax.set_ylabel('Semantic category')
    ax.set_xlabel('Voynich section')

    for sec_j, cat_i in EXPECTED:
        ax.add_patch(plt.Rectangle((sec_j, cat_i), 1, 1, fill=False,
                                   edgecolor='blue', linewidth=2.5, linestyle='--'))

    ax.text(0.02, -0.15, 'Blue boxes = expected correspondence',
            transform=ax.transAxes, fontsize=9, color='blue')
    plt.tight_layout()
    out = os.path.join(IMG_DIR, 'semantic_enrichment_heatmap.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'  Saved: {out}')


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print('Generating English figures for DSH paper...')
    print(f'Output: {IMG_DIR}/')
    print()

    fig1_entropy()
    fig2_mi()
    fig3_fingerprint()
    fig4_distributions()
    fig5_synthetic_curves()
    fig6_radar()
    fig7_sensitivity()
    fig8_semantic()

    print('\nDone! All figures saved to images/ directory.')

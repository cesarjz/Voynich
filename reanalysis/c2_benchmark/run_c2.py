"""Known-plaintext benchmark: run Models 1 and 7 on enciphered Hebrew.

Functions and classes are executed verbatim from the published notebooks
(07_compositional, 14_neural_v2); only the top-level glue is re-written here,
keeping every seed, hyper-parameter and selection rule of the original cells.
The difference is scheduling: all EM seeds and MCMC chains of all twelve runs
go to one CPU process pool (fork, one torch thread per worker), as in nb 25/26.

Usage:
  python cipher.py           # once: plaintexts + ciphers
  python run_c2.py           # trains LMs if needed, then runs everything
  python run_c2.py --only M7:torah_holdout:L0 --workers 15
  python spec_data.py && python run_c2.py --spec   # specificity control

Every finished job is written to results/jobs/; re-running skips them.
"""
import argparse
import contextlib
import copy
import io
import json
import math
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import multiprocessing as mp

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / 'reeval'))
import corpora as C  # noqa: E402
import ngram as N  # noqa: E402
from nbcode import _notebook_source  # noqa: E402
import ast  # noqa: E402

DATA, CACHE, JOBS, LOGS = HERE / 'data', HERE / 'cache', HERE / 'results' / 'jobs', HERE / 'logs'
RESULTS = HERE / 'results'
FREE = False  # --free: no C/V roles (all glyphs '?') and w_gram=0; the LM is the only signal
PLAINS, LEVELS = ('torah_holdout', 'moreh'), ('L0', 'L1', 'L2')
# --voynich (implies --free): Voynich + controls from voynich_data.py, decoded with the full-Torah
# LM of the Moreh condition so that realism indices are comparable with moreh L0-L2.
VOYNICH_RUNS = ('voy:STA', 'voy:EVA', 'voy:SHUF', 'ctl:GEEZ', 'ctl:JARAB')
LM_OF = {'voy': 'moreh', 'ctl': 'moreh', 'voyg': 'gkn', 'voygc': 'gkc'}
# --geez (implies --free): same design with Ge'ez (TraCES v1, geez_data.py): Kebra Nagast L0 as the
# known-plaintext control, the Voynich inputs decoded against an LM trained on the other ten texts.
# gkc/voygc: the same with every fidel sign reduced to its consonant (vowel order dropped, ~37 signs).
# --spec (implies --free): specificity control (spec_data.py), non-Hebrew structured texts vs the full-Torah LM.
SPEC_RUNS = ('ctl:LATIN', 'ctl:LATL1', 'ctl:GEEZN', 'ctl:SELF', 'ctl:NAIB')
GEEZ_RUNS = ('gkn:L0', 'voyg:STA', 'voyg:EVA', 'voyg:SHUF', 'gkc:L0', 'voygc:STA', 'voygc:EVA', 'voygc:SHUF')


def lm_name(plain):
    return LM_OF.get(plain, plain)


# ── Verbatim notebook definitions ────────────────────────────────────

SEGMENT = ['construir_matriz_transicion_intrapalabra', 'segmentar_silabas_tp', 'catalogar_silabas',
           'clasificar_silabas_posicionalmente', 'syls_to_words', 'clasificar_glifos']
NB14 = SEGMENT + [
    'HEBREW_PREFIXES', 'HEBREW_SUFFIXES', 'HEBREW_ROOT_CONSONANTS', 'build_glyph_grammar_roles',
    'CharDataset', 'NeuralCharLM', 'GlyphMappingState', 'init_frequency_mapping',
    'build_glyph_word_index', 'score_positional', 'score_grammar', 'score_entropy',
    'score_neural_lm_batch', 'score_cardinality', 'score_total_neural', 'score_total_incremental',
    'propose_change_hard_k', 'HEBREW_CONSONANTS_SET', 'HEBREW_MATRES', 'HEBREW_ROOTS',
    'extract_skeleton_deterministic', 'count_roots_quick', 'calibrate_mcmc_temp']
NB07 = SEGMENT + ['CharLM', 'GlyphMappingState', 'score_char_lm', 'score_positional',
                  'score_total_comp', 'score_total_comp_fast', 'init_frequency_mapping',
                  'em_glyph_decipher', 'mcmc_glyph_refine']


def load_nb(nb_name, names, extra):
    """Like nbcode.load_defs, with extra globals (torch, DEVICE, ...) in the namespace."""
    tree = ast.parse(_notebook_source(nb_name))
    found = {}
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names:
            found[n.name] = n
        elif isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id in names:
                    found[t.id] = n
    missing = set(names) - set(found)
    if missing:
        raise KeyError(f'{nb_name}: not found: {sorted(missing)}')
    ns = {'re': __import__('re'), 'json': json, 'math': math, 'np': np, 'copy': copy,
          'Counter': Counter, 'defaultdict': defaultdict, **extra}
    for name in names:
        exec(compile(ast.Module([found[name]], []), f'{nb_name}:{name}', 'exec'), ns)
    return ns


def torch_ns(device):
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset
    return {'torch': torch, 'nn': nn, 'Dataset': Dataset, 'DEVICE': torch.device(device)}


# ── Neural LM training (nb 14 cell 5), run in a subprocess ───────────

def lm_words(plain, n):
    return C.subsample(json.loads((DATA / f'{lm_name(plain)}_lm_corpus.json').read_text(encoding='utf-8')), n)


def train_lm(plain):
    import torch
    import torch.optim as optim
    from torch.utils.data import DataLoader
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    ns = load_nb('14_neural_v2.ipynb', ['CharDataset', 'NeuralCharLM'], torch_ns(dev))
    hebrew_words = lm_words(plain, C_N_WORDS)

    all_chars_heb = sorted(set(c for w in hebrew_words for c in w))
    char_vocab = ['<pad>', '<w>', '</w>', '<unk>'] + all_chars_heb
    char2idx = {c: i for i, c in enumerate(char_vocab)}
    idx2char = {i: c for c, i in char2idx.items()}

    rng_split = np.random.default_rng(42)
    n_val = int(0.2 * len(hebrew_words))
    val_idx = set(rng_split.permutation(len(hebrew_words))[:n_val])
    train_words = [hebrew_words[i] for i in range(len(hebrew_words)) if i not in val_idx]
    val_words = [hebrew_words[i] for i in range(len(hebrew_words)) if i in val_idx]
    train_loader = DataLoader(ns['CharDataset'](train_words, char2idx), batch_size=256, shuffle=True)
    val_loader = DataLoader(ns['CharDataset'](val_words, char2idx), batch_size=256, shuffle=False)

    neural_lm = ns['NeuralCharLM'](len(char_vocab), embed_dim=32, hidden_dim=192,
                                   n_layers=2, dropout=0.2).to(dev)
    optimizer = optim.AdamW(neural_lm.parameters(), lr=2e-3, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=30)
    criterion = torch.nn.CrossEntropyLoss(ignore_index=char2idx['<pad>'])
    best_val_loss, patience_counter, best_state_dict = float('inf'), 0, None
    for epoch in range(30):
        neural_lm.train()
        for ctx_b, tgt_b in train_loader:
            ctx_b, tgt_b = ctx_b.to(dev), tgt_b.to(dev)
            optimizer.zero_grad()
            logits, _ = neural_lm(ctx_b)
            loss = criterion(logits[:, -1, :], tgt_b)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(neural_lm.parameters(), 1.0)
            optimizer.step()
        neural_lm.eval()
        val_loss, nb = 0.0, 0
        with torch.no_grad():
            for ctx_b, tgt_b in val_loader:
                logits, _ = neural_lm(ctx_b.to(dev))
                val_loss += criterion(logits[:, -1, :], tgt_b.to(dev)).item()
                nb += 1
        val_loss /= max(nb, 1)
        scheduler.step()
        print(f'  [{plain}] epoch {epoch + 1}: val_loss={val_loss:.4f}', flush=True)
        if val_loss < best_val_loss - 1e-4:
            best_val_loss, patience_counter = val_loss, 0
            best_state_dict = {k: v.detach().cpu().clone() for k, v in neural_lm.state_dict().items()}
        else:
            patience_counter += 1
            if patience_counter >= 5:
                break
    CACHE.mkdir(exist_ok=True)
    torch.save({'state_dict': best_state_dict, 'char2idx': char2idx, 'idx2char': idx2char,
                'best_val_loss': best_val_loss}, CACHE / f'lm_{plain}.pt')


C_N_WORDS = 37087


# ── Per-run context (built in the parent, inherited by forked workers) ──

CTX = {}


def glyph_setup(ns, palabras):
    """nb 07/14 cell 2-3: TP-P20 segmentation and positional glyph roles."""
    VOCAB = sorted(set(g for p in palabras for g in p))
    _, M_prob, tokens_tr, index_tr = ns['construir_matriz_transicion_intrapalabra'](palabras)
    silabas, _, _ = ns['segmentar_silabas_tp'](palabras, M_prob, tokens_tr, index_tr, threshold_percentile=20)
    clase_silaba, _ = ns['clasificar_silabas_posicionalmente'](silabas, min_freq=5)
    words_syl = ns['syls_to_words'](silabas)
    glyph_role, glyph_stats = ns['clasificar_glifos'](palabras, words_syl, clase_silaba, VOCAB)
    return VOCAB, glyph_role, glyph_stats


def build_ctx(model, plain, level):
    d = json.loads((DATA / f'{plain}_{level}.json').read_text(encoding='utf-8'))
    palabras = d['cipher_words']
    hebrew_words = lm_words(plain, len(palabras))
    target_chars = sorted(set(c for w in hebrew_words for c in w))
    char_role = {c: 'V' if c in set('אהוי') else 'C' for c in target_chars}
    ctx = {'palabras': palabras, 'key': d['key'], 'plain_words': d['plain_words'],
           'hebrew_words': hebrew_words, 'target_chars': target_chars, 'char_role': char_role}
    if model == 'M1':
        ns = load_nb('07_compositional.ipynb', NB07, {})
        VOCAB, glyph_role, _ = glyph_setup(ns, palabras)
        if FREE:
            glyph_role = {}
        clm = ns['CharLM'](order=3)
        clm.fit(hebrew_words)
        ctx.update(ns=ns, VOCAB=VOCAB, glyph_role=glyph_role, lm=clm)
    else:
        import torch
        ns = load_nb('14_neural_v2.ipynb', NB14, {**torch_ns('cpu'), 'K_MIN': 20})
        VOCAB, glyph_role, glyph_stats = glyph_setup(ns, palabras)
        _, anchors = ns['build_glyph_grammar_roles'](palabras, glyph_stats, VOCAB)
        if FREE:
            glyph_role = {}
        ck = torch.load(CACHE / f'lm_{lm_name(plain)}.pt', weights_only=False)
        lm = ns['NeuralCharLM'](len(ck['char2idx']), embed_dim=32, hidden_dim=192, n_layers=2, dropout=0.2)
        lm.load_state_dict(ck['state_dict'])
        lm.char2idx, lm.idx2char = ck['char2idx'], ck['idx2char']
        lm.eval()
        # nb 14 cell 7: EM sample and base mapping (cell 10 draws the same sample for MCMC)
        rng_sample = np.random.default_rng(42)
        idx_em = rng_sample.choice(len(palabras), size=3000, replace=False)
        words_em = [palabras[i] for i in idx_em]
        base_mapping = ns['init_frequency_mapping'](palabras, VOCAB, target_chars, hebrew_words,
                                                    glyph_role, char_role)
        ctx.update(ns=ns, VOCAB=VOCAB, glyph_role=glyph_role, anchors=anchors, lm=lm,
                   words_em=words_em, widx_em=ns['build_glyph_word_index'](words_em),
                   base_mapping=base_mapping)
    return ctx


# ── Jobs ─────────────────────────────────────────────────────────────

M7_KW = dict(w_gram=2.0, w_card=0.5, K_max=20)          # nb 14 cell 7 SCORE_KW
M7_A = dict(n_seeds=20, T=3.0)
M7_B = dict(T_values=(1.5, 2.0), n_seeds=5, K_min=20)
M7_EM = dict(iters=2000, patience=100, proposals=200)
M7_MCMC = dict(n_iter=20000, burn_in=5000, seeds=(42, 137, 256, 999))
M1_MCMC_SEEDS = (42, 137, 256, 999)


def m1_em(run):
    c = CTX[run]
    ns = c['ns']
    state = ns['GlyphMappingState'](c['VOCAB'], c['target_chars'], c['glyph_role'], c['char_role'])
    state.set_mapping(ns['init_frequency_mapping'](c['palabras'], c['VOCAB'], c['target_chars'],
                                                   c['hebrew_words'], c['glyph_role'], c['char_role']))
    best, scores = ns['em_glyph_decipher'](c['palabras'], c['lm'], c['glyph_role'], c['char_role'], state,
                                           n_iter=50, patience=10, sample_size=3000, changes_per_iter=200)
    return {'mapping': best.mapping, 'score': scores[-1], 'iters': len(scores) - 1}


def m1_chain(run, chain, init_mapping):
    c = CTX[run]
    ns = c['ns']
    state = ns['GlyphMappingState'](c['VOCAB'], c['target_chars'], c['glyph_role'], c['char_role'])
    state.set_mapping(init_mapping)
    best, scores, _, _, accept = ns['mcmc_glyph_refine'](
        state, c['palabras'], c['lm'], c['glyph_role'], c['char_role'],
        n_iter=15000, seed=M1_MCMC_SEEDS[chain], thin=5, adaptive=True, target_accept=0.35,
        calibration_samples=300, T_ratio=100, sample_size=3000)
    return {'mapping': best.mapping, 'best_score': max(scores), 'accept': accept}


def _m7_init(c, rng, scramble):
    """nb 14 cells 7-8: frequency mapping + 1/3 scramble, or fully random C/V mapping."""
    ns, VOCAB, tc, gr, cr = c['ns'], c['VOCAB'], c['target_chars'], c['glyph_role'], c['char_role']
    state = ns['GlyphMappingState'](VOCAB, tc, gr, cr)
    if scramble:
        mapping_init = dict(c['base_mapping'])
        glyphs_to_scramble = rng.choice(VOCAB, size=max(1, len(VOCAB) // 3), replace=False)
        targets = glyphs_to_scramble
    else:
        mapping_init = {}
        targets = VOCAB
    for g in targets:
        role = gr.get(g, '?')
        candidates = [ch for ch in tc if cr.get(ch) == role] if role in ('C', 'V') else tc
        mapping_init[g] = rng.choice(candidates)
    state.set_mapping(mapping_init)
    return state


def m7_em(run, strategy, T, seed_idx):
    """One seed of Strategy A (multi-seed, T=3) or B (hard-K, low T), nb 14 cells 7-8."""
    c = CTX[run]
    ns = c['ns']
    if strategy == 'A':
        rng = np.random.default_rng(42 + seed_idx * 137)
        state = _m7_init(c, rng, scramble=seed_idx < 10)
    else:
        rng = np.random.default_rng(1000 + seed_idx * 137 + int(T * 100))
        state = _m7_init(c, rng, scramble=True)
    args = (c['words_em'], c['lm'], T, c['glyph_role'], c['char_role'], c['anchors'])
    best_score, best_lps = ns['score_total_neural'](state, *args, **M7_KW)
    best_state, no_improve = state, 0
    t0 = time.time()
    for it in range(M7_EM['iters']):
        improved = False
        for _ in range(M7_EM['proposals']):
            if strategy == 'A':
                proposal, changed = best_state.propose_change_tracked(rng, constrained=True)
            else:
                proposal, changed = ns['propose_change_hard_k'](best_state, rng, K_min=M7_B['K_min'],
                                                                constrained=True)
                if proposal is None:
                    continue
            ps, plps = ns['score_total_incremental'](proposal, changed, *args, c['widx_em'], best_lps, **M7_KW)
            if ps > best_score:
                best_state, best_score, best_lps, improved = proposal, ps, plps, True
        if not improved:
            no_improve += 1
            if no_improve >= M7_EM['patience']:
                break
        else:
            no_improve = 0
    roots, n_matches = ns['count_roots_quick'](best_state.mapping, c['palabras'])
    return {'strategy': strategy, 'T': T, 'seed': seed_idx, 'mapping': best_state.mapping,
            'score': best_score, 'K_eff': len(set(best_state.mapping.values())),
            'grammar': ns['score_grammar'](best_state, c['anchors']), 'n_roots': len(roots),
            'iter_converged': it + 1, 'elapsed': time.time() - t0}


def m7_select(ems):
    """nb 14 cell 9: K_eff/grammar/score filter, then sort by (roots, score)."""
    med = np.median([r['score'] for r in ems])
    g_min = -2.0 if FREE else 0.8  # grammar is not optimised in the free variant
    cand = [r for r in ems if r['K_eff'] >= 20 and r['grammar'] >= g_min and r['score'] >= med]
    if not cand:
        cand = [r for r in ems if r['K_eff'] >= 15 and r['grammar'] >= 0.5 and r['score'] >= med]
    if not cand:
        cand = list(ems)
    cand.sort(key=lambda r: (r['n_roots'], r['score']), reverse=True)
    return cand[0]


def m7_calibrate(run, best):
    c = CTX[run]
    ns = c['ns']
    state = ns['GlyphMappingState'](c['VOCAB'], c['target_chars'], c['glyph_role'], c['char_role'])
    state.set_mapping(best['mapping'])
    t0, t1 = ns['calibrate_mcmc_temp'](state, c['words_em'], c['lm'], best['T'], c['glyph_role'],
                                       c['char_role'], c['anchors'], c['widx_em'],
                                       use_hard_k=best['strategy'] == 'B', **M7_KW)
    return {'T_start': t0, 'T_end': t1}


def m7_chain(run, chain, best, cal):
    """One chain of nb 14 cell 10."""
    c = CTX[run]
    ns = c['ns']
    T_mcmc, hard_k = best['T'], best['strategy'] == 'B'
    Ts, Te = cal['T_start'], cal['T_end']
    rng = np.random.default_rng(M7_MCMC['seeds'][chain])
    current = ns['GlyphMappingState'](c['VOCAB'], c['target_chars'], c['glyph_role'], c['char_role'])
    current.set_mapping(dict(best['mapping']))
    args = (c['words_em'], c['lm'], T_mcmc, c['glyph_role'], c['char_role'], c['anchors'])
    cur_score, cur_lps = ns['score_total_neural'](current, *args, **M7_KW)
    best_ch, best_ch_score, accepted = current, cur_score, 0
    n_iter, burn = M7_MCMC['n_iter'], M7_MCMC['burn_in']
    for it in range(n_iter):
        if it < burn:
            frac = it / burn
            T_ann = Ts * (1 - frac) + (Ts * 0.5) * frac
        else:
            frac = (it - burn) / max(n_iter - burn - 1, 1)
            T_ann = (Ts * 0.5) * ((Te / (Ts * 0.5)) ** frac)
        if hard_k:
            proposal, changed = ns['propose_change_hard_k'](current, rng, K_min=M7_B['K_min'])
            if proposal is None:
                continue
        else:
            proposal, changed = current.propose_change_tracked(rng, constrained=True)
        ps, plps = ns['score_total_incremental'](proposal, changed, *args, c['widx_em'], cur_lps, **M7_KW)
        delta = ps - cur_score
        if delta > 0 or rng.random() < math.exp(delta / max(T_ann, 1e-10)):
            current, cur_score, cur_lps = proposal, ps, plps
            accepted += 1
            if cur_score > best_ch_score:
                best_ch, best_ch_score = current, cur_score
    return {'mapping': best_ch.mapping, 'best_score': best_ch_score, 'accept': accepted / n_iter}


def run_job(job_id, fn_name, args):
    """Worker entry point: run, log stdout, checkpoint."""
    import torch
    torch.set_num_threads(1)
    out = JOBS / f'{job_id}.json'
    buf = io.StringIO()
    t0 = time.time()
    with contextlib.redirect_stdout(buf):
        res = globals()[fn_name](*args)
    res['wall'] = time.time() - t0
    (LOGS / f'{job_id}.log').write_text(buf.getvalue(), encoding='utf-8')
    out.write_text(json.dumps(res, ensure_ascii=False), encoding='utf-8')
    return job_id, res


def load_job(job_id):
    p = JOBS / f'{job_id}.json'
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None


def run_pool(jobs, workers):
    """jobs: list of (job_id, fn_name, args). Returns {job_id: result}, skipping finished ones."""
    done = {j: load_job(j) for j, _, _ in jobs}
    todo = [(j, f, a) for j, f, a in jobs if done[j] is None]
    if todo:
        print(f'  {len(todo)} jobs to run ({len(jobs) - len(todo)} cached) on {workers} workers', flush=True)
        t0 = time.time()
        with ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context('fork')) as ex:
            futs = [ex.submit(run_job, j, f, a) for j, f, a in todo]
            for k, fut in enumerate(as_completed(futs), 1):
                j, res = fut.result()
                done[j] = res
                print(f'  [{k}/{len(todo)}] {j} ({res["wall"]:.0f}s, elapsed {time.time() - t0:.0f}s)', flush=True)
    return done


# ── Evaluation ───────────────────────────────────────────────────────

def evaluate(run, mapping, B=1000):
    c = CTX[run]
    words, key = c['palabras'], c['key']
    toks = [s for w in words for s in w]
    if key is not None:
        acc = float(np.mean([mapping.get(s) == key[s] for s in toks]))
        sym_ok = sum(1 for s in set(toks) if mapping.get(s) == key[s])
    else:
        acc, sym_ok, key = float('nan'), -1, {}

    vocab = sorted(set(toks))
    gid = {s: i for i, s in enumerate(vocab)}
    keys = [[gid[s] for s in w] for w in words]
    target_full = json.loads((DATA / f"{lm_name(run.split(':')[1])}_lm_corpus.json").read_text(encoding='utf-8'))
    target = C.subsample(target_full, len(words))
    units = sorted({(v,) for v in mapping.values()} | {(v,) for v in key.values()})
    uid = {u: i for i, u in enumerate(units)}
    enc = N.Encoder({ch for w in target_full for ch in w} | {u[0] for u in units})
    corpus = N.DecodedCorpus(keys, units, enc)
    ref = N.corpus_dist(target, enc)
    k2u = np.array([uid[(mapping[s],)] for s in vocab], dtype=np.int64)
    real, null, p = N.permutation_test(corpus, k2u, [np.arange(len(vocab))], ref, B=B, seed=42)
    chosen = set(map(id, target))
    rest = [w for w in target_full if id(w) not in chosen]
    assert len(rest) == len(target_full) - len(target), 'ceiling sample not disjoint (target not drawn from target_full)'
    ceiling = N.jsd(N.corpus_dist(C.subsample(rest, len(target), seed=7), enc), ref)
    oracle = N.jsd(N.corpus_dist(c['plain_words'], enc), ref) if c['plain_words'] else float('nan')
    nm = float(null.mean())

    ns14 = CTX_ROOTS
    roots, _ = ns14['count_roots_quick'](mapping, words)
    roots_oracle, _ = ns14['count_roots_quick'](key, words) if key else ([], 0)
    return {'token_accuracy': acc, 'symbols_correct': sym_ok, 'symbols_used': len(vocab),
            'K_eff': len(set(mapping.values())),
            'jsd_real': real, 'jsd_null_mean': nm, 'jsd_null_sd': float(null.std(ddof=1)),
            'jsd_ceiling': ceiling, 'jsd_oracle': oracle,
            'realism_index': (nm - real) / (nm - ceiling), 'realism_index_oracle': (nm - oracle) / (nm - ceiling),
            'p_value': p, 'n_roots': len(roots), 'roots': sorted(roots), 'n_roots_oracle': len(roots_oracle),
            'decoded_sample': [''.join(mapping.get(s, '?') for s in w) for w in words[:15]],
            'plain_sample': [''.join(w) for w in (c['plain_words'] or [])[:15]]}


CTX_ROOTS = None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--train-lm')
    ap.add_argument('--only', nargs='*', help='run ids like M7:moreh:L1')
    ap.add_argument('--workers', type=int, default=15)
    ap.add_argument('--B', type=int, default=1000)
    ap.add_argument('--free', action='store_true')
    ap.add_argument('--voynich', action='store_true')
    ap.add_argument('--geez', action='store_true')
    ap.add_argument('--spec', action='store_true')
    args = ap.parse_args()
    global FREE, JOBS, LOGS, RESULTS
    if args.free or args.voynich or args.geez or args.spec:
        FREE = True
        M7_KW['w_gram'] = 0.0
        sub = 'voynich' if args.voynich else 'geez' if args.geez else 'spec' if args.spec else 'free'
        RESULTS = HERE / f'results_{sub}'
        JOBS, LOGS = RESULTS / 'jobs', HERE / f'logs_{sub}'

    if args.train_lm:
        train_lm(args.train_lm)
        return

    for d in (CACHE, JOBS, LOGS):
        d.mkdir(parents=True, exist_ok=True)
    runs = [f'{m}:{p}:{lv}' for m in ('M1', 'M7') for p in PLAINS for lv in LEVELS]
    if args.voynich or args.geez or args.spec:
        sel = VOYNICH_RUNS if args.voynich else GEEZ_RUNS if args.geez else SPEC_RUNS
        runs = [f'{m}:{pl}' for m in ('M1', 'M7') for pl in sel]
    if args.only:
        runs = [r for r in runs if r in args.only]

    # LMs are trained in a separate process so this one never initialises CUDA or OpenMP before forking.
    for p in sorted({lm_name(r.split(':')[1]) for r in runs if r.startswith('M7')}):
        if not (CACHE / f'lm_{p}.pt').exists():
            print(f'Training neural LM for {p}...', flush=True)
            subprocess.run([sys.executable, __file__, '--train-lm', p], check=True)

    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    import torch
    torch.set_num_threads(1)
    global CTX_ROOTS
    CTX_ROOTS = load_nb('14_neural_v2.ipynb', ['HEBREW_CONSONANTS_SET', 'HEBREW_MATRES', 'HEBREW_ROOTS',
                                               'extract_skeleton_deterministic', 'count_roots_quick'], {})
    for r in runs:
        t0 = time.time()
        CTX[r] = build_ctx(*r.split(':'))
        print(f'context {r}: {len(CTX[r]["VOCAB"])} symbols, '
              f'roles {dict(Counter(CTX[r]["glyph_role"].values()))} [{time.time() - t0:.0f}s]', flush=True)

    m1 = [r for r in runs if r.startswith('M1')]
    m7 = [r for r in runs if r.startswith('M7')]
    tag = lambda r: r.replace(':', '_')  # noqa: E731

    print('\nStage 1: EM', flush=True)
    jobs = [(f'{tag(r)}_em', 'm1_em', (r,)) for r in m1]
    for r in m7:
        jobs += [(f'{tag(r)}_A{s:02d}', 'm7_em', (r, 'A', M7_A['T'], s)) for s in range(M7_A['n_seeds'])]
        jobs += [(f'{tag(r)}_B{T}_{s}', 'm7_em', (r, 'B', T, s))
                 for T in M7_B['T_values'] for s in range(M7_B['n_seeds'])]
    em = run_pool(jobs, args.workers)

    print('\nStage 2: selection + MCMC calibration', flush=True)
    best7 = {r: m7_select([v for k, v in em.items() if k.startswith(tag(r) + '_') and not k.endswith('_em')])
             for r in m7}
    cal = run_pool([(f'{tag(r)}_cal', 'm7_calibrate', (r, best7[r])) for r in m7], args.workers)

    print('\nStage 3: MCMC chains', flush=True)
    jobs = [(f'{tag(r)}_m1c{i}', 'm1_chain', (r, i, em[f'{tag(r)}_em']['mapping'])) for r in m1 for i in range(4)]
    jobs += [(f'{tag(r)}_m7c{i}', 'm7_chain', (r, i, best7[r], cal[f'{tag(r)}_cal'])) for r in m7 for i in range(4)]
    ch = run_pool(jobs, args.workers)

    print('\nStage 4: evaluation', flush=True)
    summary = []
    for r in runs:
        chains = [ch[k] for k in ch if k.startswith(tag(r) + '_m')]
        final = max(chains, key=lambda x: x['best_score'])['mapping']
        em_map = em[f'{tag(r)}_em']['mapping'] if r.startswith('M1') else best7[r]['mapping']
        row = {'run': r, 'final': evaluate(r, final, args.B), 'em': evaluate(r, em_map, B=200)}
        summary.append(row)
        f = row['final']
        print(f"{r:20s} acc={f['token_accuracy']:.3f} sym={f['symbols_correct']}/{f['symbols_used']} "
              f"RI={f['realism_index']:+.3f} (oracle {f['realism_index_oracle']:+.3f}) p={f['p_value']:.4f} "
              f"roots={f['n_roots']} (oracle {f['n_roots_oracle']})", flush=True)
    (RESULTS / 'c2_summary.json').write_text(json.dumps(summary, indent=1, ensure_ascii=False),
                                                      encoding='utf-8')


if __name__ == '__main__':
    main()

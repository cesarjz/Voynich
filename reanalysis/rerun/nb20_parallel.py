"""Parallel runner for nb20 (Model 12, syllable-to-syllable) — R1 capacity control on shuffled glyphs (2026-11-11).

Why: the notebook runs 20 EM restarts + 4 MCMC chains serially on one CPU core. With shuffled input the Voynich has
16,775 syllable types (real text: 2,923), and the serial run did not finish in 10.5 h.

What is identical to the notebook: cells 1-3, 5, 8-10 are exec'd verbatim from 20_syllable_to_syllable_R1shuf.ipynb;
cell 4 (LSTM) is exec'd verbatim in the main process, its best state is saved and loaded by every worker; the EM and
MCMC loops below are copies of cells 6 and 7 with the same per-job seeds (default_rng(42 + seed*137 + int(T*1000)),
default_rng(42 + chain*999)). The only change inside the loops: the "keep rare syllable fallbacks" loop over
VOCAB_SYL_V after each proposal is dropped, because it is a no-op (every mapping already holds every key; propose_change
copies the dict and reassigns one functional syllable) and it uses no random numbers. `--check` verifies this by running
seed 0 for a few iterations with and without the loop.

Caveat (also true of the notebook): torch is not seeded, so the LSTM differs from run to run; all workers share one LSTM.

Run (from rerun/):  nice -n 19 python -u nb20_parallel.py --workers 8 > nb20_parallel.log 2>&1
Check:              python -u nb20_parallel.py --check
Outputs: syl2syl_shuf_resultados.json, syl2syl_shuf_mapping.json (as the notebook), plus nb20_parallel_lm.pt and
nb20_parallel_em.json (per-seed EM summary).
"""
import argparse
import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
NB = HERE / '20_syllable_to_syllable_R1shuf.ipynb'
LM_PATH = HERE / 'nb20_parallel_lm.pt'


def cells():
    d = json.loads(NB.read_text(encoding='utf-8'))
    return [''.join(c['source']) for c in d['cells'] if c['cell_type'] == 'code']


def setup(train_lm):
    """Exec notebook cells 1-5 into a namespace. train_lm=False: build the LSTM and load the saved state."""
    import torch
    cs = cells()
    g = {'__name__': 'nb20'}
    for c in cs[:3]:                       # cells 1-3: imports, Voynich (shuffled), Hebrew
        exec(c, g)
    c4 = cs[3]
    if train_lm:
        exec(c4, g)
        torch.save(g['best_model_state'], LM_PATH)
        json.dump({'best_val_loss': g['best_val_loss']}, open(LM_PATH.with_suffix('.json'), 'w'))
    else:
        head = c4.split('# Train/val split')[0]          # classes + char vocab
        exec(head, g)
        exec("neural_lm = NeuralCharLM(len(char_vocab), embed_dim=32, hidden_dim=192, n_layers=2, dropout=0.2).to(DEVICE)\n"
             "neural_lm.char2idx = char2idx\nneural_lm.idx2char = idx2char\n", g)
        g['neural_lm'].load_state_dict(torch.load(LM_PATH))
        g['neural_lm'] = g['neural_lm'].to(g['DEVICE'])
        g['best_val_loss'] = json.load(open(LM_PATH.with_suffix('.json')))['best_val_loss']
    exec(cs[4], g)                         # cell 5: mapping state + scoring
    # cell 6 preamble (constants, EM subsample, index, base mapping) — everything before the seed loop
    exec(cs[5].split('all_em_results = []')[0], g)
    return g


G = None


def _init_worker(smoke=False):
    global G, SMOKE
    SMOKE = smoke
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        G = setup(train_lm=False)


SMOKE = False


def em_job(args, g=None, keep_noop_loop=False, em_iters=None):
    """Copy of the cell-6 loop body for one (T, seed_idx)."""
    T, seed_idx = args
    g = g or G
    np = g['np']
    VF, HF, VA = g['VOCAB_SYL_V_FUNC'], g['VOCAB_SYL_H_FUNC'], g['VOCAB_SYL_V']
    words_em, lm, KW, idx_em = g['words_em'], g['neural_lm'], g['SCORE_KW'], g['syl_word_idx_em']
    EM_ITERS = em_iters or (2 if SMOKE else g['EM_ITERS'])
    rng = np.random.default_rng(42 + seed_idx * 137 + int(T * 1000))
    state = g['SylMappingState'](VF, HF)
    if seed_idx < 5:
        mapping_init = dict(g['base_mapping'])
        n_scramble = max(1, len(VF) // 3)
        scramble_idx = rng.choice(len(VF), size=n_scramble, replace=False)
        for si in scramble_idx:
            mapping_init[VF[si]] = HF[rng.integers(len(HF))]
        state.set_mapping(mapping_init)
    else:
        state.set_mapping({s: HF[rng.integers(len(HF))] for s in VF})
    for syl in VA:
        if syl not in state.mapping:
            state.mapping[syl] = HF[0]
    best_score, best_word_lps = g['score_total_syl'](state, words_em, lm, T, **KW)
    best_state, no_improve = state, 0
    t0 = time.time()
    for it in range(EM_ITERS):
        improved = False
        for _ in range(g['PROPOSALS_PER_ITER']):
            proposal, changed_syl = best_state.propose_change(rng)
            if keep_noop_loop:
                for syl in VA:
                    if syl not in proposal.mapping:
                        proposal.mapping[syl] = HF[0]
            prop_score, prop_lps = g['score_incremental_syl'](
                proposal, changed_syl, words_em, lm, T, idx_em, best_word_lps, **KW)
            if prop_score > best_score:
                best_state, best_score, best_word_lps, improved = proposal, prop_score, prop_lps, True
        if not improved:
            no_improve += 1
            if no_improve >= g['EM_PATIENCE']:
                break
        else:
            no_improve = 0
    elapsed = time.time() - t0
    K_eff = len(set(best_state.mapping.values()))
    print(f'  [EM] T={T} seed {seed_idx:2d} [{"freq+scramble" if seed_idx < 5 else "random":13s}]: '
          f'score={best_score:.4f}, K={K_eff:3d}, iter={it+1:4d}, {elapsed:.0f}s', flush=True)
    return {'seed': seed_idx, 'T': T, 'score': best_score, 'K_eff': K_eff, 'elapsed': elapsed,
            'mapping': best_state.mapping, 'word_lps': best_word_lps, 'iter_converged': it + 1}


def mcmc_job(args):
    """Copy of the cell-7 loop body for one chain. Stored mappings keep only functional syllables (the others are the
    fixed fallback HF[0] throughout, and cell 8 only reads functional ones); cell-7 tail re-adds the fallback."""
    chain_id, best_mapping, T_mcmc = args
    g = G
    np = g['np']
    VF, HF, VA = g['VOCAB_SYL_V_FUNC'], g['VOCAB_SYL_H_FUNC'], g['VOCAB_SYL_V']
    words_em, lm, KW, idx_em = g['words_em'], g['neural_lm'], g['SCORE_KW'], g['syl_word_idx_em']
    N_ITER, THIN = (600 if SMOKE else 15000), 5
    rng = np.random.default_rng(42 + chain_id * 999)
    state = g['SylMappingState'](VF, HF)
    init_map = dict(best_mapping)
    n_perturb = max(1, len(VF) // 10)
    perturb_idx = rng.choice(len(VF), size=n_perturb, replace=False)
    for pi in perturb_idx:
        init_map[VF[pi]] = HF[rng.integers(len(HF))]
    state.set_mapping(init_map)
    for syl in VA:
        if syl not in state.mapping:
            state.mapping[syl] = HF[0]
    cur_score, cur_lps = g['score_total_syl'](state, words_em, lm, T_mcmc, **KW)
    chain_mappings, chain_scores, n_accepted, temp_scale = [], [], 0, 1.0
    t0 = time.time()
    for it in range(N_ITER):
        proposal, changed_syl = state.propose_change(rng)
        prop_score, prop_lps = g['score_incremental_syl'](
            proposal, changed_syl, words_em, lm, T_mcmc, idx_em, cur_lps, **KW)
        delta = prop_score - cur_score
        if delta > 0 or rng.random() < math.exp(delta * temp_scale):
            state, cur_score, cur_lps = proposal, prop_score, prop_lps
            n_accepted += 1
        if it % THIN == 0:
            chain_mappings.append({s: state.mapping[s] for s in VF})
            chain_scores.append(cur_score)
        if it > 0 and it % 500 == 0:
            accept_rate = n_accepted / (it + 1)
            if accept_rate < 0.3:
                temp_scale *= 0.9
            elif accept_rate > 0.7:
                temp_scale *= 1.1
    accept_rate = n_accepted / N_ITER
    print(f'  Chain {chain_id}: accept={accept_rate:.3f}, final_score={cur_score:.4f}, {time.time()-t0:.0f}s', flush=True)
    return {'chain_mappings': chain_mappings, 'chain_scores': chain_scores, 'accept_rate': accept_rate}


def check():
    """Serial notebook loop (with the no-op fallback loop) vs the worker loop, 3 EM iterations, seed 0 and 7."""
    if not LM_PATH.exists():
        setup(train_lm=True)
    g = setup(train_lm=False)
    for job in [(2.0, 0), (3.0, 7)]:
        a = em_job(job, g, keep_noop_loop=True, em_iters=3)
        b = em_job(job, g, keep_noop_loop=False, em_iters=3)
        same = a['score'] == b['score'] and a['mapping'] == b['mapping']
        print(f'check {job}: score {a["score"]:.6f} vs {b["score"]:.6f}, mapping identical: {a["mapping"] == b["mapping"]}'
              f'  -> {"OK" if same else "DIFFERENT"}')
        if not same:
            sys.exit(1)


def main():
    import multiprocessing as mp
    ap = argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--smoke', action='store_true', help='2 EM iters, 600 MCMC iters; outputs renamed *_SMOKE')
    ap.add_argument('--retrain', action='store_true',
                    help='retrain the LSTM even if nb20_parallel_lm.pt exists (GPU training is not bit-for-bit deterministic)')
    a = ap.parse_args()
    if a.check:
        return check()
    t0 = time.time()
    if a.retrain or not LM_PATH.exists():
        print('== setup + LSTM training (main process) ==', flush=True)
        g = setup(train_lm=True)
        print(f'LSTM saved to {LM_PATH.name}; {time.time()-t0:.0f}s', flush=True)
    else:
        print(f'== setup; LSTM loaded from {LM_PATH.name} (use --retrain to train it again) ==', flush=True)
        g = setup(train_lm=False)
    import torch                                   # free the main process's GPU memory (cells 8-10 do not use the LM)
    g['neural_lm'] = g['neural_lm'].cpu()
    g.pop('best_model_state', None); g.pop('optimizer', None)
    torch.cuda.empty_cache()

    ctx = mp.get_context('spawn')
    jobs = [(T, s) for T in g['T_VALUES'] for s in range(g['N_SEEDS'])]
    print(f'== EM: {len(jobs)} jobs on {a.workers} workers ==', flush=True)
    with ctx.Pool(a.workers, initializer=_init_worker, initargs=(a.smoke,)) as pool:
        em = pool.map(em_job, jobs, chunksize=1)
    json.dump([{k: v for k, v in r.items() if k not in ('mapping', 'word_lps')} for r in em],
              open(HERE / 'nb20_parallel_em.json', 'w'), indent=1)
    best = max(em, key=lambda r: r['score'])
    print(f'\nBest: T={best["T"]}, seed={best["seed"]}, score={best["score"]:.4f}, K_eff={best["K_eff"]}; '
          f'{time.time()-t0:.0f}s', flush=True)

    print(f'MCMC: 4 chains, 15000 iter, T={best["T"]}', flush=True)
    with ctx.Pool(4, initializer=_init_worker, initargs=(a.smoke,)) as pool:
        chains = pool.map(mcmc_job, [(c, best['mapping'], best['T']) for c in range(4)], chunksize=1)

    # Hand state to the notebook's cell-7 tail and cells 8-10 (verbatim)
    state = g['SylMappingState'](g['VOCAB_SYL_V_FUNC'], g['VOCAB_SYL_H_FUNC'])
    state.set_mapping(best['mapping'])
    g['BEST'] = dict(best, state=state)
    g['all_em_results'] = em
    g['T_mcmc'], g['N_CHAINS'], g['N_ITER'], g['BURN_IN'], g['THIN'] = best['T'], 4, 15000, 3000, 5
    g['mcmc_chains'] = chains
    cs = cells()
    exec(cs[6][cs[6].index('# Global best from MCMC'):], g)
    for c in cs[7:]:
        exec(c, g)
    if a.smoke:
        for f in ['syl2syl_shuf_resultados.json', 'syl2syl_shuf_mapping.json', 'nb20_parallel_em.json']:
            (HERE / f).rename(HERE / f.replace('.json', '_SMOKE.json'))
    print(f'== done in {time.time()-t0:.0f}s ==', flush=True)


if __name__ == '__main__':
    import os
    os.environ.setdefault('PYTORCH_ALLOC_CONF', 'expandable_segments:True')
    os.chdir(HERE)
    main()

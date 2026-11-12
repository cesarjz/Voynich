# Re-analysis with controls (2026)

Scripts, logs and result files of the re-analysis that supersedes the preliminary preprints in this repository
(see the correction notice at the top of the main [README](../README.md) and on Zenodo:
[Phase 1](https://doi.org/10.5281/zenodo.19188264) · [Phase 2](https://doi.org/10.5281/zenodo.19546773)).
Every analysis is run with explicit controls: a known-plaintext benchmark, natural-language and shuffled
baselines, and permutation nulls. Seeds are fixed. Each script states its purpose, inputs and outputs in its
header docstring; each folder keeps the log of the run that produced its `results/`.

## Where each result comes from

| Topic | Folder / scripts | Outputs |
|---|---|---|
| Nineteen decipherment models: unified n-gram re-scoring (realism index), frequency-band null, shuffled-input runs | `reeval/` (`run_ngram_reeval.py`, `freq_band_null.py`, `shuf_models.py`; original model outputs in `reeval/stored_results/`) | `reeval/results/` |
| Models 12 and 13 re-run (syllable-to-syllable, nucleus-only), real and shuffled input | `rerun/` (`make_reruns.py`, `make_reruns_shuf.py`, `nb20_parallel.py`) | `rerun/*.json`, `*.ipynb` |
| Known-plaintext benchmark (enciphered Hebrew, three levels), diagnosis of the objective | `c2_benchmark/` (`cipher.py`, `run_c2.py`, `diag_objective.py`) | `c2_benchmark/results/`, `results_free/` |
| Calibrated tests on the manuscript; Ge'ez positive controls; specificity controls | `c2_benchmark/` (`voynich_data.py`, `geez_data.py`, `spec_data.py`, `run_c2.py --voynich/--geez/--spec`) | `results_voynich/`, `results_geez/`, `results_spec/` |
| Entropy estimator ('bounce') calibration and decomposition; information capacity; ranking of generative models without the bounce | `c1_entropy/` (`bounce_calibration.py`, `capacity.py`, `rerank_no_bounce.py`) | `c1_entropy/results/` |
| Self-citation control | `c3_baselines/self_citation.py` | `c3_baselines/results/` |
| Verbose substitution (merge test) | `h1_verbose/verbose_merge.py` | `h1_verbose/results/` |
| Utilization null; corpus comparison table (STA1 and EVA) | `c3_baselines/` (`utilization_null.py`, `comparison_table.py`, `comparison_table_eva.py`) | `c3_baselines/results/` |
| Onset/coda ratio: Semitic and sixteen further historical texts, subsample/edge/shuffle nulls, synthetic cipher factors and seeds; figure | `c3_baselines/` (`onset_coda_null.py`, `onset_coda_v2.py`, `onset_coda_factors.py`, `onset_coda_seeds.py`, `fig_onset_coda.py`) | `c3_baselines/results/`, `figures/` |
| Six-role grammar: positional null, random-partition control | `c3_baselines/` (`role_transition_null.py`, `role_partition_control.py`) | `c3_baselines/results/` |
| Visual glyph families and word position | `c3_baselines/family_position.py` | `c3_baselines/results/` |
| Page-initial words | `c3_baselines/first_word_null.py` | `c3_baselines/results/` |
| Five-slot schema; Stolfi's and Zattera's grammars reimplemented; word-model comparison | `c4_schema/` (`slot_schema.py`, `prior_models.py`, `role_vs_prior.py`) | `c4_schema/results/` |
| Section classifier by scribe; section labels from the transliteration metadata | `c5_classifier/` (`classifier_c5.py`, `classifier_c5_withinhand.py`, `sections_rerun.py`), `sections_I/` | `c5_classifier/results/`, `sections_I/out/` |

Shared code: `reeval/nbcode.py` loads parsing and segmentation functions verbatim from the original notebooks;
`reeval/corpora.py` loads every corpus; `common/` holds the control-text loader and the Naibbe cipher.

## Data

- In this repository: the Voynich transliterations (`corpus/voynich_sta.txt`, `corpus/voynich_eva.txt`), the
  Hebrew Torah from Sefaria (public domain, `corpus/sefaria/`), the Tibbonid Hebrew and Judeo-Arabic corpora
  (`corpus/`), and the Project Gutenberg texts (public domain, `corpus/gutenberg/`).
- Fetched by `bash fetch_external.sh` into `reanalysis/external/` (not redistributed here; pinned to the commits used
  and verified against `checksums_external.sha256`): the Gaskell & Bowern (2022) historical texts, the Naibbe cipher
  tables (Greshko 2025), Stolfi's word grammar (from Zattera's v4j repository), and Targum Onkelos and the Zohar
  from Sefaria. Sefaria has since added two vowel points to Onkelos Deuteronomy 32:31–32; vowel points are
  removed before tokenisation, so the words used are unchanged.
- The Ge'ez corpus is TraCES v1 (doi:10.25592/uhhfdm.707). Its licence (CC BY-NC-ND 4.0) does not allow
  redistribution: download it and run `geez/traces_v1_extract.py`. The earlier Ge'ez export used by the
  preliminary notebooks contained interleaved annotation layers and has been removed from this repository; the
  re-scoring of Model 19 (`reeval/`, model 19) needs that export and is therefore not reproducible from here. Files
  derived from TraCES (Ge'ez plaintexts, enciphered versions, Ge'ez language models) are not included, and the
  plaintext samples of the Ge'ez positive controls were removed from `c2_benchmark/results_geez/c2_summary.json`.

## Running

Python 3.12 with the versions in `requirements.txt`. From each folder: `python <script>.py`. Long jobs
(`c2_benchmark/run_c2.py`, `rerun/nb20_parallel.py`, `c3_baselines/role_partition_control.py`) run in parallel
over CPU cores. The benchmark's Hebrew language models are included (`c2_benchmark/cache/`); the Ge'ez ones are
not, since they are trained on TraCES, and are rebuilt on first run.
Training the LSTM language models on a GPU is not bit-for-bit deterministic, so the trained models used in the
analysis are included and reused when present: `c2_benchmark/cache/lm_*.pt` and `rerun/nb20_parallel_lm.pt` (Model 12).
Delete them (or pass `--retrain` to `rerun/nb20_parallel.py`) to retrain; results then differ slightly. `rerun/nb20_parallel.py` uses the GPU in every worker; 8 workers
fit in 16 GB.

## Known issue (12 November 2026)

The specificity control `ctl_SELF` (copy-and-modify text, `c2_benchmark/data/ctl_SELF.json`, `results_spec/`) was
generated before a fix that made `c3_baselines/self_citation.py::copy_modify` independent of Python's hash seed
(set iteration order). Re-running `spec_data.py` now produces a different, deterministic `ctl_SELF`; the
corresponding benchmark runs are being repeated and will replace the current files.

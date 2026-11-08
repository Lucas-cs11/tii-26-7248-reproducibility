# Reproduction guide

Each experiment is independent: you can reproduce one without re-running the
others. The scalability study is the only experiment executed on Modal; all
other experiments run on GitHub Actions or a local machine. **Timings are
compared only within one execution platform** — the paper never pools
measurements taken on different hardware.

## 0. Environment

```bash
python3 --version          # 3.13.x
python3 -m venv .venv && . .venv/bin/activate
python -m pip install --require-hashes -r experiments/01_scalability/code/requirements.lock

# 55 unit tests (exact-rational timing boundaries, SCG/synchronizer regressions,
# instance-family semantics, verifier behaviour)
(cd experiments/01_scalability/code && python -m unittest discover -s tests -p 'test_*.py')
```

The scalability execution additionally needs `modal==1.6.3` and a Modal
account; the worker image is pinned to Python 3.13, NumPy 2.3.4, SciPy 1.16.2
and Modal 1.6.3 (see `experiments/01_scalability/code/modal_app/`).

## 1. Protocol integrity (one minute)

```bash
tar -xzf experiments/01_scalability/protocol/formal_tasks.tar.gz \
  -C experiments/01_scalability/protocol
python experiments/01_scalability/code/scripts/validate_formal_grid.py \
  --manifest experiments/01_scalability/protocol/formal_task_manifest.json \
  --tasks experiments/01_scalability/protocol/formal_tasks \
  --semantics-reference experiments/01_scalability/protocol/semantics_reference.json \
  --out /tmp/validation.json
```

Expected: PASS with 8,280 evaluations, 120 worker partitions, and the
pre-registered group sizes 600 / 1,080 / 5,400 / 1,200.

## 2. Scalability study — 8,280 evaluations

Prerequisites: a Modal token configured in the usual way, no active Modal
applications, and the budget file `work/budget.json` with the authorised cap
(see `docs/execution_environment.md`).

```bash
# free planning check
python experiments/01_scalability/code/scripts/run_modal.py plan --dry-run --formal

# paid run: 120 partitions x 69 evaluations, 20 concurrent, 60 s cap,
# budget guard stops new work at $9.50 of the authorised $10
python experiments/01_scalability/code/scripts/run_modal.py run \
  --confirm-budget --max-parallel 20 \
  --shard-manifest experiments/01_scalability/protocol/shard_manifest.json \
  --shard-dir experiments/01_scalability/protocol/shard_plan

# download, independent audit, statistics, figure
python experiments/01_scalability/code/scripts/run_modal.py download --run-id <run id>
python experiments/01_scalability/code/scripts/audit_results.py \
  --download-dir work/run_<run id> \
  --shard-manifest experiments/01_scalability/protocol/shard_manifest.json \
  --source-tasks experiments/01_scalability/protocol/formal_tasks \
  --expected-tasks 8280 --out work/audit
python experiments/01_scalability/code/scripts/analyze_results.py \
  --tasks-dir experiments/01_scalability/protocol/formal_tasks \
  --manifest experiments/01_scalability/protocol/formal_task_manifest.json \
  --raw-dir work/run_<run id> --out work/analysis \
  --dataset-label FORMAL --reference-audit work/audit/audit.json
python experiments/01_scalability/code/scripts/plot_figure6.py \
  --analysis-dir work/analysis --out work/analysis
```

Expected: 5,406 completed, 2,874 wall-clock-capped, 0 errors; verdicts
VER 1,975 / AMB 2,782 / INC 649; total cost ≈ $5.5. Capped evaluations are
never imputed as completions, and time quantiles use completed evaluations only.

Reference run: `run-5038d2a9-20261107T113535Z`; independent audit PASS (8,280
evaluations, 8,280 unique identifiers, 120 partitions, 0 technical failures).

## 3. Implementation equivalence

```bash
python experiments/01_scalability/code/scripts/evaluate_equivalence.py
# expect EQUIVALENCE_ACCEPTED = GO
```

Three layers: (i) 48 paired evaluations (30 conclusive and identical, 18
accounted as censored), (ii) transition-level comparison of the observation
synchronizer (45 checked + 3 unrunnable heavy evaluations with stated reasons;
726,665 comparisons, 0 mismatches), (iii) five component checks (SCG adjacency
index, marking cache, trace deduplication, exact-rational boundary cases,
independent rational oracle). Evidence files are in
`experiments/02_implementation_equivalence/`.

## 4. Historical baseline audit (3,645 evaluations)

The fixed manifest and the sharded workflow live in the archived companion
repository; the final aggregate is checked in here:

```text
experiments/06_historical_audit/summary.json
experiments/06_historical_audit/historical_baseline_report.md
```

Result: 3,645/3,645 primary recomputations with **0 verdict changes**
(VER 1,689→1,689, AMB 1,956→1,956); full second pass 1,956/1,956 (1,136
completed, 820 wall-clock-capped).

## 5. Verifier timing (Fig. 3)

The per-case timing table is shipped as `experiments/03_verifier_timing/results/timing_all_rows.csv.gz`
(36,450 rows) together with `timing_summary.json` (counts and runtime quantiles:
median 8.1 ms, P95 0.92 s, maximum 5.59 s; verdicts VER 20,412 / AMB 16,038).

```bash
# measure one partition from scratch (60 s cap per evaluation, 3 repeats)
python experiments/03_verifier_timing/driver/run_shard.py --shard 000 --out results/
```

The frozen evaluation list (255 partitions) remains in the archived companion
repository `tii-26-7248-verifier-timing`; the verifier implementation is
`experiments/01_scalability/code/src/`.

## 6. Ambiguity-horizon study

The aggregate result is `experiments/04_ambiguity_horizon/results/threshold_summary.json`
(4,068 models covered by the archived artifacts; threshold `H_amb*/H_base`
median 0.231, P05–P95 0.141–0.333). Fixed implementation and configuration:
`experiments/04_ambiguity_horizon/experiment/`.

```bash
python experiments/04_ambiguity_horizon/experiment/run_threshold.py --help
```

The cohort definitions are indexed in `cohorts/index.json`; the cohort CSV files
and the lab-completed part remain in the archived repository.

## 7. One-step exhaustive adjustment baseline

The complete population result is
`experiments/05_exhaustive_baseline/results/adjustment_summary.json`:
16,038 evaluations — 2,001 verified successes, 11,314 finite-search failures,
2,683 wall-clock-capped, 40 errors (≈72.6 h of runner time in total).

Fixed population (`population/full_amb_population.csv.gz`), the 32-partition
plan (`shards/index.json`) and the sharding/benchmark tools are shipped here;
the full per-evaluation result rows remain in the archived companion
repository `tii-26-7248-exhaustive-full`.

## 8. Case studies

* `07_case_studies/illustrative/` — fixed net, driver scripts, results, figures.
* `07_case_studies/published_cases/` — literature-grounded evaluation of
  published nets; models, pipeline, figures and case reports included.
* `07_case_studies/context_dataset/` — scripts for the public Kaupp context
  dataset (Zenodo 4034867, CC BY-NC 4.0); the dataset is downloaded from its
  original source and never redistributed here.

Each folder has its own README.

## 9. Integrity

```bash
sha256sum -c MANIFEST.sha256
```

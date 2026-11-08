# Reproduction guide

Everything below is independent: you can reproduce a single experiment without
re-running the others. The scalability matrix (8,280 cells) is the only
Modal-executed experiment; all other experiments run on GitHub Actions or a
local machine. **Never compare timings across execution platforms** — the paper
normalizes within one platform only.

## 0. Environment

```bash
python3 --version          # 3.13.x
python3 -m venv .venv && . .venv/bin/activate
python -m pip install --require-hashes -r experiments/01_scalability_v6/code/requirements-v5.lock
(cd experiments/01_scalability_v6/code && python -m unittest discover -s tests -p 'test_*.py')   # expect 67 tests OK
```

For the Modal execution you additionally need `modal==1.6.3` and a Modal
account/workspace; the worker image is pinned to `numpy==2.3.4`,
`scipy==1.16.2`, `modal==1.6.3`, Python 3.13 (see
`experiments/01_scalability_v6/code/modal_app/`).

## 1. Protocol integrity (1 minute)

```bash
cd experiments/01_scalability_v6/protocol
tar -xzf v6_formal_tasks.tar.gz
cd - >/dev/null
python experiments/01_scalability_v6/code/scripts/validate_v6_formal_protocol.py \
  --manifest experiments/01_scalability_v6/protocol/v6_formal_manifest.json \
  --tasks experiments/01_scalability_v6/protocol/v6_formal_tasks \
  --semantics-gate experiments/01_scalability_v6/protocol/v6_semantics_gate.json \
  --out /tmp/v6_validation.json
# expect PASS, 8,280 tasks, 120 shards, 600/1080/5400/1200 cells per experiment family
```

## 2. Scalability v6 — 8,280 cells on Modal

Preconditions: `work/v6_modal_budget/budget.json` with `authorized: true` and
the $10 cap (see `docs/v6_modal_environment.md`); a Modal token configured the
usual way; no active Modal apps.

```bash
# dry run (no paid resources)
python experiments/01_scalability_v6/code/scripts/run_v6_modal.py plan --dry-run --formal

# paid run: 120 shards x 69 cells, max 20 parallel, 60 s/cell, budget guard $9.50
python experiments/01_scalability_v6/code/scripts/run_v6_modal.py run \
  --confirm-budget --max-parallel 20 --volume-prefix scalability_v6_formal \
  --shard-manifest experiments/01_scalability_v6/protocol/v6_modal_shards_manifest.json \
  --shard-dir experiments/01_scalability_v6/protocol/v6_modal_shards

# download, audit and statistics (the audit is deliberately independent)
python experiments/01_scalability_v6/code/scripts/run_v6_modal.py download --run-id <run id>
python experiments/01_scalability_v6/code/scripts/audit_v6_modal_results.py \
  --download-dir work/v6_modal_run_<run id> \
  --shard-manifest experiments/01_scalability_v6/protocol/v6_modal_shards_manifest.json \
  --source-tasks experiments/01_scalability_v6/protocol/v6_formal_tasks \
  --expected-tasks 8280 --out work/v6_formal_audit
python experiments/01_scalability_v6/code/scripts/analyze_v6_formal_results.py \
  --tasks-dir experiments/01_scalability_v6/protocol/v6_formal_tasks \
  --manifest experiments/01_scalability_v6/protocol/v6_formal_manifest.json \
  --raw-dir work/v6_modal_run_<run id> --out work/v6_analysis_formal \
  --dataset-label FORMAL --reference-audit work/v6_formal_audit/audit.json
python experiments/01_scalability_v6/code/scripts/plot_figure6_v6.py \
  --analysis-dir work/v6_analysis_formal --out work/v6_analysis_formal
```

Expected: **5,406 completed / 2,874 `TIMEOUT_WALL_CLOCK` / 0 errors**, VER 1,975 /
AMB 2,782 / INC 649, cost ≈ $5.5 (the reference run measured $5.53 including
the pilot). Results are censoring-aware: time quantiles use COMPLETED cells
only; timeouts are never imputed.

Reference run: `run-5038d2a9-20261107T113535Z`; independent audit PASS
(8,280 tasks, 8,280 unique task ids, 120 shards, 0 technical failures).

## 3. Differential v2 (semantic equivalence of the optimized verifier)

```bash
python experiments/02_cross_version_equivalence/../01_scalability_v6/code/scripts/evaluate_v6_differential_v2.py
# expect DIFFERENTIAL_V2_ACCEPTED = GO
```

Layers: 48-cell end-to-end differential (30 conclusive identical, 18 censored),
transition-level synchronizer equivalence (45 checked + 3 heavy cells censored
with explicit reasons, 726,665 comparisons, 0 mismatch) and component audits
(SCG adjacency index, marking cache, trace-record dedupe, DBM/Fraction
boundaries, independent Fraction oracle). Evidence files are in
`experiments/02_cross_version_equivalence/`.

## 4. Historical baseline audit (3,645 evaluations)

The frozen manifest and the GitHub Actions sharded workflow live in the
archived scalability repository; the aggregate result is checked in here:

```text
experiments/03_historical_audit/summary.json
experiments/03_historical_audit/v6_historical_recompute_report.md
```

Result: 3,645/3,645 primary recomputations, **0 verdict drift**
(VER 1,689→1,689, AMB 1,956→1,956), COMPLETE_SET second pass 1,956/1,956 with
1,136 completed / 820 timeouts.

## 5. Verifier timing (Fig. 3)

```bash
# per-case timing: 255 shards x 143 cases, 3 repeats, method "main", 60 s cap
python experiments/04_verifier_timing/runner/run_shard.py --shard <NNN> --out results/
```

Results in `experiments/04_verifier_timing/results/shard_*.csv`; the curated
package keeps the first shard as an example — the full 255-shard output is in
the archived `tii-26-7248-verifier-timing` repository.

## 6. H-sensitivity

Frozen implementation and configuration:
`experiments/05_h_sensitivity/experiment/` (`run_threshold.py`,
`h_sensitivity_config.json`). The 40 remaining cohorts (1,140 models) are
defined in the archived repository; the lab-completed part (14,898 models) is
not redistributed. Run:

```bash
python experiments/05_h_sensitivity/experiment/run_threshold.py --help
```

## 7. One-step exhaustive baseline

Frozen population (`population/full_amb_population.csv.gz`, 16,038 AMB
evaluations), sharding tools and the source snapshot are in
`experiments/06_exhaustive_baseline/`. The full shard results (40 shards) are in
the archived repository; `shards/calib.json` is the 40-case calibration sample.

## 8. Case studies

* `07_case_studies/illustrative/` — model, scripts, results and figures of the
  illustrative TPN case.
* `07_case_studies/published_cases/` — literature-grounded evaluation of Wang/
  Mahulea/Silva TAC 2015 and other published nets; includes models, pipeline,
  figures, reports and `MANIFEST.sha256`.
* `07_case_studies/context_dataset/` — scripts and reports for the public Kaupp
  context dataset (Zenodo 4034867, CC BY-NC 4.0).

Each folder has its own README/commands.

## 9. Integrity

```bash
sha256sum -c MANIFEST.sha256
```

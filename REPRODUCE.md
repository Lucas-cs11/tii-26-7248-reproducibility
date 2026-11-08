# Reproduction

## Environment

```bash
python3 --version      # 3.13
python -m venv .venv && . .venv/bin/activate
python -m pip install --require-hashes -r experiments/01_scalability/code/requirements.lock

(cd experiments/01_scalability/code && python -m unittest discover -s tests -p 'test_*.py')
```

## 1. Scalability study (8,280 evaluations, Fig. 6)

Protocol integrity:

```bash
tar -xzf experiments/01_scalability/protocol/formal_tasks.tar.gz \
  -C experiments/01_scalability/protocol
python experiments/01_scalability/code/scripts/validate_formal_grid.py \
  --manifest experiments/01_scalability/protocol/formal_task_manifest.json \
  --tasks experiments/01_scalability/protocol/formal_tasks \
  --semantics-reference experiments/01_scalability/protocol/semantics_reference.json \
  --out /tmp/validation.json
```

Execution (20 concurrent workers, 60 s per evaluation):

```bash
python experiments/01_scalability/code/scripts/run_modal.py plan --dry-run --formal
python experiments/01_scalability/code/scripts/run_modal.py run \
  --confirm-budget --max-parallel 20 \
  --shard-manifest experiments/01_scalability/protocol/shard_manifest.json \
  --shard-dir experiments/01_scalability/protocol/shard_plan
```

Audit, statistics and figure:

```bash
python experiments/01_scalability/code/scripts/run_modal.py download --run-id <id>
python experiments/01_scalability/code/scripts/audit_results.py \
  --download-dir work/run_<id> \
  --shard-manifest experiments/01_scalability/protocol/shard_manifest.json \
  --source-tasks experiments/01_scalability/protocol/formal_tasks \
  --expected-tasks 8280 --out work/audit
python experiments/01_scalability/code/scripts/analyze_results.py \
  --tasks-dir experiments/01_scalability/protocol/formal_tasks \
  --manifest experiments/01_scalability/protocol/formal_task_manifest.json \
  --raw-dir work/run_<id> --out work/analysis \
  --dataset-label FORMAL --reference-audit work/audit/audit.json
python experiments/01_scalability/code/scripts/plot_figure6.py \
  --analysis-dir work/analysis --out work/analysis
```

Expected: 5,406 completed, 2,874 wall-clock-capped, 0 errors; VER 1,975 /
AMB 2,782 / INC 649. Capped evaluations are never imputed as completions.

## 2. Implementation equivalence

```bash
python experiments/01_scalability/code/scripts/evaluate_equivalence.py   # EQUIVALENCE_ACCEPTED = GO
```

Proof layers: 48 paired evaluations; transition-level synchronizer comparison
(726,665 comparisons, 0 mismatches); five component audits. Evidence:
`experiments/02_implementation_equivalence/`.

## 3. Verifier timing (Fig. 3)

The complete table is `experiments/03_verifier_timing/results/timing_all_rows.csv.gz`
(36,450 rows). To measure one partition from scratch:

```bash
python experiments/03_verifier_timing/driver/run_shard.py --shard 000 --out results/
```

## 4. Ambiguity-horizon study

Aggregate: `experiments/04_ambiguity_horizon/results/threshold_summary.json`.
Fixed implementation: `experiments/04_ambiguity_horizon/experiment/`.

```bash
python experiments/04_ambiguity_horizon/experiment/run_threshold.py --help
```

## 5. One-step exhaustive adjustment baseline

Aggregate: `experiments/05_exhaustive_baseline/results/adjustment_summary.json`.
Inputs and tools: `experiments/05_exhaustive_baseline/`.

```bash
python experiments/05_exhaustive_baseline/tools/make_shards.py --help
```

## 6. Historical-baseline audit

Result: `experiments/06_historical_audit/summary.json` (3,645 evaluations,
0 verdict changes; second pass 1,956/1,956).

## 7. Case studies

`experiments/07_case_studies/` — each folder has its own README, models and
result files.

## Integrity

```bash
sha256sum -c MANIFEST.sha256
```

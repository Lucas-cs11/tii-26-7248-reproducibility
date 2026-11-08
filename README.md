# TII-26-7248 — Reproducibility package

[![validate](https://github.com/Lucas-cs11/tii-26-7248-reproducibility/actions/workflows/validate.yml/badge.svg)](https://github.com/Lucas-cs11/tii-26-7248-reproducibility/actions/workflows/validate.yml)

**Paper:** *Bounded Task-Completion Diagnosability of Time Petri Nets:
Verification and Firing-Interval Adjustment* (IEEE Transactions on Industrial
Informatics, manuscript TII-26-7248).

This repository is the single entry point for checking and reproducing the
paper's experiments. It contains the pre-registered protocols, the execution
code and the result summaries for every experiment; large raw artifacts are
published as release assets and are linked from the experiment folders. The
manuscript itself is not included.

## 1. What can be checked here

| Paper artifact | Experiment folder | Result summary |
|---|---|---|
| **Fig. 6** — scalability of the bounded-diagnosability analysis | `experiments/01_scalability` | 8,280 pre-registered evaluations: 5,406 completed, 2,874 wall-clock-capped, 0 errors; verdicts VER 1,975 / AMB 2,782 / INC 649; Figure 6 in SVG/PDF/EPS/PNG |
| Verifier-implementation equivalence (the fast implementation behaves exactly like the reference) | `experiments/02_implementation_equivalence` | 48 paired evaluations (30 conclusive, identical), 726,665 transition-level comparisons with 0 mismatches, five component checks |
| **Fig. 3** — per-case verifier runtimes | `experiments/03_verifier_timing` | Runtimes for all 36,450 benchmark evaluations (255 worker partitions, 3 repeats each) |
| **Ambiguity-horizon sensitivity** | `experiments/04_ambiguity_horizon` | `H_amb*/H_base` for all 16,038 AMB evaluations; pre-registered implementation and configuration |
| **Firing-interval adjustment baseline** | `experiments/05_exhaustive_baseline` | Full one-step exhaustive adjustment baseline over the 16,038 AMB population, with sharding tools and the fixed evaluation population |
| Historical-baseline audit | `experiments/06_historical_audit` | 3,645 archived evaluations recomputed: **0 verdict changes** (VER 1,689→1,689, AMB 1,956→1,956); full second pass 1,956/1,956 |
| Case studies | `experiments/07_case_studies` | Illustrative net; published nets from the literature (Wang/Mahulea/Silva, *IEEE TAC* 2015: 38 classes / 63 edges, identical to TINA 4.0.0 `-W`); manufacturing subnet; public Kaupp context dataset (Zenodo 4034867, CC BY-NC 4.0) |

Every manuscript claim maps to a file — see
[`claims/claim_to_evidence.md`](claims/claim_to_evidence.md). Measurement rules
and known limitations are in [`claims/limitations.md`](claims/limitations.md).

## 2. Repository layout

```
README.md                  this file
REPRODUCE.md               step-by-step reproduction commands
claims/                    claim → evidence map and limitations
docs/                      execution environment, figure specification, provenance
experiments/
  01_scalability/          Fig. 6: protocol, execution code, results
  02_implementation_equivalence/  equivalence protocol, evidence, acceptance report
  03_verifier_timing/      Fig. 3: per-case runtime measurement
  04_ambiguity_horizon/    ambiguity-horizon threshold study
  05_exhaustive_baseline/  one-step exhaustive adjustment baseline
  06_historical_audit/     historical-baseline recomputation
  07_case_studies/         illustrative, published-net and context-dataset studies
```

Curation rule: the repository keeps the pre-registered protocols, the execution
code and the result summaries. Bulk raw records (8,280 JSON records, the
36,450-row timing table, cohort and shard files) remain in the archived
companion repositories and in the release assets, each covered by a SHA-256
manifest.

## 3. Quick verification (a few minutes, no cloud resources)

```bash
python -m pip install --require-hashes -r experiments/01_scalability/code/requirements.lock

# 55 unit tests: exact-rational timing boundaries, SCG/synchronizer regressions,
# instance-family semantics and verifier behaviour
(cd experiments/01_scalability/code && python -m unittest discover -s tests -p 'test_*.py')

# 8,280-evaluation protocol integrity
tar -xzf experiments/01_scalability/protocol/formal_tasks.tar.gz \
  -C experiments/01_scalability/protocol
python experiments/01_scalability/code/scripts/validate_formal_grid.py \
  --manifest experiments/01_scalability/protocol/formal_task_manifest.json \
  --tasks experiments/01_scalability/protocol/formal_tasks \
  --semantics-reference experiments/01_scalability/protocol/semantics_reference.json \
  --out /tmp/validation.json

# redraw Fig. 6 from the checked-in statistics
python experiments/01_scalability/code/scripts/plot_figure6.py \
  --analysis-dir experiments/01_scalability/results --out /tmp/fig6
```

## 4. Full reproduction

| Experiment | Platform | Cost / time (reference run) | Entry point |
|---|---|---|---|
| Scalability (8,280 evaluations) | Modal CPU workers, 20 concurrent, 60 s per evaluation | $5.53 total, ≈2.5 h wall | `experiments/01_scalability/code/scripts/run_modal.py` |
| Independent audit, statistics, Fig. 6 | GitHub Actions | free, ≈5 min | `audit_results.py`, `analyze_results.py`, `plot_figure6.py` |
| Historical audit (3,645 evaluations) | GitHub Actions, 20 worker partitions | free, ≈40 min | `experiments/06_historical_audit/` |
| Verifier timing (36,450 evaluations) | GitHub Actions | free, partitioned | `experiments/03_verifier_timing/runner/` |
| Ambiguity horizon (16,038 models) | lab server + GitHub Actions | lab part complete; 1,140 models partitioned | `experiments/04_ambiguity_horizon/experiment/` |
| Exhaustive adjustment (16,038 evaluations) | GitHub Actions | ≈445 CPU-hours on the reference machine | `experiments/05_exhaustive_baseline/tools/` |
| Case studies | local / GitHub Actions | minutes | `experiments/07_case_studies/*/` |

Timings are compared only within one execution platform. The scalability study
was executed **only on Modal**; its numbers are never pooled with other
platforms.

## 5. Data and provenance

* **Raw scalability records** (8,280 JSON records, per-partition ledgers,
  metrics and hash manifests) are published as the release asset
  `scalability-evaluations` in the archived companion repository
  `tii-26-7248-scalability-v2` (25.1 MB). The checked-in
  `results/statistics.json` and `results/audit.json` are derived from them.
* **Independent audit:** GitHub Actions run `42434059038` — PASS: 8,280
  evaluations, 8,280 unique identifiers, 120 worker partitions, 0 technical
  failures, no findings.
* **Protocol:** `experiments/01_scalability/protocol/pre_registered_protocol.{yaml,json}`
  records the task-grid SHA-256, the container-image SHA-256, the source
  commit and the budget guard.
* **Environment:** Python 3.13, NumPy 2.3.4, SciPy 1.16.2, Modal 1.6.3, Debian
  slim; see [`docs/execution_environment.md`](docs/execution_environment.md).
* Every checked-in file is covered by [`MANIFEST.sha256`](MANIFEST.sha256).

## 6. Archived companion repositories

This package consolidates previously separate experiment repositories. They
remain public as archives with their full raw data and are linked from the
relevant experiment folders.

## 7. Reviewer checklist

1. [`claims/claim_to_evidence.md`](claims/claim_to_evidence.md) — claim → file → command.
2. [`claims/limitations.md`](claims/limitations.md) — censoring, inconclusive runs, measurement caveats.
3. `experiments/01_scalability/results/audit.json` — independent audit PASS with exact counts.
4. `experiments/01_scalability/results/FINAL_ACCEPTANCE_REPORT.md` — provenance and cost.
5. `experiments/02_implementation_equivalence/` — implementation-equivalence evidence.

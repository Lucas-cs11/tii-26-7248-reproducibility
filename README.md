# TII-26-7248 — Reproducibility package

[![validate](https://github.com/Lucas-cs11/tii-26-7248-reproducibility/actions/workflows/validate.yml/badge.svg)](https://github.com/Lucas-cs11/tii-26-7248-reproducibility/actions/workflows/validate.yml)

**Paper:** *Bounded Task-Completion Diagnosability of Time Petri Nets:
Verification and Firing-Interval Adjustment* (IEEE Transactions on Industrial
Informatics, manuscript TII-26-7248).

This repository is the single entry point for the paper's experiments: what was
executed, what the results are, and how to reproduce them. It contains the
pre-registered protocols, the execution code and the result summaries; large raw
tables are published as release assets and linked from the experiment folders.
The manuscript itself is not included.

## 1. Experiment register (all experiments completed)

| # | Experiment | Artifact | Result summary | How to reproduce |
|---|---|---|---|---|
| 01 | Scalability of bounded-diagnosability analysis | **Fig. 6** | 8,280 pre-registered evaluations: 5,406 completed, 2,874 wall-clock-capped, 0 errors; VER 1,975 / AMB 2,782 / INC 649; cost $5.53 | `experiments/01_scalability` — Modal, 20 concurrent workers, 60 s cap |
| 02 | Implementation equivalence (fast implementation == reference) | — | 48 paired evaluations (30 conclusive, identical), 726,665 transition-level comparisons (0 mismatches), 5 component checks | `experiments/02_implementation_equivalence` |
| 03 | Per-case verifier runtimes | **Fig. 3** | 36,450 evaluations, all completed; VER 20,412 / AMB 16,038; runtime median 8.1 ms, P95 0.92 s, max 5.59 s | `experiments/03_verifier_timing` — GitHub Actions |
| 04 | Ambiguity-horizon sensitivity | **H-sensitivity figure** | 4,068 AMB models covered by archived artifacts: 20,340 (model, H-ratio) evaluations; threshold `H_amb*/H_base` median 0.231, P05–P95 0.141–0.333 | `experiments/04_ambiguity_horizon` — lab + GitHub Actions |
| 05 | One-step exhaustive adjustment baseline | **Adjustment table** | Full 16,038-evaluation AMB population: 2,001 verified successes, 11,314 finite-search failures, 2,683 timeouts, 40 errors; ≈72.6 h runner time | `experiments/05_exhaustive_baseline` — GitHub Actions |
| 06 | Historical-baseline audit | — | 3,645 archived evaluations recomputed: **0 verdict changes**; full second pass 1,956/1,956 | `experiments/06_historical_audit` — GitHub Actions |
| 07 | Case studies | Case figures/tables | Illustrative net; published nets (Wang/Mahulea/Silva, *IEEE TAC* 2015: 38 classes / 63 edges, identical to TINA 4.0.0 `-W`); manufacturing subnet; public context dataset (outcome: **not sufficient** for a data-grounded task-completion case, documented honestly) | `experiments/07_case_studies` |

Every manuscript claim maps to a file — see
[`claims/claim_to_evidence.md`](claims/claim_to_evidence.md). Measurement
rules, censoring and the known limits are in
[`claims/limitations.md`](claims/limitations.md).

## 2. Repository layout

```
README.md / REPRODUCE.md
claims/                    claim → evidence map, limitations
docs/                      execution environment, figure specification, provenance
experiments/01_scalability              Fig. 6 study (protocol, code, results)
experiments/02_implementation_equivalence  equivalence protocol and evidence
experiments/03_verifier_timing          Fig. 3 measurement (code, 36,450-row table)
experiments/04_ambiguity_horizon        ambiguity-threshold study
experiments/05_exhaustive_baseline      adjustment baseline (population, tools, summary)
experiments/06_historical_audit         historical-baseline recomputation
experiments/07_case_studies             illustrative, published-case and context studies
```

Curation rule: pre-registered protocols, execution code and result summaries
are kept here; bulk raw tables (the 8,280 scalability records, full 16,038-row
adjustment rows, cohort files) are published as release assets or kept in the
archived companion repositories, each covered by a SHA-256 manifest.

## 3. Quick verification (minutes, no cloud resources)

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

| Experiment | Platform | Cost / time (reference) | Entry point |
|---|---|---|---|
| 01 Scalability | Modal CPU workers, 20 concurrent, 60 s/evaluation | $5.53, ≈2.5 h | `experiments/01_scalability/code/scripts/run_modal.py` |
| 02 Equivalence | local / GitHub Actions | minutes | `code/scripts/evaluate_equivalence.py` + `verify_*` scripts |
| 03 Verifier timing | GitHub Actions | free, 255 partitions | `experiments/03_verifier_timing/driver/` |
| 04 Ambiguity horizon | lab + GitHub Actions | free runner part | `experiments/04_ambiguity_horizon/experiment/` |
| 05 Exhaustive baseline | GitHub Actions | ≈72.6 h runner time | `experiments/05_exhaustive_baseline/tools/` |
| 06 Historical audit | GitHub Actions, 20 partitions | free, ≈40 min | `experiments/06_historical_audit/` |
| 07 Case studies | local / GitHub Actions | minutes | `experiments/07_case_studies/*/` |

Timings are only compared within one execution platform; the scalability study
ran **only on Modal**.

## 5. Data and provenance

* Raw scalability records (8,280 JSON records, per-partition ledgers, metrics,
  hash manifests): release asset `scalability-evaluations` in
  [`tii-26-7248-scalability-archive`](https://github.com/Lucas-cs11/tii-26-7248-scalability-archive).
* Independent audit: GitHub Actions run `42434059038` — PASS, 8,280 evaluations,
  8,280 unique identifiers, 120 partitions, 0 technical failures, no findings.
* Pre-registered protocol: `experiments/01_scalability/protocol/pre_registered_protocol.{yaml,json}`.
* Environment: Python 3.13, NumPy 2.3.4, SciPy 1.16.2, Modal 1.6.3; see `docs/`.
* Every checked-in file is covered by [`MANIFEST.sha256`](MANIFEST.sha256).

## 6. Archived companion repositories

All experiments were originally developed in separate repositories; this
package consolidates them. The archives remain public with their full raw data:

| Archive | Content now in this package |
|---|---|
| [`tii-26-7248-scalability-archive`](https://github.com/Lucas-cs11/tii-26-7248-scalability-archive) | Experiments 01, 02, 06 and the raw scalability records |
| [`tii-26-7248-verifier-timing`](https://github.com/Lucas-cs11/tii-26-7248-verifier-timing) | Experiment 03 evaluation list |
| [`tii-26-7248-h-sensitivity`](https://github.com/Lucas-cs11/tii-26-7248-h-sensitivity) | Experiment 04 cohort files |
| [`tii-26-7248-exhaustive-full`](https://github.com/Lucas-cs11/tii-26-7248-exhaustive-full) | Experiment 05 full result rows |
| [`tii-published-tpn-case-eval`](https://github.com/Lucas-cs11/tii-published-tpn-case-eval) | Experiment 07 published-case sources |
| [`tii-illustrative-tpn-case`](https://github.com/Lucas-cs11/tii-illustrative-tpn-case) | Experiment 07 illustrative-case sources |
| [`tii-context-case-study`](https://github.com/Lucas-cs11/tii-context-case-study) | Experiment 07 context-dataset raw tables |
| [`tii-26-7248-scalability-early-archive`](https://github.com/Lucas-cs11/tii-26-7248-scalability-early-archive) | superseded early design, history only |

The separate industrial *Version B* study is maintained in its own repository
and is not part of this package.

## 7. Reviewer checklist

1. [`claims/claim_to_evidence.md`](claims/claim_to_evidence.md) — claim → file → command.
2. [`claims/limitations.md`](claims/limitations.md) — censoring, inconclusive runs, caveats.
3. `experiments/01_scalability/results/audit.json` — independent audit PASS with exact counts.
4. `experiments/01_scalability/results/FINAL_ACCEPTANCE_REPORT.md` — provenance and cost.
5. `experiments/02_implementation_equivalence/` — implementation-equivalence evidence.

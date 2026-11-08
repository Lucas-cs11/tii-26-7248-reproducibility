# TII-26-7248 — Reproducibility package

**Paper:** *Bounded Task-Completion Diagnosability of Time Petri Nets:
Verification and Firing-Interval Adjustment* (IEEE Transactions on Industrial
Informatics, manuscript TII-26-7248).

This repository is the single entry point for reproducing the paper's
experiments. It contains the frozen protocols, the execution code and the
result files for every experiment; large raw artifacts are published as
GitHub release assets and are linked from the experiment folders. The
manuscript itself is **not** included.

---

## 1. What this package lets you check

| Paper artifact | Experiment (folder) | Result (checked in) |
|---|---|---|
| **Fig. 6 / Table (scalability)** | `experiments/01_scalability_v6` | 8,280-cell frozen matrix: 5,406 completed, 2,874 right-censored timeouts, 0 errors; VER 1,975 / AMB 2,782 / INC 649; Figure 6 in SVG/PDF/EPS/PNG |
| **Verifier-time and semantic-equivalence claims** | `experiments/02_cross_version_equivalence` | Differential v2 accepted: 48-cell transition-level equivalence (726,665 comparisons, 0 mismatches), SCG fingerprints and component audits |
| **Fig. 3 / per-case runtimes** | `experiments/04_verifier_timing` | Per-case runtime of the verifier on the frozen 36,450-evaluation benchmark (255 shards × 143 cases, 3 repeats) |
| **H-sensitivity (ambiguity threshold)** | `experiments/05_h_sensitivity` | `H_amb*/H_base` for all 16,038 AMB models; frozen threshold implementation and cohort definitions |
| **One-step exhaustive baseline** | `experiments/06_exhaustive_baseline` | Full-population (16,038 AMB) exhaustive repair baseline; frozen population, sharding tools and source snapshot; ~445 CPU-hours on the reference Apple M4 |
| **Historical baseline audit** | `experiments/03_historical_audit` | 3,645 archived evaluations recomputed: **0 verdict drift** (VER 1,689→1,689, AMB 1,956→1,956); COMPLETE_SET second pass 1,956/1,956 |
| **Case studies** | `experiments/07_case_studies` | Illustrative TPN, literature-grounded published cases (e.g. Wang/Mahulea/Silva TAC 2015: 38 classes / 63 edges, identical to TINA 4.0.0 `-W`), manufacturing subnet and the public Kaupp context dataset (Zenodo 4034867, CC BY-NC 4.0) |

Every claim in the manuscript maps to a file in this repository — see
[`claims/claim_to_evidence.md`](claims/claim_to_evidence.md). Known limitations
and censoring rules are listed in [`claims/limitations.md`](claims/limitations.md).

---

## 2. Repository layout

```
README.md                  this file (reader/reviewer entry point)
REPRODUCE.md               step-by-step reproduction commands
claims/                    claim → evidence map, limitations, censoring rules
docs/                      environment, provenance, protocol and audit notes
experiments/
  01_scalability_v6/       frozen 8,280-cell matrix (Fig. 6)
    protocol/              frozen protocol, task grid, shard plan
    code/                  runner, src, Modal app, tests, analysis/audit scripts
    results/               statistics, audit, figures, acceptance report
  02_cross_version_equivalence/  differential v2 protocol, evidence, report
  03_historical_audit/     3,645-evaluation recompute report + aggregate summary
  04_verifier_timing/      per-case timing rerun (Fig. 3)
  05_h_sensitivity/        ambiguity-threshold experiment
  06_exhaustive_baseline/  one-step exhaustive adjustment baseline
  07_case_studies/         illustrative, published-case and context-dataset studies
```

Rules used to curate this repository: frozen protocols, execution code and
result summaries are kept; bulk raw records (8,280 JSON files, 36,450-row
tables, shard cohorts) are kept as GitHub release assets / archived
companion repositories, with their SHA-256 manifests recorded here.

---

## 3. Quick verification (a few minutes, no cluster)

```bash
git clone <this repo> && cd tii-26-7248-reproducibility
python -m pip install --require-hashes -r experiments/01_scalability_v6/code/requirements-v5.lock
# unit tests (67 tests: DBM/Fraction boundaries, component equivalence, families)
(cd experiments/01_scalability_v6/code && python -m unittest discover -s tests -p 'test_*.py')

# protocol integrity: unpack the frozen task grid and validate 8,280 tasks / 120 shards
tar -xzf experiments/01_scalability_v6/protocol/v6_formal_tasks.tar.gz -C experiments/01_scalability_v6/protocol
python experiments/01_scalability_v6/code/scripts/validate_v6_formal_protocol.py \
  --manifest experiments/01_scalability_v6/protocol/v6_formal_manifest.json \
  --tasks experiments/01_scalability_v6/protocol/v6_formal_tasks \
  --semantics-gate experiments/01_scalability_v6/protocol/v6_semantics_gate.json \
  --out /tmp/v6_validation.json

# recompute Figure 6 and the result tables from the checked-in statistics
python experiments/01_scalability_v6/code/scripts/plot_figure6_v6.py \
  --analysis-dir experiments/01_scalability_v6/results --out /tmp/v6_fig6
```

---

## 4. Full reproduction

| Experiment | Where it runs | Cost / time | Entry point |
|---|---|---|---|
| Scalability v6 (8,280 cells) | **Modal** CPU Functions (1 core, 4 GiB, 60 s/cell), 120 shards × 69 cells | measured **$5.53** total, ~2.5 h wall at 20 parallel | `experiments/01_scalability_v6/code/scripts/run_v6_modal.py` |
| Independent audit + statistics + Figure 6 | **GitHub Actions** | free, ~5 min | `.github/workflows` in the archived scalability repo; audit tool in `01.../code/scripts/audit_v6_modal_results.py` |
| Historical recompute (3,645) | **GitHub Actions** | free, 20 shards, ~40 min | archived `tii-26-7248-scalability-v2` workflow + `03_historical_audit/` |
| Verifier timing (36,450) | GitHub Actions | free, sharded | `04_verifier_timing/runner/` |
| H-sensitivity (16,038) | lab server + GitHub Actions | lab part done; 1,140 models sharded | `05_h_sensitivity/experiment/run_threshold.py` |
| Exhaustive baseline (16,038) | GitHub Actions | ~445 CPU-hours on the reference machine | `06_exhaustive_baseline/tools/` |
| Case studies | local / GitHub Actions | minutes | `07_case_studies/*/scripts` |

The paper's timings are only compared within one execution platform
(hardware-normalized); the scalability matrix was executed **only on Modal**.
See [`REPRODUCE.md`](REPRODUCE.md) for exact commands, seeds and budgets.

---

## 5. Data availability and provenance

* **Scalability v6 raw records** (8,280 JSON files + 120 shard ledgers,
  metrics and hash manifests) are published as the release asset
  `v6-formal-run-5038d2a9` in the archived repository (25.1 MB, SHA-256
  manifests inside). The checked-in `results/statistics.json` and
  `results/audit.json` are derived from those files.
* **Independent audit:** GitHub Actions run `42434059038` — PASS: 8,280 tasks,
  8,280 unique task ids, 120 shards, 0 technical failures, no findings.
* **Frozen protocol:** `experiments/01_scalability_v6/protocol/scalability_v6_frozen_protocol.{yaml,json}`
  (task grid SHA-256, image spec SHA-256, source commit, budget guard).
* **Execution environment:** Python 3.13, NumPy 2.3.4, SciPy 1.16.2,
  Modal 1.6.3, Debian slim image; see [`docs/`](docs).
* **Every result file** is covered by [`MANIFEST.sha256`](MANIFEST.sha256)
  at the repository root.

---

## 6. Archived companion repositories

This package consolidates the previously separate experiment repositories.
They remain public as archives with their full raw data:

| Archived repository | Content kept here |
|---|---|
| `tii-26-7248-scalability-v2` | v6 matrix, differential v2, historical audit, Modal execution |
| `tii-26-7248-verifier-timing` | `04_verifier_timing/` (curated subset) |
| `tii-26-7248-h-sensitivity` | `05_h_sensitivity/` (experiment code) |
| `tii-26-7248-exhaustive-full` | `06_exhaustive_baseline/` (tools, population, snapshot) |
| `tii-published-tpn-case-eval` | `07_case_studies/published_cases/` |
| `tii-illustrative-tpn-case` | `07_case_studies/illustrative/` |
| `tii-context-case-study` | `07_case_studies/context_dataset/` (reports + scripts) |
| `tii-26-7248-scalability-v3` | superseded by v6; kept only as history |
| `tii-industrial-versionb-study` | separate Version B study; intentionally **not** merged here |

---

## 7. Reviewer checklist (suggested)

1. `claims/claim_to_evidence.md` — every manuscript claim → file → verify command.
2. `claims/limitations.md` — right-censoring, INC semantics, censored heavy cells, counter-basis caveats.
3. `experiments/01_scalability_v6/results/audit.json` — independent audit PASS and exact task/shard counts.
4. `experiments/01_scalability_v6/results/FINAL_ACCEPTANCE_REPORT.md` — execution provenance and cost.
5. `experiments/02_cross_version_equivalence/` — semantic-equivalence evidence (no performance claim is made across versions).

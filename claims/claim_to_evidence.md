# Claim → evidence map

Each manuscript claim, the artifact that supports it, the checked-in file, and
the command a reviewer can run. All verification commands are read-only and need
no cloud resources.

| # | Manuscript claim | Artifact | Evidence file | Verify |
|---|---|---|---|---|
| C1 | The analysis is exact for strong-time Time Petri Nets: canonical normalization, soundness and completeness of the verifier | — | `experiments/01_scalability/protocol/semantics_gate.json`, `code/tests/`, `docs/execution_environment.md` | `(cd experiments/01_scalability/code && python -m unittest discover -s tests -p 'test_*.py')` |
| C2 | The bounded task-completion decision (H-bounded completion over L-bounded observable histories) is implemented exactly as specified | — | `experiments/01_scalability/code/`, `protocol/formal_task_manifest.json` (L, H per evaluation), `results/statistics.json` | `validate_formal_grid.py` + unit tests |
| C3 | Verdicts are three-valued and auditable: VER/AMB carry certificates, INC means completed-but-inconclusive, capped runs are censored | — | `results/statistics.json` (`censoring_note`, `failure_stage_distribution`), `claims/limitations.md` | inspect `statistics.json` |
| C4 | Scalability: the pre-registered 8,280-evaluation study completes with bounded cost and correct censoring discipline | Fig. 6 | `experiments/01_scalability/results/` (`statistics.json`, `figure6.*`, `audit.json`, `FINAL_ACCEPTANCE_REPORT.md`) | `plot_figure6.py`; audit PASS in `audit.json` |
| C5 | The optimized verifier is behaviourally equivalent to the reference implementation | — | `experiments/02_implementation_equivalence/` (`component_equivalence.json`, `sync_transition_equivalence.json`, `equivalence_acceptance_report.md`) | `evaluate_equivalence.py` → `EQUIVALENCE_ACCEPTED = GO` |
| C6 | Historical baseline verdicts are unchanged under the revised semantics | — | `experiments/06_historical_audit/summary.json`, `historical_baseline_report.md` | read `summary.json` (3,645/3,645, 0 verdict changes) |
| C7 | Per-case verifier runtimes are recoverable and consistent with the reported timing claims | Fig. 3 | `experiments/03_verifier_timing/results/`, `runner/` | `run_shard.py`; compare output columns |
| C8 | The ambiguity threshold `H_amb*/H_base` is well defined for every AMB evaluation | Ambiguity-horizon figure | `experiments/04_ambiguity_horizon/experiment/` | `run_threshold.py --help` and configuration |
| C9 | One-step exhaustive adjustment is a valid baseline on the full AMB population | Adjustment table | `experiments/05_exhaustive_baseline/` (population, tools, calibration) | `tools/make_shards.py` |
| C10 | The analysis and the adjustment replicate on independent published nets and a public industrial dataset | Case-study figures/tables | `experiments/07_case_studies/` | per-folder README |

## Evidence authority

* The independent audit (`experiments/01_scalability/results/audit.json`,
  GitHub Actions run `42434059038`) recomputes every hash and pre-registered field from
  the raw records; it is the authoritative integrity check.
* `results/statistics.json` is produced by the analysis pipeline from the raw
  records and is cross-checked against the audit.
* No result in this repository is edited by hand; every result file is produced
  by the scripts listed above and covered by `MANIFEST.sha256`.

## Note on machine-readable identifiers

`results/*.json` are machine-generated evidence and retain the identifiers of
the pre-registered protocol (evaluation identifiers, group labels, family
labels). The reader-facing documents in this repository describe the same
experiments with descriptive names; the mapping is unambiguous because the
protocol and the statistics share the identical label strings.

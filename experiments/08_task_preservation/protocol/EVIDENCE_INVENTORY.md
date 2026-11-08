# Phase 0 — evidence inventory and reconstructability

Read-only audit of the frozen adjustment study. No original file was modified.

## Verified frozen artifacts

| artifact | location | count | identity |
|---|---|---|---|
| AMB population | `firing_interval_adjustment/population/full_amb_population.csv.gz` | 16,038 unique evaluations | SHA-256 `7b0a1504…de63` (matches recorded meta) |
| CPG-LD full results | `results/full_adjustment_cpgld.csv.gz` | 16,038 records | 14,830 VERIFIED_SUCCESS / 1,202 TIMEOUT / 6 FINITE_SEARCH_FAILURE |
| Coquand full results | `results/full_adjustment_coquand.csv.gz` | 16,038 records | 9,097 / 6,455 NO_IMPROVING_CANDIDATE / 486 TIMEOUT |
| Exhaustive full results | `results/full_adjustment_exhaustive.csv.gz` | 16,038 records | 2,005 / 11,342 FINITE_SEARCH_FAILURE / 2,691 TIMEOUT |
| validation gate | `validation/full_adjustment_validation.json` | — | status counts, closures and L/H consistency match the result files |
| frozen source | `source_snapshot/` (205 files) | — | SHA-256 list `SNAPSHOT_SHA256.txt`; S5 regression below |
| run environment | `.venv` (Python 3.11.15, NumPy 2.4.6, SciPy 1.16.2) | — | recorded in `environment.txt` |

All three methods share the same frozen population and the same adjustment protocol
(`protocol_reconstruction.md`): extended domain, complete-set verification, 120 s verify /
300 s repair budget, objective O0, `ψ_task ≡ 1` (always true).

## Adjusted assignments: stored or reconstructable?

The result files and checkpoints store `final_model_hash`, `CI`, modified-transition counts and
statuses, but **not the adjusted interval assignments**. Reconstructability was tested by
rerunning the frozen per-case runner (`tools/run_case.py`) on a deterministic sample.

* sample: 4 successes per method (smallest recorded runtimes, spread over the parameter grid)
* result: **12/12 exact matches** on status, `final_model_hash`, `modified_transition_count` and `CI`
  (`results/determinism_probe.json`)
* conclusion: adjusted models are deterministically reconstructable from the frozen population,
  frozen source and recorded run configuration for the sampled cases; Phase A will require a full
  rerun because assignments are not persisted.

## Reference-execution evidence (S5 industrial case)

`TII_IndustrialTPN_VersionB_Final_Validated.zip` contains the frozen complete-set enumeration of
the industrial case (18 places / 16 transitions, L=10, H=60): 1,749 certificates yielding
**87 distinct normal** and **88 distinct fault** certificate sequences. The stored
`exact_sequence_preservation.json` reports exactly these counts and flags. Regression
`results/s5_reference_regression.json`: **PASS** (87/88 reproduced). The stored “complete witness”
fields are example complete executions, not certificate words; they are not used as the reference
set.

## Certificate-count distribution (predicate cost driver)

Distinct certificate sequences per successful evaluation can be large:

| method | n | median | P90 | P99 | max |
|---|---:|---:|---:|---:|---:|
| CPG-LD | 14,830 | 2 | 30 | 2,424 | 15,856 |
| Coquand | 9,097 | 1 | 2 | 5,084 | 15,360 |
| Exhaustive | 2,005 | 1 | 1 | 2,128 | 5,084 |

A predicate over *all* certificate sequences would need millions of path-feasibility LPs.
The protocol therefore uses a deterministic, frozen sample of the reference set (see
`PROTOCOL_DRAFT.md`), with a full-set check only where the certificate count is small.

## Known data issue (recorded, not used)

A GitHub-actions artifact aggregation of the exhaustive method (collected during an unrelated
packaging task) reports 2,001 successes and 40 ERROR records, inconsistent with the frozen local
result file (2,005 successes, 0 ERROR). The **frozen local result files and validation gate are
authoritative** for this task; the artifact aggregation is excluded and recorded as an inconsistency.

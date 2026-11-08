# Experiment 08 — non-trivial task-preservation constraints (R3-2)

Independent verification for Reviewer 3, Comment 2 of TII-26-7248: what do the
existing firing-interval adjustment methods achieve when a non-trivial
task-preservation predicate is actually enforced, and what can the authorized
timing domains support physically?

This folder contains the frozen inputs, the predicate implementation, the
tests, the frozen pilot manifest and the GitHub Actions workflows. The original
full-population adjustment records (16,038 evaluations per method) are copied
here read-only for verification; no original file is modified.

## Stage

Phase 0 complete (evidence inventory, reconstructability, S5 reference
regression). Predicate implementation and unit tests complete locally
(6 real models, lost-path rejection, tolerance tiers). The 10% stratified pilot
(GitHub Actions) is the next step after the Linux compatibility job passes.

## Files

```
protocol/PROTOCOL_DRAFT.md       predicate definition, reference-set rule, phases, budget
protocol/EVIDENCE_INVENTORY.md   frozen evidence, hashes, gaps
protocol/pilot_manifest.json     frozen 10% stratified pilot cells (evaluation-ID sampled)
protocol/s5/                     S5 industrial complete-set enumeration + stored evidence
code/frozen_src/src/             frozen adjustment/verifier source (read-only)
code/predicate.py                psi_path / psi_perf implementation
code/tests_unit.py               predicate unit tests (real frozen models)
code/s5_regression.py            S5 regression (87 normal / 88 fault)
code/evidence_inventory.py       frozen-evidence verification
code/determinism_probe.py        reconstruction determinism probe
code/compat_probe.py             cross-platform compatibility probe
code/run_case_audit.py           reconstruct one case + evaluate predicate
code/run_pilot_shard.py          pilot shard driver
code/build_pilot_manifest.py     pilot manifest builder
code/aggregate_audit.py          pilot aggregation audit
data/frozen/                     population, three method result files, validation gate
```

## Workflow

`.github/workflows/r3_2_phaseA_pilot.yml`:
1. `compatibility` — Linux: pinned Python/deps, predicate tests, S5 regression,
   evidence inventory, reconstruction probe (3 frozen successes per method).
2. `pilot` — 4-way parallel shard matrix over the frozen manifest (manual input).
3. `audit` — independent aggregation: missing / duplicate / reconstruction
   mismatch / predicate-consistency checks.

## Current frozen numbers

* population 16,038; original successes: CPG-LD 14,830, Coquand 9,097, exhaustive 2,005.
* pilot manifest: 1,942 evaluation IDs (12.1% after per-stratum rounding), 771 strata,
  SHA-256 in `protocol/pilot_manifest.sha256`.
* local predicate tests: PASS; S5 regression: PASS (87/88); determinism probe: 12/12 exact.

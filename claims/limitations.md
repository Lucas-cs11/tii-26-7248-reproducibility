# Limitations, censoring rules and honest caveats

Reviewers should read this before comparing numbers across figures.

## Measurement discipline

* **Right-censoring.** A cell that hits the 60 s wall-clock cap is reported as
  `TIMEOUT_WALL_CLOCK`; it is never imputed as a completion and never used in
  time quantiles. Time P50/P90/P95 use COMPLETED cells only, with the observed
  n printed next to them.
* **INC is not a timeout.** `INC` means the run completed but the analysis
  report is inconclusive (e.g. `SCG_STATE_LIMIT`); it is reported in its own
  denominator and never merged into VER/AMB.
* **Platform normalization.** The formal scalability matrix was executed
  **only on Modal** (1 physical core, 4 GiB, Debian slim, Python 3.13, NumPy
  2.3.4, SciPy 1.16.2). Timings are never pooled with GitHub Actions or
  lab-machine timings.
* **Censored cells in the equivalence study.** In differential v2, 3 of 48
  cells (`F06/F09/F12`, `L_high_complete`) cannot have their synchronizer
  automaton built within the 900 s budget and are censored with explicit
  reasons; they are not counted as passes. 18 of the 48 v1 pairs are censored
  (11 baseline-timeout/optimized-completed, 7 both-timeout) and stay in the
  denominator.

## Experiment-specific caveats

* **Historical baseline.** The archived v4-era records do not persist a `mode`
  column (FIRST_CERTIFICATE is the documented assumption) and their
  critical-pair counter is not definitionally identical to the v6 counter
  (archived: complete v4 enumeration; recomputed: `terminal_pairs +
  enclosure_rejected_pairs`). The report compares them explicitly and reports
  the LP-feasible certificate count separately. The MSCG-LP reference re-run is
  planned only and reuses the shared SCG builder, so it is **not** an
  independent SCG oracle.
* **Exhaustive baseline.** The ~445 CPU-hour figure is for the reference Apple
  M4 machine; GitHub runners are slower and the timeout budget is scaled by the
  measured runner/reference speed ratio so each case receives the same amount
  of computation, not the same wall clock.
* **H-sensitivity.** 14,898 of 16,038 models were completed on the lab
  machine/server before archiving; the remaining 1,140 are defined as frozen
  cohorts. Results from the two parts are not mixed in the paper's threshold
  statistic without the documented cohort separation.
* **Case studies.** The public context dataset (Kaupp et al., Zenodo 4034867)
  is licensed CC BY-NC 4.0 and is **redistributed only through its original
  source**; this repository ships scripts and reports, not the dataset.
* **Version B.** The industrial TPN Version B study is a separate line of work
  (archived repository `tii-industrial-versionb-study`). It is intentionally not
  merged here and no claim in this package depends on it.
* **Raw data size.** The 8,280 raw records, 36,450-row timing table and the
  full experiment shards are not stored in git; they are published as release
  assets / archived repositories, with SHA-256 manifests recorded in this
  package.

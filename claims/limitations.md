# Limitations and measurement rules

Read this before comparing numbers across figures.

## Measurement discipline

* **Wall-clock caps.** An evaluation that reaches its 60 s cap is reported as
  capped (`TIMEOUT_WALL_CLOCK` in the machine-readable files). It is never
  imputed as a completion and never enters a time quantile. Time statistics use
  completed evaluations only and print the observed count next to each value.
* **Inconclusive outcomes are a separate class.** `INC` means the run completed
  but the analysis is inconclusive (for example, the state-class limit was
  reached). INC has its own denominator and is never merged into VER/AMB.
* **One platform per comparison.** The scalability study was executed only on
  Modal CPU workers (1 physical core, 4 GiB, Python 3.13, NumPy 2.3.4,
  SciPy 1.16.2). Its timings are never pooled with GitHub Actions or
  lab-machine measurements.
* **Unrunnable heavy evaluations in the equivalence study.** Three of the 48
  paired evaluations cannot build the full observation synchronizer within the
  900 s budget and are censored with explicit reasons; they are not counted as
  equivalent. In the end-to-end layer, 18 of 48 pairs are censored (11 where the
  reference implementation capped but the optimized one completed, 7 where both
  capped) and remain in the denominator.

## Experiment-specific caveats

* **Historical baseline.** The archived records predate the revised semantics
  and do not store the certificate mode (first-certificate is the documented
  assumption). Their critical-pair counter is not definitionally identical to
  the current counter: the archived value is a complete enumeration under the
  old semantics, the recomputed value is the current terminal-pair counter plus
  enclosure-rejected pairs. The report compares them explicitly and reports the
  LP-feasible certificate count separately. The reference-baseline re-run is
  planned only and reuses the shared SCG builder, so it is not an independent
  oracle.
* **One-step exhaustive baseline.** The ≈445 CPU-hour figure refers to the
  reference Apple M4 machine. GitHub runners are slower; the timeout budget is
  scaled by the measured runner/reference speed ratio so that each evaluation
  receives the same amount of computation, not the same wall-clock.
* **Ambiguity horizon.** 14,898 of the 16,038 models were completed on the lab
  machine/server before archiving; the remaining 1,140 are defined as fixed
  cohorts. The paper does not mix the two parts without the documented cohort
  separation.
* **Context dataset.** The Kaupp et al. dataset (Zenodo 4034867) is licensed
  CC BY-NC 4.0 and is redistributed only through its original source; this
  repository ships scripts and reports, not the dataset.
* **Version B industrial study.** The industrial Time Petri Net “Version B”
  study is a separate line of work and is intentionally not part of this
  package; no claim here depends on it.
* **Raw data size.** The 8,280 raw records, the 36,450-row timing table and the
  full partition/cohort files are not stored in git. They are published as
  release assets in the archived companion repositories, with SHA-256 manifests
  recorded here.

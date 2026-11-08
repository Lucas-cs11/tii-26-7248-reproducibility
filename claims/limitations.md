# Measurement rules and limitations

## Measurement discipline

* **Wall-clock caps.** An evaluation that reaches its 60 s cap is reported as
  capped and never imputed as a completion; it never enters a time quantile.
* **Inconclusive outcomes are a separate class.** `INC` means the run completed
  but the analysis is inconclusive (for example, the state-class limit was
  reached). INC has its own denominator and is never merged into VER/AMB.
* **One platform per comparison.** The scalability study was measured on one
  cloud CPU platform only; its timings are never pooled with other platforms.
* **Unrunnable heavy evaluations in the equivalence study.** Three of the 48
  paired evaluations cannot build the full observation synchronizer within the
  900 s budget and are censored, not counted as equivalent; in the end-to-end
  layer, 18 of 48 pairs are censored and stay in the denominator.

## Experiment-specific caveats

* **Historical baseline.** The archived records predate the revised semantics
  and do not store the certificate mode (first-certificate is the documented
  assumption). Their critical-pair counter is not definitionally identical to
  the current counter: the archived value is a complete enumeration under the
  old semantics, the recomputed value is the current terminal-pair counter plus
  enclosure-rejected pairs. The report compares them explicitly and reports the
  LP-feasible certificate count separately. The reference-baseline re-run is
  planned only and reuses the shared state-class builder, so it is not an
  independent oracle.
* **One-step exhaustive baseline.** The ≈445 CPU-hour figure refers to the
  reference Apple M4 machine; on GitHub runners the timeout budget is scaled by
  the measured speed ratio so each evaluation receives the same amount of
  computation, not the same wall clock.
* **Ambiguity horizon.** 14,898 of the 16,038 models were completed on the lab
  machine/server; the remaining 1,140 are fixed cohorts. The two parts are not
  mixed without the documented cohort separation.
* **Context dataset.** The Kaupp et al. dataset (Zenodo 4034867) is licensed
  CC BY-NC 4.0 and is redistributed only through its original source; this
  repository ships scripts and reports, not the dataset. The study finds the
  archive insufficient for a task-completion case; that negative outcome is
  reported as a result.
* **Raw data size.** The 8,280 raw scalability records, the full adjustment
  rows and the cohort files are provided as release assets alongside this
  package; the repository keeps the pre-registered protocols, the execution
  code and the result summaries.

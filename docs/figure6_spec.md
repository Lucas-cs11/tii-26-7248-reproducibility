# Figure 6 specification

Figure 6 reports the scalability of the bounded-diagnosability analysis on the
pre-registered 8,280-evaluation study.

## Panels

* **(a) Structural size.** Analysis time per completed evaluation (state-class
  construction plus verification) against model size (places + transitions) for
  the structural-size group (600 evaluations). Wall-clock-capped evaluations are
  drawn at the cap as hollow triangles and are excluded from the time quantiles;
  the rank correlation is computed on completed evaluations only.
* **(b) Work-in-process sensitivity.** Paired trajectories of the same base
  model at work-in-process bounds 1, 2 and 3 (1,080 evaluations). Thin grey
  segments connect completed evaluations of one base model; the black line is
  the median over completed evaluations at each bound. A pair with a capped
  member only provides a lower bound and is never used as a measured ratio.
* **(c) Observable-history bound L.** Retained-history workload as L increases
  on fixed models (5,400 evaluations). Filled markers indicate evaluations that
  genuinely become L-sensitive (the candidate-word set appears); the panel
  shows onset and plateau. Capped evaluations are drawn at the cap.

## Counting rules

* Denominators are printed inside each panel (total, completed, capped, INC).
* Time quantiles use completed evaluations only.
* INC (completed but inconclusive) is its own class and is drawn at its real
  runtime with a hollow diamond.
* Capped evaluations are right-censored at the cap; they are never imputed as
  completions and never enter a quantile.

## Colors and data

* Colors encode instance groups, consistently across panels.
* Every plotted number is recomputable from
  `experiments/01_scalability/results/statistics.json`; the plotting data are
  shipped as `figure6_data.csv` and the exact rendering metadata as
  `figure6_metadata.json`.

## Reviewer checklist for this figure

1. Do the panel denominators match `statistics.json`?
2. Are capped evaluations shown at the cap and excluded from quantiles?
3. Are INC evaluations visible and separate from both VER/AMB and capped runs?
4. Is the paired WIP growth computed only from pairs where both sides completed?
5. Does the number of L-sensitive models match the candidate-word onsets in
   `statistics.json`?

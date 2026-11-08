# Figure 6 specification

* **(a) Structural size.** Analysis time per completed evaluation against model
  size (places + transitions) for the structural-size group (600 evaluations);
  capped evaluations are drawn at the cap and excluded from the quantiles; the
  rank correlation is computed on completed evaluations only.
* **(b) Work-in-process sensitivity.** Paired trajectories of the same base
  model at bounds 1, 2 and 3 (1,080 evaluations); the median line uses completed
  evaluations; a pair with a capped member only provides a lower bound.
* **(c) Observable-history bound L.** Retained-history workload as L increases
  on fixed models (5,400 evaluations); filled markers mark evaluations that
  genuinely become L-sensitive; the panel shows onset and plateau.

Counting rules: denominators are printed in each panel; time quantiles use
completed evaluations only; INC is its own class; capped evaluations are
right-censored and never imputed.

All plotted numbers are recomputable from
`experiments/01_scalability/results/statistics.json`; the plotting data are in
`results/figure6_data.csv`.

# Experiment 04 — ambiguity-horizon sensitivity

For every AMB model of the frozen baseline population (16,038 models) the
experiment computes the ambiguity threshold `H_amb*/H_base`: the smallest
H-normalized horizon at which the verdict becomes AMB, with an epsilon
re-check on both sides of the threshold.

14,898 models were completed on the lab machine/server; the remaining 1,140 are
defined as fixed cohorts and computed on GitHub-hosted runners. The per-model
protocol (analysis budget, status vocabulary, threshold method) is unchanged
between the two parts.

## Contents

* `experiment/` — fixed implementation (`run_threshold.py`,
  `h_sensitivity_config.json`, analysis and cohort preparation scripts,
  `src/` snapshot).
* The 40 cohort files (1,140 models) and the lab-completed results remain in the
  archived companion repository.

## Reproduce

```bash
python experiment/run_threshold.py --help
```

The configuration fixes the analysis budget and the bisection/epsilon
parameters; changing them changes the experiment and must be reported as a
protocol change, not as a reproduction.

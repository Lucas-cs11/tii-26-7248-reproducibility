# Experiment 04 — ambiguity-horizon sensitivity

For each AMB model of the pre-registered baseline population the experiment computes
the ambiguity threshold `H_amb*/H_base`: the smallest H-normalized horizon at
which the verdict becomes AMB, with an epsilon re-check on both sides.

## Result (available artifact coverage)

| metric | value |
|---|---:|
| models covered by the archived run artifacts | 4,068 |
| (model, H-ratio) evaluations | 20,340 |
| completed / wall-clock-capped | 18,194 / 2,146 |
| completed verdicts | AMB 18,194 |
| threshold `H_amb*/H_base` | P05 0.141, P25 0.197, median 0.231, P75 0.282, P95 0.333; range 0.141–0.394 |

The fixed population contains 16,038 AMB models; the archived run artifacts
recovered for this package cover the 4,068 models listed above. The remaining
lab-completed part is not redistributed.

## Contents

* `experiment/` — fixed implementation (`run_threshold.py`,
  `h_sensitivity_config.json`, cohort preparation and analysis scripts, source
  snapshot).
* `cohorts/index.json` — cohort definition index (the cohort CSVs remain in the
  archived companion repository).
* `results/threshold_summary.json` — the aggregate above.

## Reproduce

```bash
python experiment/run_threshold.py --help
```

The configuration fixes the analysis budget and the bisection/epsilon
parameters; changing them changes the experiment and must be reported as a
protocol change, not as a reproduction.

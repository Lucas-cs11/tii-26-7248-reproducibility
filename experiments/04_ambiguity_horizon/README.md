# Experiment 04 — ambiguity-horizon sensitivity

For each AMB model the experiment computes the ambiguity threshold
`H_amb*/H_base`: the smallest H-normalized horizon at which the verdict becomes
AMB, with an epsilon re-check on both sides of the threshold.

## Result

| metric | value |
|---|---:|
| models with result rows (population: 16,038) | 15,288 |
| (model, H-ratio) evaluations | 76,440 |
| completed / wall-clock-capped | 74,294 / 2,146 |
| completed verdicts | AMB 74,294 |
| threshold `H_amb*/H_base` | P05 0.167, P25 0.231, median 0.278, P75 0.313, P95 0.394; range 0.141–0.394 |

The fixed population contains 16,038 AMB models; the recovered run artifacts
cover the 4,068 models above.

## Files

* `experiment/` — fixed implementation (`run_threshold.py`,
  `h_sensitivity_config.json`, cohort preparation and analysis scripts).
* `cohorts/index.json` — cohort definition index.
* `results/threshold_summary.json` — the aggregate above.

## Reproduce

```bash
python experiment/run_threshold.py --help
```

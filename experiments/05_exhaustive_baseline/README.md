# Experiment 05 — one-step exhaustive adjustment baseline

Runs the one-step exhaustive firing-interval adjustment baseline over the full
16,038-evaluation AMB population of the frozen benchmark.

## Result (complete population)

| status | evaluations |
|---|---:|
| VERIFIED_SUCCESS | 2,001 |
| FINITE_SEARCH_FAILURE | 11,314 |
| TIMEOUT | 2,683 |
| ERROR | 40 |
| **total** | **16,038** |

Sum of the per-partition runtimes reported by the archived jobs: ≈72.6 hours
on the GitHub-hosted runners (the jobs ran in parallel). Success requires VER
**and** an empty certificate set after a fresh complete-set re-verification;
nothing else is counted as success.

## Method

1. regenerate the Time Petri Net with the pre-registered L and H from the
   population;
2. verify the evaluation; it must return AMB;
3. run the exhaustive repair over the authorized Cartesian product
   (`max_scope_combinations = 200,000`);
4. re-verify the returned model with the complete-set analysis.

## Contents

* `population/full_amb_population.csv.gz` — fixed 16,038-evaluation AMB
  population.
* `shards/index.json` — the 32-partition plan used by the archived runs.
* `tools/` — sharding, benchmark calibration and run tools.
* `shards/calib.json` — calibration sample.
* `results/adjustment_summary.json` — the status aggregate above.

# Experiment 05 — one-step exhaustive adjustment baseline

Runs the one-step exhaustive firing-interval adjustment baseline over the full
16,038-evaluation AMB population of the pre-registered benchmark.

Method (identical to the reference protocol):
1. regenerate the Time Petri Net with the pre-registered L and H from the population;
2. verify the model; the evaluation must return AMB;
3. run the exhaustive repair over the authorized Cartesian product
   (`max_scope_combinations = 200,000`);
4. **freshly** re-verify the returned model with the complete-set analysis;
   success requires VER **and** an empty certificate set. Nothing else is ever
   reported as success.

Status vocabulary: `VERIFIED_SUCCESS`, `FINITE_SEARCH_FAILURE`, `INC`,
`TIMEOUT`, `ERROR`, `VALIDATION_FAILURE`.

## Contents

* `population/full_amb_population.csv.gz` — fixed 16,038-evaluation AMB
  population.
* `tools/` — sharding, benchmark calibration and run tools.
* `shards/calib.json` — 40-case calibration sample.
* The 40 full-run partitions remain in the archived companion repository.

## Cost

≈445 CPU-hours on the reference Apple M4 machine. The workload is
embarrassingly parallel; on GitHub runners the timeout budget is scaled by the
measured runner/reference speed ratio so each evaluation receives the same
amount of computation.

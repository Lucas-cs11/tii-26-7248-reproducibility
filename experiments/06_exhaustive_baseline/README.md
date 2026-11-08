> **Package note.** This folder is a curated subset of the archived repository
> `tii-26-7248-exhaustive-full`. Kept here: frozen population (16,038 AMB
> evaluations), sharding/benchmark tools, source snapshot and the 40-case
> calibration sample. The 40 full-run shard results remain in the archived
> repository.

# TII-26-7248 — full-population one-step exhaustive adjustment (GitHub Actions compute)

This repository runs the **one-step exhaustive** adjustment baseline of

> *Bounded Task-Completion Diagnosability of Time Petri Nets: Verification and Firing-Interval Adjustment*
> (IEEE Transactions on Industrial Informatics, TII-26-7248)

over the **full 16,038-evaluation AMB population** of the frozen baseline verification benchmark.

## Why GitHub Actions

The exhaustive baseline is the dominant runtime of the revision experiment (~445 CPU-hours on the
reference Apple M4 machine). The workload is embarrassingly parallel — every evaluation is an
independent process with no shared state — so it is sharded across GitHub-hosted runners.
Shards are merged locally afterwards; the merge key is `(evaluation_id, method)`.

## Method (identical to the local protocol, `protocol_reconstruction.md` §6)

For each evaluation:
1. regenerate the TPN with `repair_domain="extended"` and the frozen `L`, `H` from the population;
2. run `verify(tpn, L, H, complete_set=True)` — the case must return AMB;
3. run `exhaustive_repair(...)` over the authorized Cartesian product (`max_scope_combinations=200_000`);
4. **fresh** complete-set re-verification of the returned model; success requires `VER` **and** an empty
   certificate set. Anything else is never reported as success.

Status vocabulary: `VERIFIED_SUCCESS`, `FINITE_SEARCH_FAILURE`, `INC`, `TIMEOUT`, `ERROR`, `VALIDATION_FAILURE`.

### Timeout calibration

The reference protocol uses 120 s (complete verification) / 300 s (search) on the M4 machine.
GitHub runners are slower; both budgets are scaled by the measured runner/M4 speed ratio so that each
case receives the **same amount of computation**, not the same wall-clock. `tools/gh_bench.py` prints the
ratio for every job, and it is recorded in the job log.

## Layout

```
population/full_amb_population.csv.gz   16,038 frozen AMB evaluations (sha256 in the local archive)
shards/calib.json                        40-case calibration sample
shards/shard_NNN.json                    full-run shards (generated with tools/make_shards.py)
source_snapshot/src/                     frozen verifier / repair implementation
tools/run_case.py                        one (evaluation, method) -> one JSON record
tools/run_full_adjustment.py             shard driver with checkpointing
tools/gh_bench.py                        runner speed benchmark
tools/make_shards.py                     shard generator
```

## How to run

Actions → **exhaustive** → *Run workflow*:

| input | calibration | full run |
|---|---|---|
| `mode` | `calib` | `full` |
| `workers` | 4 | 4 |
| `verify_timeout` | 240 | calibrated |
| `repair_timeout` | 900 | calibrated |

Each shard uploads `exhaustive-shard-<k>-<run_id>` as an artifact (JSONL records).

## Notes

* Code and data are published here solely to make the reported experiment reproducible; the results are
  merged and validated locally before being reported in the paper.
* No personal data is contained in this repository.

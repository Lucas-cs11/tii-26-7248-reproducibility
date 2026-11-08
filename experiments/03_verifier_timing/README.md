# Experiment 03 — per-case verifier runtimes (Fig. 3)

Per-evaluation runtimes of the verifier on the fixed 36,450-evaluation
benchmark: 255 worker partitions × 143 evaluations, three repetitions per
evaluation, method `main`, 60 s cap per evaluation.

## Result

| metric | value |
|---|---:|
| evaluations | 36,450 |
| completed | 36,450 |
| verdicts | VER 20,412 / AMB 16,038 |
| median runtime | 8.1 ms |
| P90 / P95 / P99 | 107 ms / 924 ms / 2.60 s |
| maximum runtime | 5.59 s |

Timings are comparable only within this execution platform.

## Files

* `driver/run_one.py`, `driver/run_shard.py` — measurement path and partition
  driver.
* `results/timing_summary.json` — counts and runtime quantiles.
* `results/timing_all_rows.csv.gz` — all 36,450 per-evaluation rows.
* `results/shard_000.csv` — one example partition in plain CSV.

## Reproduce

```bash
python driver/run_shard.py --shard 000 --out results/
```

The verifier implementation is `../01_scalability/code/src/`.

# Experiment 03 — per-case verifier runtimes (Fig. 3)

Per-evaluation runtimes of the verifier on the fixed 36,450-evaluation
benchmark (255 worker partitions × 143 evaluations, three repetitions per
evaluation, method `main`, 60 s cap per evaluation), measured on GitHub Actions.

## Result

| metric | value |
|---|---:|
| evaluations | 36,450 |
| completed | 36,450 (0 wall-clock-capped, 0 errors) |
| verdicts | VER 20,412 / AMB 16,038 |
| median runtime | 8.1 ms |
| P90 / P95 / P99 | 107 ms / 924 ms / 2.60 s |
| maximum runtime | 5.59 s |

Timings are only compared within this execution platform. The distribution is
right-skewed; the reported quantiles are computed over all completed
evaluations.

## Contents

* `driver/run_one.py`, `driver/run_shard.py` — measurement path and partition
  driver.
* `results/timing_summary.json` — counts and runtime quantiles.
* `results/timing_all_rows.csv.gz` — all 36,450 per-evaluation rows
  (evaluation identifier, verdict, status, model hash, L, H, runtime total,
  median over repeats, repeats, warm-up count, error, expected hash/L/H).
* `results/shard_000.csv` — one example output partition in plain CSV.

## Reproduce

```bash
python driver/run_shard.py --shard 000 --out results/
```

The verifier implementation is the one shipped in
`../01_scalability/code/src/`; the frozen evaluation list is in the archived
companion repository `tii-26-7248-verifier-timing`.

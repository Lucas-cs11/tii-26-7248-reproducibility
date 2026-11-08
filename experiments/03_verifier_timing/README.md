# Experiment 03 — per-case verifier runtimes (Fig. 3)

Per-evaluation runtimes of the verifier on the fixed 36,450-evaluation
benchmark: 255 worker partitions × 143 evaluations, three repetitions per
evaluation, method `main`, 60 s cap per evaluation.

The measurement recovers the per-case timing table that is summarized in
Fig. 3 and in the timing claims of the manuscript.

## Contents

* `runner/run_one.py` — faithful copy of the measurement path used for the
  reported timings.
* `runner/run_shard.py` — partition driver; writes `results/shard_NNN.csv`.
* `src/` — verifier snapshot used for the measurement.
* `results/shard_000.csv` — one example output partition (the full 255-partition
  output remains in the archived companion repository).

## Reproduce

```bash
python runner/run_shard.py --shard 000 --out results/
```

Output columns: evaluation identifier, verdict, execution status, model hash,
L, H, total runtime, median runtime, repetitions, warm-up count, error, expected
hash, expected L, expected H.

## Note

The full evaluation list (255 partitions) and the complete output remain in the
archived companion repository `tii-26-7248-verifier-timing`; this folder keeps
the measurement code and one example partition so the format and the procedure
are auditable without shipping several megabytes of timing rows.

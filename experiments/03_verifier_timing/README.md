# Experiment 03 — per-case verifier runtimes (Fig. 3)

Per-evaluation runtimes of the verifier on the fixed 36,450-evaluation
benchmark: 255 worker partitions x 143 evaluations, three repetitions per
evaluation, method `main`, 60 s cap per evaluation.

The measurement recovers the per-case timing table summarized in Fig. 3 and in
the timing claims of the manuscript.

## Contents

* `driver/run_one.py` — measurement path used for the reported timings.
* `driver/run_shard.py` — partition driver; writes `results/shard_NNN.csv`.
* `results/shard_000.csv` — one example output partition. The complete
  255-partition output remains in the archived companion repository.

## Reproduce

```bash
python driver/run_shard.py --shard 000 --out results/
```

Output columns: evaluation identifier, verdict, execution status, model hash,
L, H, total runtime, median runtime, repetitions, warm-up count, error, expected
hash, expected L, expected H. The verifier implementation itself is the one
shipped in `../01_scalability/code/src/`.

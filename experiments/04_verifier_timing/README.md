> **Package note.** This folder is a curated subset of the archived repository
> `tii-26-7248-verifier-timing` (Fig. 3 experiment). Kept here: runner, verifier
> source, one example result shard, README. The full 255-shard instance set and
> outputs remain in the archived repository; this folder is enough to run the
> measurement and inspect the output format.

# Verifier timing re-run (TII-26-7248, Figure 3)

Re-runs the proposed verifier on the frozen 36,450-evaluation benchmark to recover
per-case runtimes, because the original per-case timing file was overwritten by a
dry-run placeholder in the manuscript workspace.

- instances/: 255 shards x 143 model records (model_id, parameters, L, H, expected model hash, expected verdict)
- runner/run_one.py: faithful copy of the archived measurement path (method "main", warmup 0, repeats 3)
- runner/run_shard.py: 60 s per-case timeout, writes results/shard_NNN.csv
- src/: verifier source, unchanged

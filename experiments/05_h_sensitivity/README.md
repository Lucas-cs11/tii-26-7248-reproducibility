> **Package note.** This folder is a curated subset of the archived repository
> `tii-26-7248-h-sensitivity`. Kept here: the frozen threshold implementation,
> configuration and analysis scripts. The 40 cohort CSVs (1,140 models) and the
> lab-completed part (14,898 models) remain in the archived repository.

# TII-26-7248 — H-sensitivity threshold experiment (GitHub Actions compute)

Companion repository for the H-sensitivity experiment of
*Bounded Task-Completion Diagnosability of Time Petri Nets: Verification and Firing-Interval Adjustment* (IEEE TII, TII-26-7248).

For each baseline-AMB model (16,038 in total) the experiment computes the ambiguity threshold
`H_amb* / H_base`, i.e. the smallest H-normalised horizon at which the verdict becomes AMB,
with an epsilon re-check on both sides of the threshold.

14,898 models were completed on the lab machine / server; the remaining **1,140** are sharded in
`cohorts/` (40 shards, ~28 models each) and computed on GitHub-hosted runners. The per-model
protocol (analysis budget, statuses, threshold method) is unchanged.

## Layout
```
experiment/            frozen implementation (src/, run_threshold.py, config)
cohorts/shard_NNN.csv  1,140 remaining models, 40 shards
cohorts/index.json     shard index
.github/workflows/threshold.yml
```

## Run
Actions → **threshold** → Run workflow: `mode=smoke` (5 cases) or `mode=full` (all shards).
Each shard uploads `results/shard_NNN.csv` as an artifact.

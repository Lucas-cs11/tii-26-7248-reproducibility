# Experiment 06 — historical-baseline audit (3,645 evaluations)

The paper modifies the semantics of state-class construction and of the
completion analysis. This audit establishes that the archived baseline verdicts
are unchanged: a fixed sample of the archived baseline is recomputed with the
current implementation, independently of the new scalability study.

## Result

| item | value |
|---|---:|
| recomputed evaluations | 3,645 (555 bounded problems; VER 1,689 / AMB 1,956) |
| primary pass completed | 3,645 / 3,645 (100 %) |
| **verdict changes** | **0** (VER 1,689→1,689, AMB 1,956→1,956; 0 INC, 0 undecidable) |
| full second pass (archived AMB) | 1,956 / 1,956 (1,136 completed, 820 wall-clock-capped) |
| critical-pair comparison (AMB rows) | archived mean 68,224.5 vs recomputed 2,457.3 pairs; 274 increased / 862 decreased; median ratio 0.149 |
| certificate overlap inside the archived window | 1,136 / 1,136 |

## Files

* `summary.json` — final aggregate of the sharded run (20 partitions, 60 s per
  evaluation, no retries of mathematical timeouts).
* `coverage.json`, `shard_manifest.json` — per-partition accounting.
* `historical_baseline_report.md` — full report, including the documented
  counter-definition caveat and the planned-only reference re-run.

## Scope

This is an add-on audit: it is disjoint from the 8,280-evaluation scalability
study, does not share its budget, and its numbers are never pooled with it.

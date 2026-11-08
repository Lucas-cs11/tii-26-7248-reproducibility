# Experiment 03 — historical baseline audit (3,645 evaluations)

The paper's semantic changes could in principle alter archived verdicts. This
audit recomputes a frozen sample of the archived v4-era baseline under the v6
semantics, independently of the new scalability matrix.

## Result

| item | value |
|---|---:|
| frozen evaluations | 3,645 (555 bounded problems; VER 1,689 / AMB 1,956) |
| primary pass recorded | 3,645 / 3,645 (100 %) |
| **verdict drift** | **0** (VER 1,689→1,689, AMB 1,956→1,956; 0 INC, 0 not-decidable) |
| COMPLETE_SET second pass (archived AMB) | 1,956 / 1,956 (1,136 completed, 820 right-censored) |
| critical-pair comparison (AMB rows) | archived mean 68,224.5 vs recomputed 2,457.3 pairs; 274 increased / 862 decreased; median ratio 0.149 |
| certificate overlap inside archived [L,H] | 1,136 / 1,136 |

## Files

* `summary.json` — final aggregate from the GitHub Actions sharded run
  (20 shards, 60 s per task, no retries of mathematical timeouts).
* `coverage.json`, `shard_manifest.json` — per-shard accounting.
* `v6_historical_recompute_report.md` — full report, including the documented
  counter-basis caveat and the (planned-only) MSCG-LP reference re-run.

## Reproduce

The frozen manifest and the sharded workflow are in the archived scalability
repository; the workflow is deterministic (task index modulo shard count). The
report lists the exact commands and the 97,962.6 s reference estimate.

## Scope

This is an add-on audit: it is disjoint from the 8,280-cell matrix, does not
share its budget and its numbers are never pooled with it.

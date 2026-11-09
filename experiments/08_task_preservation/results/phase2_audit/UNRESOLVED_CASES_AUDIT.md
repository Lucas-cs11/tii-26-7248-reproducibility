# Unresolved cases audit (338 records)

## Classification

| Original status | Count | Classification |
|---|---:|---|
| TIMEOUT | 336 | originally_timeout_compute_limit |
| VERIFIED_SUCCESS | 2 | originally_successful_compute_limit |

All 338 records are `INFRA_TIMEOUT_OR_ERROR`: the shard driver's hard subprocess
timeout (~840 s) was exceeded. None is a task-preservation failure; all are
compute-limited and must not be interpreted as adjustment method failures.

## Two originally-successful cases

| Case | Method | Original runtime | Cause |
|---|---|---:|---|
| `fs_m3_j2_k2_w2_ur30_fl4_wf10_ar10_s11` | cpgld | 1,511 s | Subprocess timeout (~840 s < needed 1,511 s) |
| `fs_m4_j2_k2_w2_ur30_fl2_wf15_ar25_s1` | cpgld | 965 s | Subprocess timeout (~840 s < needed 965 s) |

Both had very long original runtimes that exceed the shard driver's hard limit.
They are compute-limited, not method failures. Targeted re-execution with a
longer limit (~2,000 s) would resolve them.

## Recommended action

The 336 originally-TIMEOUT cases do not warrant re-execution (they are the
hardest instances and the original timeouts are the correct result under the
frozen protocol). The 2 originally-successful cases could be resolved with
two single-case re-executions at ~2,000 s budget each.

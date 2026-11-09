# Unresolved cases audit (338 records → 336 remaining, 2 resolved)

## Classification

| Original status | Count | Classification | Status |
|---|---:|---|---|
| TIMEOUT | 336 | originally_timeout_compute_limit | unresolved (expected) |
| VERIFIED_SUCCESS | 2 | originally_successful_compute_limit | **resolved by targeted re-execution** |

## Two originally-successful cases — RESOLVED

| Case | Original runtime | Re-execution | hash_match | fresh | path_pass | ψ@0% | ψ@10% |
|---|---:|---:|---|---|---|---|---|
| `fs_m3_j2_k2_w2_ur30_fl4_wf10_ar10_s11` | 1,511 s | 712 s | ✅ | VER | ❌ | ❌ | ❌ |
| `fs_m4_j2_k2_w2_ur30_fl2_wf15_ar25_s1` | 965 s | 477 s | ✅ | VER | ❌ | ❌ | ❌ |

Both cases are **legitimate CPG-LD successes** that do not satisfy the
non-trivial task-preservation constraint. They join the fault-path-loss
category. The overall CPG-LD statistics change by ≤0.1 percentage point.

## Remaining 336 cases

All are originally-TIMEOUT evaluations that also exceeded the pilot's hard
subprocess limit (~840 s). These are the hardest instances in the population
and are not expected to complete under any reasonable budget. They are
correctly reported as compute-limited, not as task-preservation failures.

**No further re-execution is recommended.**

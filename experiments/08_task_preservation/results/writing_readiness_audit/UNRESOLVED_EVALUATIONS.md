# Unresolved evaluations and targeted reruns

Of the 5,826 records, 338 have `INFRA_TIMEOUT_OR_ERROR`: 336 were already TIMEOUT in the original experiment, and two were original CPG-LD successes whose original runtimes (1510.9084 s and 964.9958 s) exceeded the pilot shard's hard subprocess limit. These are incomplete computations, not negative adjustment or task-preservation results.

The two original-success cases were rerun separately with a larger budget. Raw stdout JSON, input identity, command templates, frozen records, and independent comparisons are stored in `TARGETED_RERUN_CERTIFICATES/`.

| Case | Frozen hash | Rerun hash | Fresh verification | CI | Path result |
|---|---|---|---|---:|---|
| fs_m3_j2_k2_w2_ur30_fl4_wf10_ar10_s11 | 75f5b4f62a09b248 | 75f5b4f62a09b248 | VER, 0 certificates | 4.9375 | fails; one normal and three fault words lost |
| fs_m4_j2_k2_w2_ur30_fl2_wf15_ar25_s1 | 39962c0cdb2fb439 | 39962c0cdb2fb439 | VER, 0 certificates | 6.3125 | fails; three fault words lost |

The original and rerun adjusted-model hashes, modification counts, and CI values agree. The raw runner's `modified_match`/`CI_match` flags are not used because the first invocation supplied placeholder expected values; the independent comparison in each `validation.json` uses the actual frozen CSV record.

The remaining 336 originally timed-out cases are left censored. Re-executing all of them is unnecessary for the proposed paper claims and would not convert a compute limit into proof of infeasibility or non-repairability.

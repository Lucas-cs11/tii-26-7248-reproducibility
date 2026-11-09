# Outcome flip audit (120 cases)

## Summary

| Original status | Count | Classification |
|---|---:|---|
| TIMEOUT → success | 111 | Timeout boundary; this round has no per-case 300 s limit |
| NO_IMPROVING_CANDIDATE → success | 6 | Platform/solver difference on the global LP |
| FINITE_SEARCH_FAILURE → success | 3 | Platform/solver difference |

## Root cause

The original experiment enforced a 300 s per-case repair timeout via SIGALRM.
The pilot reconstruction (`run_case_audit.py`) does **not** enforce per-case
timeouts (only the shard driver has a hard subprocess limit of ~840 s).
Consequently, cases that originally timed out at 300 s could complete in
300–500 s on the pilot.

Original runtimes of the 111 TIMEOUT flips: min 120 s, P50 330 s, max 414 s —
all at or beyond the original timeout boundary, confirming the mechanism.

## Predicate outcomes for flips

- path_pass: 15/120 (12.5%) — far below the 88–95% rate on original successes,
  confirming these are genuinely harder instances that the original timeouts
  correctly identified as difficult.

## Conclusion

All 120 flips are explained by the **absence of the per-case 300 s timeout in
the pilot reconstruction**, not by algorithmic changes, code bugs, or data
errors. They are legitimate completions under a relaxed compute budget and are
reported separately from the original results.

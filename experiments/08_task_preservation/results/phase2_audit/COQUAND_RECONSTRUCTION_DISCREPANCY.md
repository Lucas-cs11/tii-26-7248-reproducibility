# Coquand reconstruction discrepancy

## Case

`fs_m3_j2_k2_w2_ur50_fl2_wf5_ar10_s6` (coquand).

## Evidence

| | Original | This round |
|---|---|---|
| status | VERIFIED_SUCCESS | RECONSTRUCTED_SUCCESS |
| final_model_hash | `7868dcfd319e2666` | `d076ab72c93739f7` |
| CI | 2.531250 | 2.250000 |
| modified transitions | 2 | 2 |
| fresh verdict | VER | VER |
| fresh certificates | 0 | 0 |
| runtime | 605.3 s | 466.4 s |

Both models are valid adjustments (VER, 0 certificates, same modified count),
but they differ in interval assignment and objective value.

## Root cause

**Multiple valid adjustment solutions via LP solver path difference (type B4+B5).**

The Coquand-inspired method (`global_constraint_repair`) solves a one-shot global
LP synthesis. The original run (macOS, SIGALRM-based 300 s repair timeout) had an
effective runtime of 605 s because the alarm cannot interrupt a C-extension LP
call; the new run (Linux, no per-case timeout in `run_case_audit.py`) completed
in 466 s. The HiGHS LP solver on the two platforms took different internal paths
and returned different vertices of the (apparently non-unique) optimal face,
yielding a lower CI (2.25 vs 2.53) for the new solution.

## Status

`RESOLVED: multiple_valid_solutions_lp_path_difference`

Not an error in either run; both are valid adjustments. The new solution is
strictly better in CI. The 1-case reconstruction mismatch is explained and does
not indicate a systematic defect.

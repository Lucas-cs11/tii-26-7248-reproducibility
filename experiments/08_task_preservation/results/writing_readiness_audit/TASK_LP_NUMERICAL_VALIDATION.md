# LP numerical validation

## Actual numerical mechanism

`code/frozen_src/src/exact_confirmation/lp_solver.py` uses SciPy/HiGHS floating-point LP. Fraction endpoints are converted to float (lines 15–16 and 62–65). Default primal/dual feasibility and optimality tolerances are \(10^{-9}\) (lines 39–40). Minimum and maximum total delay are optimized separately. Returned floats are converted to `Fraction` using `limit_denominator(10**9)` (lines 320–322). This is a rational representation of a numerical result, **not exact-rational solving**.

The solver distinguishes OPTIMAL, INFEASIBLE, UNBOUNDED, NUMERICAL_FAILURE, and UNKNOWN internally. However, `compute_completion_time_interval` returns `None` for any non-OPTIMAL minimum result (lines 300–307), and the pilot predicate maps `None` or an exception to “lost” (`code/predicate.py`, lines 63–74 and 84–92). The saved pilot records therefore do not distinguish mathematical infeasibility from numerical/solver failure.

## Consequences for the aggregate statistics

* A passing path check means the floating-point LP returned OPTIMAL for every selected word.
* A path failure in the raw pilot must be described as **failure of the solver-based feasibility check**, not as a certified exact infeasibility result.
* The recorded `undetermined=0` counts only missing-baseline/exception bookkeeping in the predicate wrapper. It does not establish zero LP numerical unknowns.
* `DECISION_STATUS_AUDIT.csv` marks this limitation for every path-failing record. No global correction is possible without reconstructing the adjusted models and re-running status-preserving LP checks; that larger computation was not authorized.

## Targeted independent checks

For Case 1, direct calls to the underlying LP routine returned `INFEASIBLE` for both lost fault words on both minimum and maximum solves. These are strong solver-reported infeasibility certificates for the representative example, but still floating-point results rather than exact rational proofs. Case 2 returned feasible intervals for its normal and fault reference words and preserved the normal earliest completion time exactly.

Thus the representative scientific point is supported by concrete models and statuses, while the population percentages remain numerical-audit outcomes. No evidence was found that LP numerical failures changed the headline counts; equally, the saved records cannot prove that no such failure occurred.

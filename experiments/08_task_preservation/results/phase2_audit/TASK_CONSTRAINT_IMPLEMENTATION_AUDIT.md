# Task-constraint implementation audit

## Answer: the current experiment implements Capability A (post-hoc check) only

### What the pilot does

1. Run the frozen adjustment method with `AlwaysTrueTaskConstraint` (ψ_task ≡ 1).
2. Obtain the adjusted model N'.
3. Verify N' is diagnosable (VER, 0 certificates).
4. **After** obtaining N', evaluate ψ_path and ψ_perf against the frozen reference set.

The task constraint does NOT participate in candidate generation, LP constraints,
candidate screening, or the optimization objective. It is a **post-hoc audit**
of the unconstrained adjustment result.

### Source evidence

`run_case_audit.py` (the pilot runner) calls `repair(..., task_constraint=AlwaysTrueTaskConstraint())`
for CPG-LD and `exhaustive_repair(..., task_constraint=AlwaysTrue...)` for exhaustive,
then evaluates the predicate on the returned model. The frozen source
(`src/repair/task_constraint.py`) contains an `ExactCriticalSequencePreservation`
class (used in prior R3-2b/c experiments) that applies the constraint during
candidate screening — but the pilot does **not** use it.

### Three capability levels

| Level | Description | Implemented in pilot? | Available in frozen source? |
|---|---|---|---|
| A: Post-hoc check | Check after adjustment | **Yes** | N/A |
| B: Candidate screening | Reject violating candidates during search | **No** | Yes (`ExactCriticalSequencePreservation`) |
| C: Constraint in optimization | Integrate into LP/MILP feasible domain | **No** | No |

### Implications

- The reported 88.1%/94.8%/85.4% are **post-hoc preservation rates** of unconstrained
  adjustments, NOT constrained-search success rates.
- A method's low post-hoc rate (e.g. CPG-LD ψ@0% = 58.8%) does not mean the method
  cannot find satisfying adjustments — it means the *specific* adjustment it returned
  does not satisfy the constraint. A constrained search (Capability B) might find others.
- Phase B (constrained re-search using `ExactCriticalSequencePreservation`) would answer
  whether the methods can still succeed when the constraint is enforced during search.
  This has not been run.

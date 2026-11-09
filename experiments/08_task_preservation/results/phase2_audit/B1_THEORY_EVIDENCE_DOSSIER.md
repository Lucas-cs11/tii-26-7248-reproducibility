# B1 theory evidence dossier

## A. Rigorously proven properties (with definitions and proofs in v26)

1. Strong-time SCG construction is sound and complete for bounded task-completion
   diagnosability (Theorem in paper; SCG construction Definition).
2. The bounded verification problem is decidable under (L, H) bounds (completeness
   of the SCG-pair enumeration).
3. The firing-interval adjustment problem is well-defined on the authorized domain
   (Lemma on the admissible domain).
4. The LP feasibility formulation (Eq. 28) exactly characterizes firing-sequence
   completion-time feasibility under strong-time semantics.

## B. Properties supported by experiment

1. **Non-trivial task constraints are active**: 314/3,181 (9.9%) of successful
   adjustments lose at least one required fault execution; 12 lose a normal execution.
   This is a property of the unconstrained method, not a proof of infeasibility.
2. **Normal-path performance impact is bounded**: all path-preserving repairs have
   ≤10% normal completion-time degradation (CPG-LD: degradation concentrated in 0–10%;
   Coquand/exhaustive: zero degradation on all path-preserving repairs).
3. **Cross-platform reproducibility**: 3,060/3,061 original successes reconstructed
   with identical model hashes on Linux (99.97%).
4. **The 92.47% CPG-LD success rate is reproducible** (in the 1,942-instance pilot
   at the same rate within sampling error).

## C. Unresolved theoretical questions

1. **Is the task-preservation-constrained adjustment problem decidable?** The paper
   proves decidability of the *unconstrained* adjustment. Adding task-preservation
   constraints (path feasibility + performance bounds) may or may not preserve
   decidability under the same bounds — this requires a new proof.
2. **Does a satisfying adjustment always exist when the unconstrained one does?**
   No proof or counterexample. The 314 fault-path-loss cases show it can fail for
   specific returned candidates, but not that no satisfying candidate exists.
3. **What is the computational complexity of the constrained adjustment?** The
   unconstrained version is already expensive; adding path constraints to the LP
   may change the complexity class.

## Why the current task-preservation experiment does not establish theoretical novelty

The experiment demonstrates that **existing** adjustment methods, when audited
post-hoc against a non-trivial behavioral constraint, do not always preserve the
required task behavior. This is an empirical observation about the unconstrained
method's output, not a new algorithm, a new decidability result, or a new proof.

Reviewer 2's B1 concern asks for **mathematical novelty** — a problem, construction,
or theorem not directly derivable from prior work. The current evidence shows:
- The *problem* (bounded task-completion diagnosability with adjustment) is
  well-defined and the paper proves its decidability — this is the paper's core
  theoretical contribution.
- The *task-preservation constraint* is an additional condition that makes the
  problem harder and more realistic, but the paper has not yet proven properties
  of the constrained version.
- The *experiment* characterizes what happens when the constraint is checked
  post-hoc, which is valuable but is not equivalent to solving the constrained
  problem.

To close the B1 gap, the paper would need at minimum: (a) a formal statement of
the constrained adjustment problem, (b) a proof or disproof of its decidability,
and (c) either an algorithm with correctness guarantees or a precise impossibility
result.

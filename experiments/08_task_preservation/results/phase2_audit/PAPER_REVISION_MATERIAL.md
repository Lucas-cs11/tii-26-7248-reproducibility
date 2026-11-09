# Paper revision material for R3-2 (task-preservation constraints)

This document provides formally worded conclusions that can be used in the
manuscript and reviewer response, with explicit conditions and evidence sources.
Internal experiment terminology is excluded.

## 1. Headline result (for the main text)

> When the returned firing-interval assignments are additionally required to
> preserve a pre-registered set of normal and fault execution sequences
> (obtained from the complete certificate enumeration of the original model),
> the proportion of verified adjustments that satisfy this requirement is
> 88.1% for CPG-LD, 94.8% for the Coquand-inspired method, and 85.4% for the
> one-step exhaustive method, on a stratified sample of 1,942 evaluations
> (12.1% of the full 16,038-evaluation population).

**Denominator**: each method's own successful adjustments on the pilot sample.
**Not** a claim about all 16,038 evaluations.

## 2. Zero-degradation result (for the main text)

> Among successful adjustments that preserve the required executions, the
> Coquand-inspired method and the exhaustive method do not increase the
> earliest completion time of any required normal execution (zero degradation
> on all path-preserving repairs). CPG-LD assignments may delay required
> normal executions by up to 10% of their original earliest completion time;
> no path-preserving CPG-LD assignment exceeds this bound.

**Evidence**: the equality of path-preservation and 10%-tolerance pass rates
is a verified data property, not a threshold artifact.

## 3. Method comparison on the attempt denominator

> On the 1,942-attempt denominator, CPG-LD yields the largest absolute number
> of task-preserving verified adjustments at every tolerance level:
> 1,633 path-preserving (84.1%), 1,090 at zero tolerance (56.1%),
> versus 1,017 (52.4%) for Coquand and 217 (11.2%) for exhaustive.

**Key caveat**: these are yields of the *unconstrained* method, audited
post-hoc. They are not success rates of a constraint-enforcing search.

## 4. Paired comparison (for the supplementary material)

> On the 250 evaluations where all three methods produce verified adjustments,
> the task-preservation outcome is identical across methods (86.8% preserve
> all required executions). Per-method differences in preservation rates
> are therefore attributable to the composition of each method's success
> set (i.e., which instances each method can solve), not to differences in
> how the methods adjust timing.

## 5. Structural finding (for the discussion section)

> The dominant failure mode of non-trivial task preservation is the loss of
> required fault execution sequences (314 of 3,181 successful adjustments,
> or 9.9%), not the loss of normal production sequences (12 of 3,181, or 0.4%)
> and not unbounded performance degradation (zero cases exceeding 10%).
> This is consistent with the repair mechanism: adjustments separate fault
> completion from normal completion, and in some cases the separation renders
> the fault execution infeasible within the horizon.

## 6. Limitations (must appear in the paper)

1. The task-preservation condition was evaluated post-hoc on unconstrained
   adjustment results; the adjustment search itself was not modified to
   enforce the condition.
2. For 359 of 3,181 successful adjustments (11.3%), only a deterministic
   sample of at most 3 normal and 3 fault executions was checked; the full
   reference set was checked for the remaining 2,822 (88.7%).
3. The experiment covers a 12.1% stratified sample of the full population;
   extrapolation to the full 16,038 evaluations assumes the stratification
   is representative.
4. Path preservation means the reference execution remains *timed-feasible*
   in the adjusted model; it does not mean all possible task behaviors are
   preserved.

## 7. Suggested revised claim (replacing the unconditional 92.47%)

> The unconstrained adjustment success rate of CPG-LD on the full population
> is 92.47%. On a stratified 12.1% sample, 88.1% of these successful
> adjustments additionally preserve all required normal and fault execution
> sequences, and 58.8% also preserve the earliest completion time of every
> required normal execution exactly. Allowing a 10% tolerance on normal-path
> completion restores the preservation rate to 88.1%.

## 8. For the reviewer response (R3-2)

> We thank the reviewer for identifying this limitation. We have conducted a
> post-hoc audit of the unconstrained adjustment results against a non-trivial
> task-preservation constraint (path feasibility of pre-registered normal and
> fault execution sequences, with 0%/5%/10% bounds on normal-path completion
> time degradation). The audit shows that: (i) 88–95% of successful adjustments
> preserve all required executions; (ii) the dominant loss mode is fault-path
> infeasibility, consistent with the repair mechanism; (iii) normal-path
> performance impact is bounded by 10% in all cases; and (iv) method rankings
> change depending on the strictness of the performance requirement. We have
> revised the manuscript to report these conditional rates and to state the
> post-hoc nature of the check as a limitation.

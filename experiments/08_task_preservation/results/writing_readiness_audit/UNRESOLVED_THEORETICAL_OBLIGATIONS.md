# Unresolved theoretical obligations

1. **Novelty against prior literature.** A formal comparison with state-class, diagnosabilization, parameter-synthesis, and timed-diagnosis literature remains necessary. This experiment cannot establish novelty by itself.
2. **Existence and search completeness under a non-trivial task predicate.** v26 proves termination and soundness for an effective predicate used in the finite search, not that a satisfying assignment exists or that the staged search will find one. Any stronger claim needs a new proof or counterexample.
3. **Predicate-specific guarantees.** The particular sampled/full reference and performance predicate used here was not supplied to Algorithm 2. Its integration, effective evaluation, and any desired completeness statement remain unverified.
4. **Exact numerical certification.** The aggregate path checks are floating-point LP outcomes. Exact-rational infeasibility certificates or independently checkable witnesses would be needed to upgrade numerical observations into exact mathematical claims at scale.
5. **All-behavior preservation.** No theorem or experiment here shows preservation of every bounded complete execution or every original feasible completion time.
6. **Performance acceleration.** Duration enclosure is a sound rejection device, but its practical pruning effect is workload-dependent; no universal acceleration theorem or empirical generalization is supported.
7. **Alternative-candidate phenomenon.** No existing returned-candidate pair was found where one VER adjustment fails and another satisfies the path predicate. An exhaustive-domain analysis would be needed to establish or refute a particular instance.

These are obligations for theoretical review, not defects that can be repaired by increasing the experimental success rate.

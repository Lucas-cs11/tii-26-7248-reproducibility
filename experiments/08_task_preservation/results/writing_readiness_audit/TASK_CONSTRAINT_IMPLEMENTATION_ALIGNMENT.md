# Task-constraint implementation alignment

## Formal claim in v26

Algorithm 2 takes \(\psi_{\mathrm{task}}\) as an input and includes it in the admissible improving set (v26 main, lines 788–797 and 804–819). The adjustment theorem states termination and soundness: **every returned model** satisfies the supplied task predicate and is bounded task-completion diagnosable, under finite domains and conclusive/inconclusive bounded analyses (lines 826–845). It does not promise existence, global optimality, or exhaustive coverage of the Cartesian product.

## What the present experiment executed

`code/run_case_audit.py`, lines 64–75, invokes CPG-LD and exhaustive search with `AlwaysTrueTaskConstraint`, and invokes the Coquand-inspired one-shot function without a task gate. After a candidate is freshly verified, lines 83–103 evaluate the path and performance predicate. The reported task checks are therefore **post-hoc evaluations**, not constraints exercised by this run.

## Capability levels supported by the source

| Level | CPG-LD | Exhaustive | Coquand-inspired implementation |
|---|---|---|---|
| A. Independent post-hoc evaluation | **Exercised** | **Exercised** | **Exercised** |
| B. Candidate screening during search | Interface and gates exist (`algorithm.py`, candidate gates at lines 375–401, LP stages 477–489, pair search 541–591, final check 702–726) | Interface and gate exist (`exhaustive.py`, lines 240–256 and final check 324–327) | Current top-level function has no task-constraint argument (`global_constraint_repair.py`, lines 93–109); do not claim screening was used |
| C. Constraint integrated into the mathematical optimization model | **Not established** | **Not established** | **Not established** |
| D. Proven conditional solution guarantee for this non-trivial predicate | **Not established by this experiment** | **Not established** | **Not established** |

The available `ExactCriticalSequencePreservation` class can gate candidates on full certificate-word feasibility, but it is not the same predicate as the pilot's sampled/full-plus-performance tiers, and it was not used here. Its LP remains an external oracle, not an integrated optimization constraint. The Coquand routine could be modified to reject its final synthesized model, but that would be a new implementation and experiment; the present source does not establish it.

## Strongest justified statement

The current experiment establishes **Level A only**: a verified adjustment can be independently evaluated for preservation of designated reference paths and earliest-completion tolerances. The source architecture makes Level B plausible for CPG-LD and exhaustive search, but no non-trivial constrained-search result or corresponding correctness/completeness guarantee is claimed from these 5,826 records.

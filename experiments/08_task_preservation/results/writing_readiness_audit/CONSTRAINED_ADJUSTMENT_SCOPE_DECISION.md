# Scope decision for constrained adjustment

## Recommended paper path: retain the existing algorithm and state the audit boundary

The present evidence is sufficient to add a post-hoc behavioral audit and to clarify that the reported large-sample adjustment runs used the constant task predicate. It is not sufficient to claim that the non-trivial path/performance predicate was enforced by the search.

## What a genuine constrained-search extension would require

1. A formal predicate definition matching the paper, including whether reference paths, all bounded executions, or performance envelopes are required.
2. For CPG-LD/exhaustive, construction and freezing of the corresponding constraint object before candidate generation, plus candidate-level rejection logs.
3. For the Coquand-inspired baseline, an explicit screening or reformulated synthesis step; the current top-level implementation does not provide it.
4. A soundness argument for accepted candidates and a carefully bounded statement about search completeness. A finite candidate screen does not by itself prove that a satisfying adjustment exists or will be found.
5. Fresh complete-set verification and separate treatment of timeouts, numerical unknowns, and finite-search failures.
6. A new, independently authorized experiment; its outcomes must not be merged into the frozen formal adjustment statistics.

No such implementation or large experiment is initiated in this audit.

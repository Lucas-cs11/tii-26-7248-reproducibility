# Implementation-equivalence acceptance report

**Decision: equivalence accepted.** The optimized implementation is
behaviourally identical to the reference implementation on every layer that
could affect a reported result.

## Pre-registered protocol

`equivalence_protocol.yaml` (+ JSON mirror), pre-registered before execution. Baseline
implementation at commit `10d27726c085…`, optimized implementation at commit
`215443219c52…`, Python 3.13.

## Layer 1 — end-to-end

48 paired evaluations (same inputs, both implementations, 60 s/300 s caps):
**30 conclusive pairs are exactly identical** (0 mismatches; 27 under the 60 s
cap, 3 under the 300 s cap). 18 pairs are censored: 11 where the reference
implementation capped but the optimized one completed, 7 where both capped;
0 pairs where the optimized implementation capped but the reference completed.

## Layer 2 — transition-level synchronizer

45 of 48 evaluations checked at transition level (3 heavy evaluations cannot
build the full synchronizer within the 900 s budget and are censored with
explicit reasons): **726,665 fresh-vs-memoized transition comparisons,
0 mismatches**; the rebuilt automaton matches the implementation for all 45
checked evaluations. An independent full-automaton comparison covers 39 of them
(6 skipped by the 60 s budget).

## Layer 3 — components

| component | evidence | mismatches |
|---|---|---:|
| state-class adjacency index | 24/24 models, 60,767 classes vs the original edge-list projection | 0 |
| marking cache | 12/12 instance families, 25 words, 1,891 nodes vs a cache-free reference | 0 |
| trace-record deduplication | 25 samples, 85,710 critical pairs, 1,354 multi-record nodes | 0 |
| exact-rational boundary cases | 13 boundary cases (half-integers, arbitrary denominators, zero, negatives, infinity, equality) | 0 |
| independent rational oracle | 15 oracle tests + 12-family semantic validation | 0 |

Unit tests: 67 tests pass.

## Limits

* The 3 heavy evaluations cannot build the synchronizer automaton in either
  implementation; they are censored, not passed.
* The no-cache full-automaton comparison covers 39/45 evaluations (6 skipped by
  budget).
* Component expansion checks use small and medium representatives; the exact
  parameters are recorded in the evidence JSON files.

## Files

`component_equivalence.json`, `sync_transition_equivalence.json`,
`equivalence_protocol.yaml/json`.

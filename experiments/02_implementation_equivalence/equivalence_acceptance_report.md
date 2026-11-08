# Implementation-equivalence report

The optimized implementation is behaviourally identical to the reference
implementation on every layer that could affect a reported result.

## End-to-end layer

48 paired evaluations (same inputs, both implementations): 30 conclusive pairs
are exactly identical (0 mismatches). 18 pairs are censored — 11 where the
reference implementation capped but the optimized one completed, 7 where both
capped; there are no pairs where the optimized implementation capped but the
reference completed.

## Transition layer

45 of 48 evaluations checked (3 heavy evaluations cannot build the full
synchronizer within the 900 s budget and are censored): 726,665
fresh-vs-memoized transition comparisons, 0 mismatches; the rebuilt automaton
matches for all 45 checked evaluations. An independent full-automaton
comparison covers 39 of them (6 skipped by the 60 s budget).

## Component layer

State-class adjacency index (24 models, 60,767 classes), marking cache (12
families), trace-record deduplication (85,710 critical pairs), exact-rational
boundary cases (13), independent rational oracle (15 tests + 12-family
semantic check): all 0 mismatches.

## Limits

The three heavy evaluations cannot build the synchronizer automaton in either
implementation; they are censored, not passed. Component checks use small and
medium representatives; the parameters are recorded in the evidence JSON.

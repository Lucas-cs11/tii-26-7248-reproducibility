# Experiment 02 — implementation equivalence

The scalability study uses an optimized verifier implementation. This
experiment demonstrates that the optimization changes no observable behaviour:
verdicts, synchronizer transitions, state-class fingerprints and every component
cache are compared against the reference implementation.

## Result: equivalence accepted

| layer | what is compared | outcome |
|---|---|---|
| end-to-end | 48 paired evaluations (same inputs, both implementations) | 30 conclusive and identical; 18 accounted as censored; 0 mismatches |
| transition level | every synchronizer state × observable label, memoized vs freshly recomputed | 726,665 comparisons, 0 mismatches; the rebuilt automaton matches for all 45 runnable evaluations (3 heavy evaluations censored, not passed) |
| components | state-class adjacency index (60,767 classes), marking cache (12 instance families), trace-record deduplication (85,710 critical pairs), exact-rational boundary cases (13), independent rational oracle (15 tests + 12-family semantics) | all pass, 0 mismatches |

## Files

`equivalence_protocol.{yaml,json}`, `equivalence_acceptance_report.md`,
`component_equivalence.json`, `sync_transition_equivalence.json`.

## Reproduce

```bash
python ../01_scalability/code/scripts/evaluate_equivalence.py   # EQUIVALENCE_ACCEPTED = GO
```

# Experiment 02 — semantic equivalence of the optimized verifier (differential v2)

The paper's scalability numbers come from an optimized verifier. This
experiment proves that the optimization is **behaviour-preserving**: end-to-end
verdicts, synchronizer transitions, SCG fingerprints and every component cache
are compared against the reference implementation.

## Result: `DIFFERENTIAL_V2_ACCEPTED = GO`

| Layer | Evidence | Outcome |
|---|---|---|
| A — end-to-end differential (48 frozen cells) | 30 conclusive identical, 18 censored with explicit accounting | 0 mismatches |
| B — transition-level synchronizer equivalence | `sync_transition_equivalence.json` | 45 checked + 3 censored cells, 726,665 fresh-vs-memo comparisons, 0 mismatches, automaton reconstruction identical for all 45 |
| C — component audits | `component_equivalence.json` | SCG adjacency index 60,767 classes; marking cache 12 families; trace-record dedupe 85,710 critical pairs; DBM/Fraction 13 boundary cases; independent Fraction oracle 15+1 tests |

Full protocol: `v6-performance-differential-2.{yaml,json}` (frozen before the
run). Detailed narrative: `v6_differential_v2_acceptance_report.md`,
`v6_differential_v2_component_evidence.md`,
`v6_optimization_differential_report.md`.

## Reproduce

```bash
python ../01_scalability_v6/code/scripts/evaluate_v6_differential_v2.py
# expects: DIFFERENTIAL_V2_ACCEPTED = GO
```

The component verifiers live in
`../01_scalability_v6/code/scripts/verify_v6_*_equivalence.py`.

## Caveat

The 3 censored Layer-B cells (`F06/F09/F12`, `L_high_complete`) cannot build the
synchronizer automaton in either version within 900 s; they are also censored in
the v1 differential at 300 s. They are **not** claimed as equivalent.

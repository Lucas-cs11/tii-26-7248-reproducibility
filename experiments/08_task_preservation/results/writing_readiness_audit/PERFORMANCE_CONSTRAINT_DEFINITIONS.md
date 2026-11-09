# Performance-constraint definitions and numerical boundaries

The performance metric is the **earliest feasible completion time** of each selected normal certificate word, computed as the minimum of total delay over its bounded path polytope. The reference is the same word on the nominal model. Each instance and each word is evaluated separately; there is no averaging over paths. Fault words are checked for feasibility only.

For baseline \(t_0>0\), the allowed maxima are \(t_0\), \(1.05t_0\), and \(1.10t_0\). For \(t_0=0\), every tier requires exactly zero increase. Comparisons are made on `Fraction` objects produced by rounding floating-point LP results with `limit_denominator(10**9)`; this display conversion does not make the LP exact-rational.

The tiers are monotone by construction: passing 0% implies passing 5%, which implies passing 10%, provided the path condition holds. If a normal word is lost, no performance credit is assigned. If a fault word is lost, all combined tiers fail even when every normal timing comparison passes.

## Why the 10% count equals the path-preservation count

This is a measured property of the dataset, not a hard-coded rule. `scripts/analyze_performance.py` scanned every retained normal row in every path-passing case:

* 4,274 normal-word comparisons;
* 875 had a positive earliest-completion increase;
* 366 exceeded 5%;
* **0 exceeded 10%**;
* the largest positive relative increase was \(1/14\approx7.14\%\).

Therefore every case passing the path condition also passes the 10% condition in this sample. This does not imply that 10% is vacuous in general: among retained normal rows in path-failing cases, eight comparisons exceeded 10%, with a maximum of \(1/7\). Those cases still fail the combined predicate because another reference word was lost.

# Task-preservation semantics

## What is actually checked

For each adjusted model N', the predicate checks:

1. **ψ_path**: every selected reference execution σ ∈ S_req is *timed-feasible* in N'
   under horizon H, i.e. the firing-sequence polytope P_H(σ) has a non-empty interior.
   Checked by the frozen LP oracle `compute_completion_time_interval(N', σ, H) ≠ None`.
2. **ψ_perf**: for every *normal* σ ∈ S_req, the earliest completion time
   t_min(N', σ) ≤ t_min(N₀, σ) + Δ, with Δ ∈ {0, 5%·t_min(N₀), 10%·t_min(N₀)}.

## What this does NOT mean

This is **not** a guarantee that all task behaviors of N₀ are preserved. It checks
that a *specific, frozen set of reference executions* remains feasible with bounded
performance degradation. The distinction is:

| Level | Meaning | Status |
|---|---|---|
| Full reference set preservation | All certificate-enumerated normal and fault executions feasible | Checked for 2,822/3,181 successes (certificate count ≤ 32) |
| Sampled reference path preservation | K=3 normal + K=3 fault paths (deterministic hash selection) feasible | Checked for 359/3,181 successes (certificate count > 32) |
| Full task semantic preservation | All mathematically possible task executions preserved | **Not checked and not claimed** |

## Why ψ@10% == path_pass

For every method, the number of repairs passing ψ@10% equals the number passing
path preservation. This means: **among repairs that preserve the reference paths,
ALL satisfy the 10% tolerance on normal-path completion time.** The CPG-LD gap
between path (88.1%) and ψ@0% (58.8%) is entirely within the 0–10% degradation
range. For Coquand and exhaustive, every path-preserving repair also has zero
degradation (their interval assignments do not delay normal completion).

This equality is a property of the data on this sample, not a code artifact.

## Reference set selection rule (frozen)

From N₀'s complete certificate enumeration, extract distinct normal words
(certificate σ_N) and fault words (σ_F). If the certificate set ≤ 32, use the
full set ("full" regime); otherwise select K=3 per class by SHA-256 keyed to
the evaluation ID ("sampled" regime). The selection is independent of the
adjustment result and identical across the three methods.

## Path coverage

| Method | Full regime | Sampled regime | Total |
|---|---:|---:|---:|
| CPG-LD | 1,595 | 259 | 1,854 |
| Coquand | 1,011 | 62 | 1,073 |
| Exhaustive | 216 | 38 | 254 |
| All | 2,822 | 359 | 3,181 |

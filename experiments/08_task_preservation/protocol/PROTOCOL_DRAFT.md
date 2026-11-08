# R3-2 protocol draft (freeze candidate)

Status: draft, to be frozen before any adjustment-result-dependent check.

## Research questions

* **RQ1/RQ2 (post-hoc):** of the original successful adjustments, how many preserve the required
  normal and fault executions, and does the normal-path earliest completion time degrade?
* **RQ3 (constrained re-search):** under a non-trivial task predicate applied inside candidate
  acceptance, can CPG-LD / Coquand / exhaustive still return freshly verified diagnoses?
* **RQ4 (physical plausibility):** what can the authorized interval domains actually support?

## Task predicate ψ_task = ψ_path ∧ ψ_perf

### Reference execution set S_req (frozen before results)

For each evaluation, run the frozen complete-set verifier on N0 (must be AMB, complete, non-empty
certificates). From the certificate set extract distinct normal words (certificate `N`) and fault
words (certificate `F`). Selection rule (deterministic, independent of any adjustment):

* canonical order by `SHA-256(evaluation_id | "N" | ",".join(word))` (resp. `"F"`);
* take the first **K = 3** distinct normal words and **K = 3** distinct fault words;
* if the certificate set is small (≤ 32 distinct words), use the **full** set instead and record
  which regime applied;
* freeze `{S_req, K, hash-selection seeds, baseline earliest completion times}` in
  `protocol/reference_sets/` before evaluating any adjusted model.

`ψ_path(N')`: every σ ∈ S_req is timed-feasible in N' under H — checked by the frozen path LP
`compute_completion_time_interval(N', σ, H) ≠ None` (exact rational timing, strong-time semantics,
first-completion sequences; structure is unchanged by repair, so feasibility is the correct test).

`ψ_perf(N')`: for every normal σ ∈ S_req, `t_min(N', σ) ≤ t_min(N0, σ) + Δ` with tiers
`Δ ∈ {0, 5%·t_min(N0), 10%·t_min(N0)}`; if `t_min(N0) = 0` the tolerance is 0 for every tier
(no division by zero, tiers coincide and are reported as such). The threshold is frozen with the
baseline set.

Failure states are not merged: `LOST_NORMAL`, `LOST_FAULT`, `PERF_FAIL_T0/T5/T10`,
`ORACLE_UNDETERMINED` (LP exception), `RECONSTRUCTION_MISMATCH`.

## Phase A — post-hoc preservation audit (no new search)

For every recorded `VERIFIED_SUCCESS` of the three methods (14,830 / 9,097 / 2,005):

1. regenerate N0 from the frozen population row; verify it is AMB with complete certificates;
2. rebuild S_req by the frozen rule and compute baseline `t_min`;
3. rerun the frozen method with `AlwaysTrueTaskConstraint` on the same inputs;
4. require the reconstructed `final_model_hash` to equal the recorded value (else
   `RECONSTRUCTION_MISMATCH`, kept separate);
5. evaluate ψ_path and ψ_perf on the reconstructed N';
6. record per-model status, per-sequence feasibility/deltas and failure causes.

Reported quantities are preservation rates over the original success set with explicit
denominators; they are **not** constrained-search success rates. A failed post-hoc check means the
returned adjustment violates the new constraint, not that no adjustment exists.

Implementation notes: reconstruction uses the frozen `tools/run_case.py` logic; final
re-verification is skipped for the audit reconstruction (the recorded status already certifies it)
but is run for an independent 1% audit sample; the predicate consumes the reconstructed N'.

## Phase B — constrained re-search (only after Phase A integrity and predicate tests pass)

Frozen stratified cohort from the full 16,038 population (not from the success subsets), with
strata on structure size, WIP bound, adjustable ratio, unobservable ratio and original-method
outcomes. Methods keep their frozen definitions and search scopes; the task gate is applied inside
the acceptance path of each method (candidate screening), and every returned model must pass a
fresh complete-set verification plus ψ_task. Reported: constrained successes, per-method rates on
the shared denominator, paired comparisons on models solved by all methods, rejection reasons,
censor counts and compute limits.

## Phase C — expansion decision

After independent audit of Phase A/B: GO-LIMITED, GO-FULL (budget and frozen protocol required) or
NO-GO, with the seven decision questions answered explicitly.

## RQ4 — physical plausibility audit

Audit (evidence only, no invented parameters): authorized domain `±50%` of nominal interval and
the five discrete authorized intervals of the extended domain are **synthetic benchmark
authorizations**; the S5 industrial case has its own frozen domain and adjustment record; no
manufacturer interval tables, controller resolution or safety limits are distributed with the
data. Report which claims (repairability, adjustment magnitude, performance impact) are supported
at the model level and which require equipment/process data that do not exist here.

## Tests required before freezing

1. N0 itself passes ψ_path (reference set is feasible on the reference model).
2. A candidate that makes a selected normal sequence infeasible is rejected (`LOST_NORMAL`).
3. A candidate that makes a selected fault sequence infeasible is rejected (`LOST_FAULT`).
4. A candidate whose normal `t_min` exceeds the tier tolerance is rejected only in that tier.
5. A candidate preserving both and satisfying the timing bound passes ψ_task.
6. Oracle failure is reported as `ORACLE_UNDETERMINED`, never as a pass/fail.
7. S5 regression: the reference builder reproduces 87 normal / 88 fault sequences.
8. Determinism probe: reconstruction matches recorded hash on the sample (done, 12/12).

## Budget (Phase A)

Recorded per-success compute (sum of `runtime_seconds`): CPG-LD 63.3 h, Coquand 25.4 h,
exhaustive 4.9 h → **93.7 CPU-hours** for full reconstruction. Predicate overhead: ≈6 sequences ×
(2–4 LPs) per case → ≈1–2 CPU-hours for 26k cases. Options:

* local MacBook Air, 7 workers: ≈10–14 h wall (no cloud cost);
* Modal CPU workers, 40 parallel: ≈2.5–3 h wall, ≈**$6–9** compute at list rates.

No full constrained matrix (16,038 × 3) is proposed; Phase C decides after the audit.

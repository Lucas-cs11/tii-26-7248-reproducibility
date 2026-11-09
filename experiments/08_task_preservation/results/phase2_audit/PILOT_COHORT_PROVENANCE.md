# Pilot cohort provenance

## Selection rule (frozen before execution)

The 1,942 pilot cells were selected from the frozen 16,038-evaluation AMB population by
deterministic stratified sampling: the population is partitioned into strata by
(structure parameters × original three-method status triplet); within each stratum,
evaluation IDs are ordered by SHA-256("pilot|" + evaluation_id) and the first
ceil(0.10 × stratum_size) are taken. The manifest was frozen in
`protocol/pilot_manifest.json` (SHA-256 `822b3e34…`) before any pilot execution.

## Verification results

- 1,942 cells, 1,942 unique evaluation IDs, 0 duplicates.
- All 1,942 IDs are members of the frozen 16,038 population.
- 0 extra IDs outside the manifest appear in the records.
- 5,826 records = 1,942 × 3 methods, 0 duplicate (evaluation, method) pairs.
- All three methods ran on exactly the same 1,942 instances.

## Stratification coverage

771 strata, each sampled at ≥10% (minimum 1/10 = 10.0%). Per-factor coverage
is uniform at ~12% across n_machines, n_parts, ops_per_part, wip_bound,
unobservable_ratio, fault_locations, interval_width_factor and adjustable_ratio.
No stratum is empty and no stratum is over-represented.

## Scope statement

**The 100% coverage figure means all 1,942 pre-registered pilot evaluations have
execution records. It does NOT mean the full 16,038-evaluation population was
analysed under non-trivial task preservation, nor that every record received a
definitive verdict (338 were compute-limited).**

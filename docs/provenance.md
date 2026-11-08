# Provenance and integrity

## What is checked in

* Pre-registered protocols (task manifest, partition plan, evaluation grid,
  semantics gate) and the pre-registered protocol description.
* Execution code (per-evaluation runner, verifier implementation, cloud
  application, analysis/audit/plot scripts) and unit tests.
* Result summaries: statistics, audit, Figure 6, acceptance report and the
  equivalence/historical reports.
* `MANIFEST.sha256` at the repository root covers every checked-in file.

## What is published as a release asset

The bulk raw data are not stored in git:

| Artifact | Size | Location |
|---|---:|---|
| 8,280 raw evaluation records, per-partition ledgers, metrics, hash manifests | 25.1 MB | release asset `scalability-evaluations` in the archived repository `tii-26-7248-scalability-v2` |
| 36,450-row timing table | — | archived repository `tii-26-7248-verifier-timing` |
| ambiguity-horizon cohorts (1,140 models) and lab results | — | archived repository `tii-26-7248-h-sensitivity` |
| exhaustive-baseline partitions (40) | — | archived repository `tii-26-7248-exhaustive-full` |
| context-dataset tables | — | archived repository `tii-context-case-study` |

## Identifiers recorded per evaluation

* evaluation identifier and the pre-registered task parameters (L, H, mode,
  seed, replicate, instance identifier);
* source commit, container-image specification SHA-256, worker invocation
  identifier;
* execution status, verdict, verdict reason, stage counters, wall time and peak
  memory;
* a record hash and the corresponding completion-ledger entry.

## Audit chain

1. The runner writes one record per evaluation and one ledger entry with a
   byte-level hash.
2. The independent audit re-reads the raw records, the pre-registered task grid, the
   ledgers, the metrics and the hash manifests; it recomputes every hash and
   checks every frozen field.
3. The analysis pipeline recomputes the statistics and cross-checks them against
   the audit; it refuses to emit statistics if the integrity check fails.
4. Figure 6 is rendered from the statistics only.

Reference audit: GitHub Actions run `42434059038` — PASS, 8,280 evaluations,
8,280 unique identifiers, 120 worker partitions, 0 technical failures, no
findings.

# Acceptance report — scalability study (8,280 evaluations)

**Verdict: ready for the manuscript.** All pre-registered evaluations were
executed; the independent audit passed; every result file is covered by
`MANIFEST.sha256`.

## Execution provenance

- run identifier `run-5038d2a9-20261107T113535Z`, source commit
  `5038d2a957eafba43bb978cdb9edea00a5c77341`, container-image specification
  SHA-256 `f64f51657a4ec43dd7946ebb931fefca7e78524017d7dd34e978c28da183fee7`.
- 120 independent worker partitions × 69 evaluations; 20 partitions concurrent;
  60 s wall-clock cap per evaluation; 50,000 state-class cap.
- Raw records: 8,280 / 8,280; worker partitions completed: 120 / 120.

## Results

| metric | value |
|---|---:|
| completed | 5,406 |
| wall-clock-capped (right-censored) | 2,874 |
| errors | 0 |
| VER | 1,975 |
| AMB | 2,782 |
| INC | 649 |

## Independent audit

- PASS: 8,280 evaluations, 8,280 unique identifiers, 120 worker partitions,
  0 technical failures, no findings (GitHub Actions run `42434059038`).
- Every pre-registered field and every recorded hash was recomputed from the raw
  records; the audit does not reuse the runner's bookkeeping.

## Cost

- Measured workspace cost for the preliminary validation plus the study:
  **$5.53**, within the authorised $10 cap (the guard stops new partitions at
  $9.50). The preliminary validation run consumed $0.10.

## Incident log (all resolved without data loss)

| event | effect | resolution |
|---|---|---|
| local network proxy returned HTTP 503 mid-run | orchestrator exited; completed evaluations preserved | resumed with the same run identifier; no evaluation re-executed |
| budget guard projected the full cost from too few evaluations and stopped new partitions | temporary stop at 3/120 partitions | projection corrected to use measured compute time and a minimum sample; run resumed |
| one worker partition hit a transient connection error | one partition retried once | completed on retry; recorded in the run manifest |

## Files

`statistics.json`, `denominators.csv`, `audit.json`, `group_statistics.csv`,
Figure 6 (`figure6.svg/pdf/eps/png`), `figure6_caption.md`, `figure6_data.csv`,
`figure6_metadata.json`.

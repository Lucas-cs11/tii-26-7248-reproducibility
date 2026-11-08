# Execution environment

| Experiment | Platform |
|---|---|
| Scalability study (8,280 evaluations) | Modal CPU workers, 20 concurrent, 1 physical core and 4 GiB per worker, 60 s per evaluation |
| Independent audit, statistics, Fig. 6 | GitHub Actions (Ubuntu 22.04) |
| Historical-baseline audit | GitHub Actions |
| Verifier timing (Fig. 3) | GitHub Actions |
| Ambiguity horizon | lab server + GitHub Actions |
| One-step exhaustive baseline | GitHub Actions |

The scalability worker image is pinned to Python 3.13, NumPy 2.3.4,
SciPy 1.16.2 and Modal 1.6.3 (Debian slim); the image specification SHA-256 is
recorded in the pre-registered protocol and in every evaluation record.
Each completed evaluation is written atomically and recorded in a partition
ledger with a byte-level SHA-256, so an interrupted worker resumes without
re-running completed evaluations. The 50,000-state-class cap applies to the
analysis; mathematical timeouts and inconclusive outcomes are never retried.

Timings are only compared within one platform.

# Execution environment

## Platforms

| Experiment | Platform | Notes |
|---|---|---|
| Scalability study (8,280 evaluations) | Modal CPU workers | executed only on this platform; the timings in Fig. 6 come from here |
| Independent audit, statistics, Fig. 6 | GitHub Actions (Ubuntu 22.04) | free compute; audit is independent of the runner |
| Historical-baseline audit | GitHub Actions, 20 worker partitions | 60 s cap per evaluation |
| Verifier timing (Fig. 3) | GitHub Actions | 255 worker partitions |
| Ambiguity horizon | lab server + GitHub Actions | lab part completed before archiving |
| One-step exhaustive baseline | GitHub Actions | timeout budget scaled to the reference machine |

Timings are never compared across platforms.

## Scalability execution

* **Worker:** 1 physical CPU core, 4 GiB memory, no GPU.
* **Image:** Debian slim, Python 3.13, NumPy 2.3.4, SciPy 1.16.2, Modal 1.6.3.
  The resolved image specification SHA-256 is recorded in the pre-registered protocol
  and in every evaluation record.
* **Concurrency:** 20 worker partitions in parallel; each partition runs its 69
  evaluations sequentially.
* **Caps:** 60 s wall clock per evaluation (hard kill of the evaluation
  subprocess group); 50,000 state classes for the analysis; no retry of a
  mathematical timeout or inconclusive outcome.
* **Checkpointing:** each completed evaluation is written atomically and
  recorded in a per-partition completion ledger with a byte-level SHA-256; an
  interrupted worker resumes from the ledger without re-running completed
  evaluations.
* **Cost guard:** the run stops spawning new partitions once the projected
  full-study cost reaches $9.50 of the authorised $10 cap; the reference run
  measured $5.53 including the preliminary validation run.

## Reproducibility notes

* The worker image and the Python dependency list are pinned
  (`code/requirements.lock` with hashes, `code/requirements-modal.lock`).
* Every evaluation record carries the source commit, the image specification
  SHA-256, the worker invocation identifier and the evaluation identifier.
* The independent audit recomputes every file hash and every pre-registered field from
  the raw records; it does not reuse the runner's bookkeeping.

## Environment of the archived experiments

The historical baseline, timing and case-study experiments were executed before
this package was assembled; their archived companion repositories record the
original machine and dependency details.

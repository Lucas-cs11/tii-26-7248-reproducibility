# v6 analysis summary (FORMAL)

- Protocol: `v6-formal-1`  Tasks: 8280  Records: 8280
- Cap: 60 s per cell  Integrity: PASS
- Datasets: run-5038d2a9-20261107T113535Z

## Denominators (all cells)

| experiment | total | completed | timeout | INC | VER | AMB | ERROR |
|---|---:|---:|---:|---:|---:|---:|---:|
| all | 8280 | 5406 | 2874 | 649 | 1975 | 2782 | 0 |
| A_structural | 600 | 600 | 0 | 50 | 343 | 207 | 0 |
| B_wip | 1080 | 628 | 452 | 30 | 164 | 434 | 0 |
| C_Lsweep | 5400 | 3249 | 2151 | 0 | 1195 | 2054 | 0 |
| D_difficult | 1200 | 929 | 271 | 569 | 273 | 87 | 0 |

## Censoring and INC handling

- 2874/8280 cells are right-censored at 60 s; all time quantiles use the 5406 COMPLETED cells only.
- INC is reported as its own denominator and is never a zero-work cell.

## Key findings

- A structural: conclusive rate over COMPLETED cells 0.917; timeout share 0.0.
- B WIP_1: 0/360 timeout, INC=0, wall P50 0.908 s (completed only).
- B WIP_2: 189/360 timeout, INC=0, wall P50 8.673 s (completed only).
- B WIP_3: 263/360 timeout, INC=30, wall P50 39.611 s (completed only).
- B paired growth (uncensored pairs): WIP2/WIP1 median 84.396, WIP3/WIP1 median 113.772; censored pairs only give lower bounds.
- C L-sweep: 4011/5400 cells entered the depth-L synchronizer stage; 2816 cells produced candidate words; 192/300 L-swept models show candidate-word onset at some L; 25 show a verdict change that is confounded by mixed modes.
- D difficult: INC 569/1200 (state-space cap), timeout 271, conclusive 360.

## Files

- `normalized_tasks.csv` — one row per task (denominators, censoring,
  stage counters/timings, cache status, L-sensitivity flags).
- `denominators.csv` — n_total/n_completed/n_timeout/n_inc/n_error per
  group with the censoring note.
- `A_structural.csv` / `B_wip*.csv` / `C_lsweep*.csv` /
  `D_difficult.csv` — the four experiment tables.
- `failure_stages.csv` — timeout/INC stopping-stage distribution.
- `statistics.json` — everything above plus metadata and caveats.

All numbers are recomputable from the raw JSONL under `/home/runner/work/tii-26-7248-scalability-v2/tii-26-7248-scalability-v2/work/v6_formal_run_run-5038d2a9-20261107T113535Z` and
the frozen tasks under `/home/runner/work/tii-26-7248-scalability-v2/tii-26-7248-scalability-v2/protocol/v6_formal_tasks`.

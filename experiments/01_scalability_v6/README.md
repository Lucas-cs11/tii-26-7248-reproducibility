# Experiment 01 — scalability of bounded task-completion diagnosability (Fig. 6)

Frozen 8,280-cell matrix over 12 TPN families and four experiment groups
(A structural 600, B WIP 1,080, C L-sweep 5,400, D difficult 1,200), 120
model-clustered shards × 69 cells, 60 s per-cell wall cap, 50,000-state-class
cap. Executed **only on Modal** CPU Functions (1 physical core, 4 GiB).

## Headline result (reference run `run-5038d2a9-20261107T113535Z`)

| metric | value |
|---|---:|
| cells | 8,280 |
| COMPLETED | 5,406 |
| TIMEOUT_WALL_CLOCK (right-censored) | 2,874 |
| ERROR | 0 |
| VER / AMB / INC | 1,975 / 2,782 / 649 |
| independent audit | PASS (8,280 tasks, 8,280 unique ids, 120 shards) |
| Modal cost (incl. pilot) | $5.53 of a $10 cap |

## Contents

```
protocol/   frozen protocol (YAML+JSON), task manifest, shard manifest,
            task grid (v6_formal_tasks.tar.gz), semantics gate, historical manifest
code/       runner/ (per-cell subprocess), src/ (verifier), modal_app/ (Modal app),
            tests/ (67 unit tests), scripts/ (build, run, audit, analyze, plot, package)
results/    statistics.json, denominators.csv, Figure 6 (svg/pdf/eps/png),
            caption, plotting data, audit.json, group_statistics.csv,
            FINAL_ACCEPTANCE_REPORT.md, differential-v2 and historical reports
```

## Reproduce

See `REPRODUCE.md` §1–§3 at the repository root. The short version:

```bash
python code/scripts/validate_v6_formal_protocol.py --manifest protocol/v6_formal_manifest.json \
  --tasks protocol/v6_formal_tasks --semantics-gate protocol/v6_semantics_gate.json --out /tmp/v.json
python code/scripts/run_v6_modal.py plan --dry-run --formal     # paid run in REPRODUCE.md §2
python code/scripts/plot_figure6_v6.py --analysis-dir results --out /tmp/fig6
```

## Data

The 8,280 raw JSON records, 120 per-shard ledgers, metrics and hash manifests
are published as the release asset `v6-formal-run-5038d2a9` in the archived
repository (25.1 MB). `results/statistics.json` and `results/audit.json` are
derived from them by `analyze_v6_formal_results.py` and
`audit_v6_modal_results.py`.

## Notes

* Timeouts are censored, never imputed; INC has its own denominator.
* 3 of the 48 differential-v2 cells cannot build the full synchronizer
  automaton inside the budget and are censored with explicit reasons (see
  `../02_cross_version_equivalence/`).

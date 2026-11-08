# Experiment 01 — scalability of bounded task-completion diagnosability (Fig. 6)

A pre-registered 8,280-evaluation study of the bounded-diagnosability analysis
on twelve Time Petri Net instance families, organised into four groups:

| group | evaluations | what varies |
|---|---:|---|
| structural size | 600 | net size (places/transitions) at fixed behaviour |
| work in process | 1,080 | work-in-process bound (1, 2, 3) on fixed base models |
| observable-history bound | 5,400 | the history bound *L* over the L-series of each base model |
| hard instances | 1,200 | instance hardness ladder at fixed size |

Execution: 120 independent worker partitions × 69 evaluations, 60 s wall-clock
cap per evaluation, 50,000 state-class cap, one physical CPU core and 4 GiB per
worker, on Modal. The study was executed **only on Modal**.

## Headline result

| metric | value |
|---|---:|
| evaluations | 8,280 |
| completed | 5,406 |
| wall-clock-capped (right-censored) | 2,874 |
| errors | 0 |
| VER / AMB / INC | 1,975 / 2,782 / 649 |
| independent audit | PASS (8,280 evaluations, 8,280 unique identifiers, 120 partitions) |
| total compute cost | $5.53 (including the preliminary validation run) |

## Contents

```
protocol/   pre-registered protocol (YAML+JSON), task manifest, partition plan,
            evaluation grid (compressed CSV archive), semantics reference,
            historical-baseline manifest
code/       runner/ (per-evaluation subprocess), src/ (verifier implementation),
            modal_app/ (Modal application), tests/ (unit tests),
            scripts/ (validate, plan, run, audit, analyse, plot)
results/    statistics.json, denominators.csv, Figure 6 (SVG/PDF/EPS/PNG),
            caption, plotting data, audit.json, group statistics,
            FINAL_ACCEPTANCE_REPORT.md
```

## Reproduce

* Protocol integrity and unit tests: see `REPRODUCE.md` §0–§1 at the repository
  root.
* Guided audit of the checked-in numbers:

```bash
python code/scripts/plot_figure6.py --analysis-dir results --out /tmp/fig6
```

* Full re-execution on Modal: `REPRODUCE.md` §2.

## Data

The 8,280 raw JSON records, the per-partition ledgers, metrics and hash
manifests are published as the release asset `scalability-evaluations` in the
archived companion repository `tii-26-7248-scalability-archive` (25.1 MB). The
checked-in `results/statistics.json` and `results/audit.json` are derived from
those files by `analyze_results.py` and `audit_results.py`.

## Rules that matter when reading the numbers

* Wall-clock-capped evaluations are right-censored, never imputed.
* INC is a separate outcome class with its own denominator.
* Time quantiles use completed evaluations only; the observed count is printed
  with every quantile.

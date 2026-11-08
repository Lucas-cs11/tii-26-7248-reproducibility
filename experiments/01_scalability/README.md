# Experiment 01 — scalability of bounded task-completion diagnosability (Fig. 6)

A pre-registered 8,280-evaluation study of the bounded-diagnosability analysis
on twelve Time Petri Net instance families, in four groups:

| group | evaluations | what varies |
|---|---:|---|
| structural size | 600 | net size at fixed behaviour |
| work in process | 1,080 | work-in-process bound (1, 2, 3) on fixed base models |
| observable-history bound | 5,400 | the history bound L |
| hard instances | 1,200 | hardness ladder at fixed size |

## Result

| metric | value |
|---|---:|
| evaluations | 8,280 |
| completed | 5,406 |
| wall-clock-capped (right-censored) | 2,874 |
| errors | 0 |
| VER / AMB / INC | 1,975 / 2,782 / 649 |

Capped evaluations are right-censored, never imputed; INC has its own
denominator; time quantiles use completed evaluations only.

## Files

```
protocol/   pre-registered protocol, task manifest, partition plan,
            evaluation grid (compressed CSV archive), semantics reference
code/       runner/, verifier implementation, cloud application, tests,
            scripts/ (validate, plan, run, audit, analyse, plot)
results/    statistics.json, denominators.csv, audit.json,
            group_statistics.csv, figure6_data.csv, figure6_metadata.json
```

## Reproduce

`REPRODUCE.md` §1 at the repository root. Redraw the figure from the checked-in
statistics:

```bash
python code/scripts/plot_figure6.py --analysis-dir results --out /tmp/fig6
```

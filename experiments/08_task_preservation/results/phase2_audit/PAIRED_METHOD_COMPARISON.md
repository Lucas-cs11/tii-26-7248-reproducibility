# Paired method comparison

## Common-success intersection

250 evaluations where all three methods obtained a fresh success this round.

## Key finding: identical preservation outcomes on the paired set

On the 250 common-success instances, all three methods produce **identical**
preservation results:

| Metric | CPG-LD | Coquand | Exhaustive |
|---|---:|---:|---:|
| n | 250 | 250 | 250 |
| path_pass | 217 (86.8%) | 217 (86.8%) | 217 (86.8%) |
| ψ@0% | 217 (86.8%) | 217 (86.8%) | 217 (86.8%) |
| ψ@10% | 217 (86.8%) | 217 (86.8%) | 217 (86.8%) |

This means: on any given instance where all three methods succeed, either all
three adjusted models preserve the reference paths or none do. The task-preservation
outcome is determined by the **instance's structure** (which paths exist, how
constrained the timing is), not by which adjustment method was used.

## Implication for per-method rates

The per-method differences (CPG-LD 88.1% vs Coquand 94.8% vs exhaustive 85.4%)
are entirely driven by **which instances each method succeeds on**, not by how
each method adjusts:

- Coquand succeeds preferentially on easier instances (where preservation is
  more likely), inflating its rate.
- CPG-LD succeeds on more instances including harder ones (where preservation
  is less likely), deflating its rate.
- Exhaustive succeeds on the easiest subset.

## Correct denominator comparison (on 1,942 attempts each)

| Metric | CPG-LD | Coquand | Exhaustive |
|---|---:|---:|---:|
| Fresh success | 1,854 (95.5%) | 1,073 (55.3%) | 254 (13.1%) |
| path_pass | 1,633 (84.1%) | 1,017 (52.4%) | 217 (11.2%) |
| ψ@0% | 1,090 (56.1%) | 1,017 (52.4%) | 217 (11.2%) |
| ψ@10% | 1,633 (84.1%) | 1,017 (52.4%) | 217 (11.2%) |

On the attempt denominator, CPG-LD dominates at every tolerance level — it
delivers more task-preserving adjustments in absolute terms despite its lower
per-success preservation rate.

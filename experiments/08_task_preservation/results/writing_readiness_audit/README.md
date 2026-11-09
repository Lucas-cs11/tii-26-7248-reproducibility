# Writing-readiness audit for the non-trivial task-preservation experiment

This directory contains an independent recomputation and writing audit. It does not modify `pilot_full/`, the formal 16,038-evaluation adjustment records, or manuscript v26.

Start with **`B1_PAPER_WRITING_EVIDENCE.md`**. It gives the final cohort-specific statistics, permitted claims, prohibited overclaims, three independent verdicts, and minimum manuscript changes.

## Reproduce the numerical audit

From a package/repository root containing `experiments/08_task_preservation/`:

```bash
python3 experiments/08_task_preservation/results/writing_readiness_audit/scripts/recompute_statistics.py
python3 experiments/08_task_preservation/results/writing_readiness_audit/scripts/build_auxiliary_tables.py
python3 experiments/08_task_preservation/results/writing_readiness_audit/scripts/analyze_performance.py
python3 experiments/08_task_preservation/results/writing_readiness_audit/scripts/validate_delivery.py --check-manifest
```

The statistical scripts use only the Python standard library. Case reconstruction requires the frozen Python 3.11 environment with NumPy 2.4.6 and SciPy 1.16.2:

```bash
<FROZEN_ENV_PYTHON> experiments/08_task_preservation/results/writing_readiness_audit/scripts/reconstruct_case.py \
  fs_m2_j2_k4_w1_ur50_fl4_wf5_ar25_s1 cpgld
<FROZEN_ENV_PYTHON> experiments/08_task_preservation/results/writing_readiness_audit/scripts/reconstruct_case.py \
  fs_m3_j1_k2_w2_ur50_fl1_wf15_ar50_s7 coquand
```

The raw pilot was executed at commit `a0d1553` by GitHub Actions run `42475575928`. Commit `64ebb3b` delivered its raw records without changing algorithm code. This directory is a later, independent writing audit; its source identity and input hashes are recorded in `SOURCE_PROVENANCE.json`.

## Verdicts

* Data for carefully scoped writing: **DATA_READY_FOR_WRITING**.
* Task-constraint implementation level: **POST_HOC_EVALUATION_ONLY**.
* B1 theoretical case: **THEORETICAL_CASE_UNRESOLVED**.

The path rates are floating-point LP audit outcomes, not exact-rational all-behavior guarantees. The primary paper cohort is the 3,060 original successes with exact adjusted-model reconstruction; the 3,181-record all-fresh-success cohort is reported separately.

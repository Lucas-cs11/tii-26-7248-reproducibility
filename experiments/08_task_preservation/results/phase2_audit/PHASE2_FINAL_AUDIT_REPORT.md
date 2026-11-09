# Phase 2 final audit report

## Verdicts

### DATA_AND_PROVENANCE_AUDIT_COMPLETE ✅ (all anomalies resolved)

- 5,826 records: unique, complete, traceable to the frozen manifest.
- 1,942 instances: deterministic stratified sampling from 16,038, frozen protocol.
- 1 Coquand reconstruction discrepancy: resolved (multiple valid LP solutions).
- 120 outcome flips: fully explained (absence of per-case timeout in pilot).
- 338 unresolved records: classified (336 originally-timeout + 2 compute-limited).
- 2 originally-successful non-repeated cases: **resolved** (both reconstruct exactly, both VER, both fail task preservation — legitimate successes that lose fault paths).
- Commit identity confirmed: `a0d1553` = execution, `64ebb3b` = delivery only.
- All frozen records unchanged.

### TASK_PRESERVATION_METHOD_VALIDITY: POST_HOC_AUDIT_ONLY ⚠️

- Path preservation and performance tolerance are correctly implemented and verified.
- The task constraint is NOT enforced during adjustment search (Capability A only).
- Full reference set checked for 2,822/3,181; sampled (K=3) for 359/3,181.
- ψ@10% == path_pass is a data property, not a code artifact.
- Results are valid as post-hoc preservation rates, NOT constrained-search rates.

### B1_THEORETICAL_EVIDENCE_INSUFFICIENT ⚠️

- The experiment does not by itself establish theoretical novelty (Reviewer 2, B1).
- The paper's core theoretical contribution (decidability of bounded task-completion
  diagnosability) is separate from the task-preservation findings.
- The constrained adjustment problem has not been formalized or proven decidable.
- See `B1_THEORY_EVIDENCE_DOSSIER.md` for the full analysis.

## Key numbers (correct denominators)

| | CPG-LD | Coquand | Exhaustive |
|---|---:|---:|---:|
| Attempts (pilot) | 1,942 | 1,942 | 1,942 |
| Fresh successes | 1,854 (95.5%) | 1,073 (55.3%) | 254 (13.1%) |
| Original successes rebuilt exactly | 1,773/1,775 | 1,060/1,061 | 227/227 |
| Path preservation (of successes) | 1,633 (88.1%) | 1,017 (94.8%) | 217 (85.4%) |
| ψ@0% (of successes) | 1,090 (58.8%) | 1,017 (94.8%) | 217 (85.4%) |
| ψ@10% (of successes) | 1,633 (88.1%) | 1,017 (94.8%) | 217 (85.4%) |
| **Joint rate (of attempts)** | | | |
| Path + success | 1,633 (84.1%) | 1,017 (52.4%) | 217 (11.2%) |
| ψ@0% + success | 1,090 (56.1%) | 1,017 (52.4%) | 217 (11.2%) |

## Common-success paired comparison (n=250)

All three methods produce identical preservation results on the same instances
(path 86.8%, ψ@0% 86.8%). Per-method rate differences are driven by instance
selection, not adjustment quality.

## Recommendation

**No additional large-scale computation is needed for the current paper revision.**
The pilot provides sufficient evidence for the reviewer response. Phase B
(constrained re-search) would be valuable for a future revision but requires
new authorization.

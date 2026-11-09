# B1 paper-writing evidence

## Section 1 — Scientific facts that can be written into the main article

1. **Verified diagnosability and preservation of designated task behavior are distinct properties.** Among the 3,060 originally successful and exactly reconstructed adjustments, 2,852 pass the selected-reference-path feasibility check (93.2026%); 208 do not. The dominant discrepancy is loss of selected fault words. This is a solver-based post-hoc check, not a proof that no satisfying alternative adjustment exists. Suggested location: Section V-B or V-C, immediately after the adjustment results.

2. **The non-trivial relationship is demonstrated by concrete models, not only by aggregate rates.** Case 1 is freshly VER with zero certificates but two designated fault words are solver-infeasible after four recovery intervals are changed. Case 2 is freshly VER with zero certificates, preserves its normal and fault reference words, and leaves the normal earliest completion time unchanged. On the same nominal model, another verified CPG-LD assignment preserves the paths but increases normal earliest completion by 1/14, failing the 0% and 5% conditions; complete paired certificates demonstrate that a verified alternative exists. Suggested location: one concise worked example in Section V, with full certificates in the supplement.

3. **The evaluated performance tiers produce different answers.** On the same 3,060-case primary cohort, 2,310 satisfy zero normal-path earliest-completion degradation (75.4902%), 2,597 satisfy 5% (84.8693%), and 2,852 satisfy 10% (93.2026%). The equality of path and 10% counts is a property of this sample, not a general performance bound. Suggested location: Section V-B or the supplement if space is limited.

4. **Conditional method rankings must not be confused with paired rankings.** On the 227 evaluations where all three methods were originally successful and again successful, each method has 216 path/0%/5%/10% passes. On their different fresh-success sets, the rates differ. On all 1,942 attempts per method, joint fresh success plus path preservation is 1,633/1,942 for CPG-LD, 1,017/1,942 for Coquand-inspired, and 217/1,942 for exhaustive. Suggested location: Section V-B, with an explicit denominator statement.

## Section 2 — Evidence suitable for the supplementary material

* Deterministic stratified selection of 1,942 of 16,038 evaluations, the frozen manifest, and the fact that this is 12.1087% of the population rather than a full-population audit.
* The distinction between original-success/exact-reconstruction, original-success-again, all-fresh-success, common-success, full-certificate-word, and sampled-reference cohorts.
* Reference-set construction: all distinct certificate words when both class counts are at most 32; otherwise three predetermined words per class. Full-certificate-word coverage is not coverage of every legal task execution.
* The numerical LP implementation and its \(10^{-9}\) tolerances; rational formatting of floating results is not exact-rational solving.
* Detailed statistics in `FINAL_TASK_PRESERVATION_STATISTICS.csv`, `REFERENCE_PATH_COVERAGE.csv`, and `STATISTICAL_RECOMPUTATION_REPORT.md`.
* The two complete model/certificate packages, the Coquand discrepancy dossier, all 120 flip classifications, and the 338 compute-limit accounting.
* Scope limits: the pilot uses unconstrained adjustment followed by post-hoc evaluation; it is not a constrained re-search experiment.

## Section 3 — Claims that currently cannot be written into the paper

* That the non-trivial task predicate was enforced or guaranteed by the adjustment search in this experiment.
* That all legal task behaviors, all bounded complete executions, or all original feasible completion times were preserved.
* That a post-hoc path failure proves that no satisfying alternative adjustment exists.
* That any method is universally better, or that rates on 1,942 evaluations directly estimate all 16,038 without further weighting/assumptions.
* That a universal 10% performance bound holds, or that paired concordance proves an instance-only law.
* That the early history-merge implementation discrepancy demonstrates a defect in classical SCG theory.
* That duration enclosure has a universally significant acceleration effect.
* That the two Coquand assignments are equivalent optimal solutions, or that the frozen record is erroneous without further evidence.
* That the 338 compute-limited cases are mathematical failures or non-repairable instances.
* That this experiment alone establishes theoretical novelty, a new decidability result, a completeness theorem, or a complexity improvement.

## Section 4 — Recommended final statistics

### A. Primary cohort for claims about the original successful adjustments

Original formal success, fresh VER again, and exact adjusted-model hash reconstruction. Percentages are post-hoc floating-LP check outcomes.

| Method | n | Path feasible | 0% | 5% | 10% |
|---|---:|---:|---:|---:|---:|
| CPG-LD | 1,773 | 1,622 (91.4834%) | 1,080 (60.9137%) | 1,367 (77.1010%) | 1,622 (91.4834%) |
| Coquand-inspired | 1,060 | 1,014 (95.6604%) | 1,014 (95.6604%) | 1,014 (95.6604%) | 1,014 (95.6604%) |
| One-step exhaustive | 227 | 216 (95.1542%) | 216 (95.1542%) | 216 (95.1542%) | 216 (95.1542%) |
| All | 3,060 | 2,852 (93.2026%) | 2,310 (75.4902%) | 2,597 (84.8693%) | 2,852 (93.2026%) |

The broader original-success-again cohort adds the unresolved Coquand model: n=3,061; path=2,852 (93.1722%), 0%=2,310 (75.4655%), 5%=2,597 (84.8416%), 10%=2,852 (93.1722%). It is a sensitivity cohort, not the primary exact-reconstruction cohort.

### B. Full fresh-success cohort for claims about the pilot rerun itself

| Method | n | Path feasible | 0% | 5% | 10% |
|---|---:|---:|---:|---:|---:|
| CPG-LD | 1,854 | 1,633 (88.0798%) | 1,090 (58.7918%) | 1,378 (74.3258%) | 1,633 (88.0798%) |
| Coquand-inspired | 1,073 | 1,017 (94.7810%) | 1,017 (94.7810%) | 1,017 (94.7810%) | 1,017 (94.7810%) |
| One-step exhaustive | 254 | 217 (85.4331%) | 217 (85.4331%) | 217 (85.4331%) | 217 (85.4331%) |
| All | 3,181 | 2,867 (90.1289%) | 2,324 (73.0588%) | 2,612 (82.1125%) | 2,867 (90.1289%) |

This cohort includes 120 original-status flips. Those 120 have path 15/120, 0% 14/120, 5% 15/120, and 10% 15/120. They must not be silently pooled with the original-success cohort when discussing the formal adjustment results.

### C. Joint fresh success and preservation on attempts

| Method | Attempts | Fresh VER | Path + VER | 0% + VER | 10% + VER |
|---|---:|---:|---:|---:|---:|
| CPG-LD | 1,942 | 1,854 (95.4686%) | 1,633 (84.0886%) | 1,090 (56.1277%) | 1,633 (84.0886%) |
| Coquand-inspired | 1,942 | 1,073 (55.2523%) | 1,017 (52.3687%) | 1,017 (52.3687%) | 1,017 (52.3687%) |
| One-step exhaustive | 1,942 | 254 (13.0793%) | 217 (11.1740%) | 217 (11.1740%) | 217 (11.1740%) |

### D. Reference-set regimes across all fresh successes

| Regime | n | Path feasible | 0% | 5% | 10% |
|---|---:|---:|---:|---:|---:|
| Full certificate-word set | 2,822 | 2,755 (97.6258%) | 2,244 (79.5181%) | 2,507 (88.8377%) | 2,755 (97.6258%) |
| Deterministic three-per-class sample | 359 | 112 (31.1978%) | 80 (22.2841%) | 105 (29.2479%) | 112 (31.1978%) |

The regime difference is descriptive and confounded with certificate-set size/complexity; it is not a causal estimate of sampling error.

### E. Paired results

* Three-method fresh-success intersection: n=250; each method has path=217, 0%=217, 5%=217, 10%=217. Per-instance discordance is zero for every reported predicate tier.
* Three-method original-success intersection: n=227; each method has path=216, 0%=216, 5%=216, 10%=216.

All tables are generated from `statistics.json` and `FINAL_TASK_PRESERVATION_STATISTICS.csv`. Missing-baseline count is zero, but raw pilot records do not distinguish LP infeasibility from numerical unknown; representative cases carry direct LP statuses.

## Section 5 — How this helps the B1 discussion

### A. Support for problem motivation

The experiment shows that eliminating bounded completion-time ambiguity is not synonymous with retaining designated task behavior. It therefore supplies a concrete application reason for stating task-preservation requirements explicitly rather than treating VER as a sufficient deployment condition.

### B. Support for understanding the method mechanism

The case studies show how recovery-interval changes can remove ambiguity while either retaining or losing selected executions. The statistics characterize the frequency and performance structure of those outcomes on specified cohorts. Fresh complete re-verification remains necessary: the task audit does not replace the diagnosis certificate.

### C. What remains missing for correctness and theoretical novelty

The experiment does not compare the formal construction with prior literature, prove existence/completeness for constrained adjustment, establish a new complexity bound, or turn numerical observations into exact-rational theorems. v26 already has a generic termination-and-soundness theorem for an effective predicate used in the finite search; the new experiment does not exercise that theorem for the non-trivial predicate. A stronger theoretical case requires formal proof and literature analysis, not additional percentages.

## Section 6 — Minimum necessary manuscript changes

1. Retain the original full-population adjustment counts, but state explicitly that their large-sample comparison used the constant task predicate and does not by itself certify the non-trivial behavior conditions evaluated here.
2. Keep Algorithm 2 and its generic soundness/termination theorem, while clarifying that the guarantee applies to the effective predicate actually enforced during candidate admissibility, not to a predicate checked only afterward.
3. Add one concise results paragraph using Table A or Table B, with the denominator and post-hoc status in the same paragraph. Do not mix their percentages.
4. Add the two representative examples to the supplement, with complete model and verification certificates. One main-text example is sufficient if space is tight.
5. Add a supplementary subsection containing cohort/reference definitions, numerical LP limits, the flip/compute-limit accounting, and the unresolved Coquand discrepancy.
6. Narrow any wording that suggests all task behavior is preserved, constrained re-search has been demonstrated, or unsuccessful searches prove non-repairability.
7. Do not add claims of theoretical novelty, universal performance bounds, or universal method superiority on the basis of this experiment.
8. No new large experiment is necessary for an accurate post-hoc v27 revision. A new constrained-search implementation/experiment is necessary only if the paper wishes to claim that the non-trivial predicate is enforced during search or that satisfying alternative adjustments are found.

## Writing-readiness verdicts

* **DATA_READY_FOR_WRITING** — subject to the cohort, numerical, and scope qualifications above.
* **POST_HOC_EVALUATION_ONLY** — the non-trivial task predicate was not enforced by the pilot search.
* **THEORETICAL_CASE_UNRESOLVED** — the experimental evidence does not by itself settle Reviewer 2's novelty objection.

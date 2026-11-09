# Representative task-preservation case studies

Both cases were independently reconstructed from the frozen generator inputs. Each certificate contains the complete nominal and adjusted TPN definitions (places, transitions, labels, arcs, initial/completion markings, and intervals), the original frozen result, reference words, baseline completion intervals, candidate verification metadata, and predicate results. The candidate models have `COMPLETE_SET`, `enumeration_complete=true`, `VER`, and zero certificates. Their model hashes match the frozen successful records.

## Case 1 — verified diagnosability with loss of designated fault executions

Evidence: `REPRESENTATIVE_EXACT_CERTIFICATES/fs_m2_j2_k4_w1_ur50_fl4_wf5_ar25_s1/`.

The nominal model is a two-machine, two-part, four-operation instance with \(L=18\), \(H=66\), and 30 ambiguity certificates. Its certificate reference contains two normal and 30 distinct fault words. CPG-LD changes four recovery transitions from \([1,3]\) to the singleton \([719/64,719/64]\) (approximately 11.234). The adjusted model is freshly verified with zero critical pairs and matches frozen hash `1c7697c29a2267d3`.

Both normal words remain feasible with unchanged earliest completion time 18. Of the 30 fault words, 28 remain feasible, while two return `INFEASIBLE` on direct minimum and maximum LP checks. One lost word, for example, follows job 1 through four operations with a fault in operation 4, then job 2 with faults in operations 2–4 before completion. Its nominal completion interval is feasible, but no feasible completion remains after the adjustment within \(H=66\).

**Scientific conclusion:** the adjustment removes bounded normal/fault completion-time ambiguity but does not preserve every designated fault execution. This is an existence result for a non-trivial relationship between diagnosability and selected task behavior, not a claim that no alternative adjustment exists.

## Case 2 — verified diagnosability with designated behavior and zero normal-path degradation

Evidence: `REPRESENTATIVE_EXACT_CERTIFICATES/fs_m3_j1_k2_w2_ur50_fl1_wf15_ar50_s7/`.

The nominal model is a three-machine, one-part, two-operation instance with \(L=6\), \(H=19.5\), and one ambiguity certificate. The Coquand-inspired one-shot adjustment changes one recovery transition from \([1,3]\) to \([9/2,9/2]\). The adjusted model is freshly verified with zero critical pairs and matches frozen hash `fe3d6442db72fd5f`.

The sole normal reference word remains feasible; its earliest completion time is \(7/2\) before and after adjustment. The sole fault reference word also remains feasible: its nominal completion interval is \([11/2,23/2]\), and its adjusted earliest completion time is 9. Thus path preservation and all three performance tiers pass.

**Scientific conclusion:** verified diagnosability and the evaluated task-preservation condition can hold simultaneously. The two cases demonstrate that the relationship is non-vacuous in both directions on actual frozen instances.

## Additional alternative-candidate evidence

On the Case-2 nominal model, CPG-LD returns a different verified assignment that preserves both reference paths but increases normal earliest completion from 7/2 to 15/4 (+1/14), hence failing the 0% and 5% conditions. The Coquand-inspired assignment above satisfies all conditions. Complete paired evidence is in `ALTERNATIVE_CANDIDATE_AUDIT/`. This demonstrates the relevance of candidate selection; it does not demonstrate a constrained-search success.

## Evidence boundary

The LP outcomes are floating-point HiGHS results with recorded statuses, not exact-rational certificates. The reference sets are complete certificate-word sets for these cases, not all legal task executions. No broader all-behavior or universal performance guarantee follows.

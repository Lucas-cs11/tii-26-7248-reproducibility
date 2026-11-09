# Coquand case resolution

Case: `fs_m3_j2_k2_w2_ur50_fl2_wf5_ar10_s6`, Coquand-inspired adjustment.

## Frozen record and current independent runs

| Evidence | Model hash | Modified transitions | \(C_I\) | Verification |
|---|---|---:|---:|---|
| Frozen formal record | `7868dcfd319e2666` | 2 | 2.531250 | VERIFIED_SUCCESS |
| Current original runner on macOS | `d076ab72c93739f7` | 2 | 2.250000 | VER, 0 certificates |
| Current pilot runner on macOS | `d076ab72c93739f7` | 2 | 2.250000 | VER, 0 certificates |
| Earlier pilot runner on Linux | `d076ab72c93739f7` | 2 | 2.250000 | VER, 0 certificates |

The two current runners agree across the two operating systems, but neither reproduces the frozen hash. The current original runner used the frozen source and its original 120 s verification / 300 s repair settings; it completed in 234.1062 s. The frozen record reported 605.2958 s. Raw outputs and command templates are in `COQUAND_CASE_RESOLUTION/`.

## Interpretation

The two hash values identify different valid verified assignments. They are **not** shown to be equally optimal. In particular, \(C_I\) is a post-hoc cost term here; the Coquand-inspired routine consolidates per-certificate restrictions and does not globally minimize the CPG-LD lexicographic objective. The lower current cost therefore does not prove a better algorithm or an “equivalent optimum.”

The frozen interval assignment was not persisted, so its exact intervals, independent task predicate result, and optimality cannot be reconstructed from the record alone. Possible contributors include numerical LP path differences and incomplete environment/version provenance, but no unique cause is established.

## Statistical disposition

Classification: **`FROZEN_RECORD_NOT_REPRODUCED_UNDER_CURRENT_ENVIRONMENT_UNRESOLVED`**.

The frozen formal record is not modified or declared erroneous. The current candidate is retained as a valid fresh-VER observation but excluded from the **exact-reconstruction** primary cohort. It remains in the broader original-success-again and all-fresh-success cohorts, which are reported separately. The current candidate fails the sampled path predicate because one selected fault word is solver-infeasible; no claim is made about the unavailable frozen candidate's task status.

This single unresolved historical discrepancy does not affect the arithmetic of the other 3,060 exact reconstructions and does not justify changing any hash or tolerance.

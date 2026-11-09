# Alternative-candidate audit

## Result: a verified alternative exists under the full path-plus-performance predicate

A scan of existing returned candidates found 337 ordered method pairs with discordant 0% outcomes, 186 with discordant 5% outcomes, and none with discordant 10% outcomes. This is a scan of returned candidates, not an exhaustive-domain search.

The clearest example is the nominal model used in Case 2 (`initial_model_hash=8d98729e374bc0d2`). Both adjusted models are independently reconstructed, match their frozen successful hashes, and have fresh `COMPLETE_SET`, `enumeration_complete=true`, `VER`, zero certificates.

| Property | CPG-LD candidate | Coquand-inspired candidate |
|---|---|---|
| Adjusted model hash | `d7732d936fd03370` | `fe3d6442db72fd5f` |
| Interval changes | processing \([3/4,9/4]\to[1,3/2]\); recovery \([1,3]\to[7/2,5]\) | recovery \([1,3]\to[9/2,9/2]\) only |
| Modified transitions | 2 | 1 |
| \(C_I\) | 5.5 | 5.0 |
| Reference path check | pass | pass |
| Normal earliest completion | \(7/2\to15/4\), increase \(1/14\approx7.14\%\) | \(7/2\to7/2\), unchanged |
| 0% / 5% / 10% | fail / fail / pass | pass / pass / pass |

Evidence: `ALTERNATIVE_CANDIDATE_AUDIT/cpgld/certificate.json` and `ALTERNATIVE_CANDIDATE_AUDIT/coquand_certificate.json`.

**Scientific conclusion:** for this nominal model, the adjustment search returned a verified candidate that fails the 0% and 5% task-performance conditions, while another verified candidate satisfies those conditions and path preservation. This directly demonstrates why the task condition must influence candidate selection when such performance is required.

It does **not** show that a constrained CPG-LD search would find the Coquand-inspired candidate: no non-trivial gated re-search was run, and inclusion of that exact assignment in every method's candidate family has not been proved. A path-loss-only scan found no cross-method pair where one candidate lost a reference path and another retained all paths; the positive result here concerns the full predicate including performance.

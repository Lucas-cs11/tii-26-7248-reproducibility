# B1 theory evidence map

This map separates formal properties in v26 from empirical observations. It does not decide Reviewer 2's novelty objection.

| Topic | Formal status in v26 | Implementation/experiment evidence | Boundary |
|---|---|---|---|
| First-completion observation | Defined over first entry into completion markings, event order, and one total duration | Complete-set verifier and certificates use the same boundary | This is the paper's problem formulation, not classical SCG itself |
| Critical-pair characterization | Proposition: bounded diagnosability iff no critical pair | Certificate sets are the adjustment input | Proof is in the manuscript; experiments do not replace it |
| Candidate-word coverage | Theorem 1 proves every critical-pair word is retained | 36,450-case reference agreement is empirical support only | No speedup follows from candidate existence alone |
| History-dependent timing | The verifier retains distinct firing histories until path feasibility is checked | Prior history-merge differences were implementation defects | Do not describe the defect as a failure of classical SCG theory |
| Path-polytope feasibility | Proposition 2 gives the exact mathematical feasibility condition | HiGHS floating-point LP implements the numerical check | Exact mathematical proposition and numerical evidence must be distinguished |
| Complete bounded verification | Theorem 2 gives verdict equivalence under termination | Fresh adjusted models in the two case studies have VER, zero certificates, complete enumeration | INC/compute limits remain possible and are not non-diagnosability |
| Lexicographic adjustment | Finite-domain termination and soundness of any returned model are proved | Frozen CPG-LD uses staged candidates and re-verification | No existence, global optimality, or Cartesian-product completeness guarantee |
| Generic task predicate | Algorithm 2/Theorem apply to any effective predicate actually used for admissibility | The pilot used AlwaysTrue and evaluated another predicate afterward | The generic formal guarantee was not exercised for the non-trivial audit predicate |
| Non-trivial task preservation | Designated nominal sequences are used in sensitivity studies; no all-behavior guarantee | Post-hoc path/performance rates and two concrete cases | Empirical motivation and algorithm behavior, not a new decidability theorem |
| Duration enclosure | Disjoint sound enclosures safely reject pairs | Prior audits found variable pruning effectiveness | Do not claim a universally significant acceleration |
| Task performance tiers | Not part of the general adjustment theorem unless supplied as the effective predicate and enforced | Experimental 0/5/10% earliest-completion comparisons | Cannot cite the theorem as proof of these post-hoc tiers |

## What this contributes to the B1 discussion

The experiment supports the **application necessity** of distinguishing bounded diagnosability from preservation of designated task behavior. It also demonstrates why a returned adjustment must be accompanied by an explicit task-preservation contract if such behavior matters. It does not show that SCG, critical-pair analysis, LP, or finite search is individually new, and it does not prove a new existence, completeness, or complexity theorem.

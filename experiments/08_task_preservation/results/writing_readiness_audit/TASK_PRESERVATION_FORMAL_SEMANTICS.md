# Formal semantics of the evaluated task-preservation conditions

## Paper definitions used as the reference

The manuscript defines a task by first entry into a completion marking, not by a firing sequence (v26 main, lines 177–179 and 249–256). A complete timed execution has a firing sequence and a total duration. Its bounded completion-time set is
\[
T_H^N(\sigma)=\{d\in[0,H]\mid \exists\rho\in\operatorname{CompRuns}(N):
\sigma_\rho=\sigma,\ \operatorname{dur}(\rho)=d\}
\]
(v26 main, Definition of the critical pair and Eq. 10, lines 310–321). The adjustment section admits a generic predicate \(\psi_{\mathrm{task}}\) (Definition of admissible adjustment, lines 716–723); it does not define the 0%, 5%, or 10% thresholds used in this audit.

## What the experiment actually checks

Let \(C_0\) be the complete-set AMB certificate enumeration of the nominal model \(N_0\) under the same \((L,H)\). Define \(S_N\) and \(S_F\) as the distinct certificate words \(\sigma_N\) and \(\sigma_F\), respectively. These are firing sequences of complete executions participating in confirmed ambiguity certificates. They are not, without further proof, all complete executions of \(N_0\).

The reference set is selected before adjustment and is identical for all methods:

* if \(|S_N|\le32\) and \(|S_F|\le32\), the **full-certificate-word regime** uses all of \(S_N\cup S_F\);
* otherwise the **sampled regime** selects three words per class by sorting on SHA-256 of `evaluation_id | class | comma-separated word`, then taking the first three.

The selection implementation is `code/predicate.py`, lines 21–35. Complete-set reference metadata for the two representative cases is independently recorded in their `reference_verification.json` files (`enumeration_complete=true`).

For a selected reference set \(R_N\subseteq S_N\), \(R_F\subseteq S_F\), the path condition is
\[
\psi_{\mathrm{path}}(N')
\iff
\forall\sigma\in R_N\cup R_F:\quad T_H^{N'}(\sigma)\ne\varnothing .
\]
Thus it checks **existence of at least one timed execution following the same firing sequence within \(H\)**. It is stronger than merely retaining the transition sequence structurally, but much weaker than preserving the original feasible-time interval, every timed realization, or every legal task behavior.

The performance condition is evaluated only on selected normal words. Let \(t_0(\sigma)=\min T_H^{N_0}(\sigma)\) and \(t'(\sigma)=\min T_H^{N'}(\sigma)\). For tolerance tier \(\tau\in\{0,0.05,0.10\}\),
\[
\psi_\tau(N')\iff
\psi_{\mathrm{path}}(N')\ \land\
\forall\sigma\in R_N:\ t'(\sigma)\le (1+\tau)t_0(\sigma),
\]
with zero absolute tolerance when \(t_0(\sigma)=0\). Missing baselines make the combined check fail; see `code/predicate.py`, lines 59–104. Fault words have a feasibility requirement but no performance threshold.

## Mapping to possible meanings of “preservation”

| Candidate meaning | Established by this experiment? |
|---|---|
| Same transition sequence remains structurally present | Implied where the timed LP is feasible, but not the property directly measured |
| Same firing sequence has at least one feasible timed realization within \(H\) | **Yes, for the selected reference words, using the floating-point LP oracle** |
| At least one adjusted completion time satisfies the original bounded path condition | **Yes, in the same limited sense** |
| Every original feasible completion time of the sequence is retained | **No** |
| Every word in the frozen finite reference set remains feasible | **Yes, subject to the LP-status caveat** |
| Every relevant bounded execution of the nominal model remains feasible | **No** |
| Normal-path earliest completion stays within an experimental tolerance | **Yes, for selected normal words only** |

Consequently, the experiment supports “preservation of designated nominal complete firing sequences” in the sense already used for sensitivity studies in Supplementary Material Section S7-C (v26 supplementary, line 1160). It does not support “preservation of all task behavior” or “preservation of all feasible timings.” The performance tiers are additional experimental criteria, not guarantees of Algorithm 2 or its theorem.

## Full versus sampled reference coverage

“Full” refers only to all distinct words present in a completed certificate enumeration under the tested bounds. It does not mean mathematical completeness over all task executions. For the sampled regime, the reference is fixed before adjustment, so there is no selection of favorable paths after seeing the result; nevertheless, only six paths are checked and no all-behavior conclusion follows.

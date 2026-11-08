# Historical-baseline audit report

## Scope

A fixed sample of the archived baseline is recomputed with the current
implementation to show that the revised semantics do not change archived
verdicts. The sample is disjoint from the 8,280-evaluation scalability study.

## Result

| item | value |
|---|---:|
| recomputed evaluations | 3,645 (555 bounded problems; VER 1,689 / AMB 1,956) |
| primary pass recorded | 3,645 / 3,645 |
| **verdict changes** | **0** (VER 1,689→1,689, AMB 1,956→1,956; 0 INC, 0 undecidable) |
| full second pass (archived AMB rows) | 1,956 / 1,956 (1,136 completed, 820 wall-clock-capped) |
| critical-pair comparison (AMB rows) | archived mean 68,224.5 vs recomputed 2,457.3 pairs; 274 increased / 862 decreased; median ratio 0.149 |
| certificate overlap inside the archived window | 1,136 / 1,136 (width p50 2.5 s, p95 5.5 s) |
| state-class counts under the current implementation | smaller in 1,925 evaluations, larger in 31, identical in 0 (median −392 classes) |

## Counter-definition caveat

The archived record stores a critical-pair count that is a complete enumeration
under the archived semantics; the recomputed count is the current terminal-pair
counter plus enclosure-rejected pairs. The two are compared explicitly and are
not definitionally identical. The number of LP-feasible ambiguity certificates
is reported separately (mean 2,382.5 per AMB row, 0 rows without a feasible
pair).

## Limits

* The archived records do not store the certificate mode (first-certificate is
  the documented assumption).
* The reference-baseline re-run is planned only; it reuses the shared
  state-class builder and is therefore not an independent oracle.
* The conservative upper bound of the affected population (36,450 rows) is not
  fully certified; 32,805 non-conflict rows are outside the certified sample.

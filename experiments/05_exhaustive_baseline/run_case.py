#!/usr/bin/env python3
"""Run exactly ONE (evaluation, method) adjustment case and print one JSON record.

Methods:
  cpgld      -> src.repair.algorithm.repair            (Algorithm 2, CPG-LD)
  coquand    -> src.repair.global_constraint_repair    (Coquand-inspired, one-shot global synthesis)
  exhaustive -> src.repair.exhaustive.exhaustive_repair(one-step exhaustive over authorized Cartesian product)

Protocol recovered from the frozen old experiment:
  repair_domain = "extended";  verify complete_set=True, budget=None
  verify_timeout = 120 s;      repair_timeout = 300 s
  task predicate = AlwaysTrue (psi_task == 1, legacy batch behaviour)
  objective variant = O0

Success requires a FRESH complete-set re-verification: verdict == VER and
final certificate set empty.  Anything else is never reported as success.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import signal
import sys
import time
from fractions import Fraction
from pathlib import Path

SNAPSHOT = Path(__file__).resolve().parents[1] / "source_snapshot"
sys.path.insert(0, str(SNAPSHOT))

from src.benchmarks.rmt_fms_generator import generate_rmt_fms
from src.verifier import verify
from src.repair.algorithm import repair, lexicographic_objective
from src.repair.exhaustive import exhaustive_repair
from src.repair.global_constraint_repair import global_constraint_repair
from src.repair.task_constraint import AlwaysTrueTaskConstraint

PARAM_FIELDS = [
    "n_machines", "n_parts", "ops_per_part", "wip_bound",
    "unobservable_ratio", "fault_locations",
    "interval_width_factor", "adjustable_ratio", "seed",
]

VERIFY_TIMEOUT = float(os.environ.get("TA_VERIFY_TIMEOUT", "120"))
REPAIR_TIMEOUT = float(os.environ.get("TA_REPAIR_TIMEOUT", "300"))
NA = "NA"


class _Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise _Timeout()


signal.signal(signal.SIGALRM, _alarm)


def with_timeout(seconds: float, fn):
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        return fn()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def model_hash(tpn) -> str:
    data = {
        "places": sorted(tpn.places.keys()),
        "transitions": sorted(
            [
                {
                    "name": n,
                    "label": t.label,
                    "fault": t.is_fault,
                    "earliest": str(t.interval.earliest),
                    "latest": str(t.interval.latest),
                }
                for n, t in tpn.transitions.items()
            ],
            key=lambda x: x["name"],
        ),
        "arcs": sorted(f"{a.from_node}->{a.to_node}" for a in tpn.arcs),
        "initial_marking": sorted(tpn.initial_marking.items()),
        "completion_markings": [sorted(m.items()) for m in tpn.completion_markings],
    }
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]


def representable_count(tpn) -> int:
    total = 1
    for t in tpn.transitions.values():
        if getattr(t, "is_adjustable", False):
            n = len(t.admissible_intervals or [])
            total *= max(n, 1)
    return total


def repair_problem_hash(tpn, L, H) -> str:
    """Hash of the actual adjustment problem (post-generation structure incl. domains)."""
    parts = [model_hash(tpn), str(L), str(H)]
    for n in sorted(tpn.transitions):
        t = tpn.transitions[n]
        if getattr(t, "is_adjustable", False):
            adm = sorted(
                (str(i.earliest), str(i.latest)) for i in (t.admissible_intervals or [])
            )
            ar = t.authorized_range
            ar_s = NA if ar is None else f"{ar.l_min}:{ar.l_max}:{ar.u_min}:{ar.u_max}:{ar.resolution}"
            parts.append(f"{n}|{adm}|{ar_s}")
    return hashlib.sha256(";".join(parts).encode()).hexdigest()[:16]


def frac_to_json(x):
    if x is None:
        return NA
    if isinstance(x, Fraction):
        return f"{float(x):.6f}"
    try:
        return f"{float(x):.6f}"
    except (TypeError, ValueError):
        return str(x)


def main() -> int:
    if len(sys.argv) < 6:
        print(json.dumps({"status": "ERROR", "error_type": "BAD_ARGV"}))
        return 2
    method = sys.argv[1]
    evaluation_id = sys.argv[2]
    params = json.loads(sys.argv[3])
    L = int(sys.argv[4])
    H = float(sys.argv[5])

    rec = {
        "evaluation_id": evaluation_id,
        "method": method,
        "initial_model_hash": NA,
        "repair_problem_hash": NA,
        "L": L,
        "H": H,
        "adjustable_ratio": params.get("adjustable_ratio"),
        "n_adjustable_transitions": NA,
        "representable_assignment_count": NA,
        "status": "ERROR",
        "runtime_seconds": NA,
        "iterations": NA,
        "candidate_evaluations": NA,
        "verifier_calls": 0,
        "LP_calls": 0,
        "initial_critical_pair_count": NA,
        "final_critical_pair_count": NA,
        "modified_transition_count": NA,
        "CI": NA,
        "W": NA,
        "final_model_hash": NA,
        "task_predicate_pass": NA,
        "fresh_reverification_verdict": NA,
        "timeout_seconds": NA,
        "error_type": NA,
        "timeout_phase": NA,
        "solve_status": NA,
        "backend_status": NA,
        "execution_path": NA,
    }

    t_case = time.perf_counter()
    verify_calls = {"n": 0, "lp": 0}

    try:
        tpn, gen_L, gen_H = generate_rmt_fms(**{k: params[k] for k in PARAM_FIELDS},
                                             repair_domain="extended")
    except Exception as e:  # noqa: BLE001
        rec["error_type"] = f"GENERATION_ERROR:{type(e).__name__}"
        rec["runtime_seconds"] = round(time.perf_counter() - t_case, 4)
        print(json.dumps(rec))
        return 0

    rec["initial_model_hash"] = model_hash(tpn)
    rec["L"] = gen_L
    rec["H"] = gen_H
    rec["n_adjustable_transitions"] = sum(
        1 for t in tpn.transitions.values() if getattr(t, "is_adjustable", False)
    )
    rec["representable_assignment_count"] = representable_count(tpn)
    rec["repair_problem_hash"] = repair_problem_hash(tpn, gen_L, gen_H)

    if gen_L != L or abs(float(gen_H) - H) > 1e-9:
        rec["error_type"] = "LH_MISMATCH"
        rec["runtime_seconds"] = round(time.perf_counter() - t_case, 4)
        print(json.dumps(rec))
        return 0

    def counted_verify(t, complete=True):
        verify_calls["n"] += 1
        out = verify(t, gen_L, gen_H, complete_set=complete)
        try:
            stats = out.get("stats") or {}
            verify_calls["lp"] += int(stats.get("lp_calls") or 0)
        except (TypeError, ValueError):
            pass
        return out

    # ---- initial complete verification (must be AMB) -------------------
    try:
        initial = with_timeout(VERIFY_TIMEOUT, lambda: counted_verify(tpn))
    except _Timeout:
        rec["status"] = "TIMEOUT"
        rec["timeout_phase"] = "initial_verify"
        rec["timeout_seconds"] = VERIFY_TIMEOUT
        rec["runtime_seconds"] = round(time.perf_counter() - t_case, 4)
        rec["verifier_calls"] = verify_calls["n"]
        rec["LP_calls"] = verify_calls["lp"]
        print(json.dumps(rec))
        return 0
    except Exception as e:  # noqa: BLE001
        rec["error_type"] = f"INITIAL_VERIFY_ERROR:{type(e).__name__}"
        rec["runtime_seconds"] = round(time.perf_counter() - t_case, 4)
        print(json.dumps(rec))
        return 0

    certs = initial.get("certificates", []) or []
    rec["initial_critical_pair_count"] = len(certs)
    try:
        width = Fraction(0)
        for c in certs:
            lo, hi = c.overlap
            width += max(Fraction(0), Fraction(hi) - Fraction(lo))
        rec["W"] = frac_to_json(width)
    except Exception:  # noqa: BLE001
        rec["W"] = NA

    if initial.get("result") != "AMB":
        rec["status"] = "ERROR"
        rec["error_type"] = f"POPULATION_VERDICT_MISMATCH:{initial.get('result')}"
        rec["fresh_reverification_verdict"] = initial.get("result")
        rec["runtime_seconds"] = round(time.perf_counter() - t_case, 4)
        rec["verifier_calls"] = verify_calls["n"]
        rec["LP_calls"] = verify_calls["lp"]
        print(json.dumps(rec))
        return 0
    if not certs:
        rec["status"] = "ERROR"
        rec["error_type"] = "AMB_WITHOUT_CERTIFICATES"
        rec["runtime_seconds"] = round(time.perf_counter() - t_case, 4)
        print(json.dumps(rec))
        return 0

    task_constraint = AlwaysTrueTaskConstraint()
    candidate_tpn = None
    backend_status = None
    solve_status = None
    iterations = NA
    cand_evals = NA

    try:
        t0 = time.perf_counter()
        if method == "cpgld":
            res = with_timeout(
                REPAIR_TIMEOUT,
                lambda: repair(
                    tpn, certs, gen_L, gen_H,
                    verifier_fn=counted_verify,
                    task_constraint=task_constraint,
                    objective_variant="O0",
                ),
            )
            backend_status = res.status
            iterations = res.iterations
            cand_evals = res.candidates_evaluated
            solve_status = res.solve_status if res.solve_status is not None else NA
            candidate_tpn = res.repaired_tpn
            rec["execution_path"] = "cpgld"
        elif method == "coquand":
            res = with_timeout(REPAIR_TIMEOUT, lambda: global_constraint_repair(tpn, certs, gen_H))
            backend_status = res.get("status")
            candidate_tpn = res.get("modified_tpn")
            rec["execution_path"] = "coquand"
            if backend_status == "SUCCESS" and candidate_tpn is not None:
                # beyond Coquand: fresh complete re-verification
                v = with_timeout(VERIFY_TIMEOUT, lambda: counted_verify(candidate_tpn))
                rec["fresh_reverification_verdict"] = v.get("result")
                rec["final_critical_pair_count"] = len(v.get("certificates") or [])
                if v.get("result") != "VER" or rec["final_critical_pair_count"]:
                    rec["status"] = "FINITE_SEARCH_FAILURE"
                    rec["error_type"] = "NEW_CERTS_EMERGED"
                    rec["backend_status"] = backend_status
                    rec["runtime_seconds"] = round(time.perf_counter() - t_case, 4)
                    rec["verifier_calls"] = verify_calls["n"]
                    rec["LP_calls"] = verify_calls["lp"]
                    rec["final_model_hash"] = model_hash(candidate_tpn)
                    print(json.dumps(rec))
                    return 0
                # else fall through to success bookkeeping
        elif method == "exhaustive":
            res = with_timeout(
                REPAIR_TIMEOUT,
                lambda: exhaustive_repair(
                    tpn, certs, gen_L, gen_H,
                    verifier_fn=counted_verify,
                    task_constraint=task_constraint,
                    max_scope_combinations=200_000,
                ),
            )
            backend_status = res.status
            solve_status = res.solve_status if res.solve_status is not None else NA
            cand_evals = res.candidates_evaluated
            iterations = res.iterations
            candidate_tpn = res.repaired_tpn
            rec["execution_path"] = "exhaustive"
        else:
            rec["status"] = "ERROR"
            rec["error_type"] = "UNKNOWN_METHOD"
            print(json.dumps(rec))
            return 0
        repair_elapsed = time.perf_counter() - t0
    except _Timeout:
        rec["status"] = "TIMEOUT"
        rec["timeout_phase"] = "repair"
        rec["timeout_seconds"] = REPAIR_TIMEOUT
        rec["backend_status"] = backend_status if backend_status else NA
        rec["runtime_seconds"] = round(time.perf_counter() - t_case, 4)
        rec["verifier_calls"] = verify_calls["n"]
        rec["LP_calls"] = verify_calls["lp"]
        print(json.dumps(rec))
        return 0

    rec["backend_status"] = backend_status if backend_status is not None else NA
    if solve_status is not None:
        rec["solve_status"] = solve_status
    rec["iterations"] = iterations
    rec["candidate_evaluations"] = cand_evals

    # ---- classify --------------------------------------------------------
    def finish(status: str, **kw):
        rec["status"] = status
        for k, v in kw.items():
            rec[k] = v
        rec["runtime_seconds"] = round(time.perf_counter() - t_case, 4)
        rec["verifier_calls"] = verify_calls["n"]
        rec["LP_calls"] = verify_calls["lp"]
        print(json.dumps(rec))
        return 0

    if backend_status == "INCONCLUSIVE":
        return finish("INC", error_type="BUDGET_EXCEEDED")
    if backend_status != "SUCCESS" or candidate_tpn is None:
        if method == "coquand":
            return finish("NO_IMPROVING_CANDIDATE")
        if method == "exhaustive":
            if solve_status == "BUDGET_EXCEEDED":
                return finish("TIMEOUT", timeout_phase="budget", timeout_seconds=REPAIR_TIMEOUT)
            return finish("FINITE_SEARCH_FAILURE")
        return finish("FINITE_SEARCH_FAILURE")

    # Success path -> fresh complete re-verification
    try:
        v = with_timeout(VERIFY_TIMEOUT, lambda: counted_verify(candidate_tpn))
    except _Timeout:
        return finish(
            "TIMEOUT", timeout_phase="final_verify", timeout_seconds=VERIFY_TIMEOUT,
            final_model_hash=model_hash(candidate_tpn),
        )

    fresh_verdict = v.get("result")
    final_certs = v.get("certificates") or []
    rec["fresh_reverification_verdict"] = fresh_verdict
    rec["final_critical_pair_count"] = len(final_certs)
    rec["final_model_hash"] = model_hash(candidate_tpn)
    rec["task_predicate_pass"] = True  # legacy psi_task == 1

    try:
        obj = lexicographic_objective(candidate_tpn, final_certs, tpn, "O0")
        # O0 base tuple: (|A_LH|, total_overlap_width, C_I, m_I)
        rec["CI"] = frac_to_json(obj[2]) if len(obj) > 2 else NA
    except Exception:  # noqa: BLE001
        rec["CI"] = NA
    try:
        rec["modified_transition_count"] = sum(
            1 for n, t in candidate_tpn.transitions.items()
            if n in tpn.transitions and t.interval != tpn.transitions[n].interval
        )
    except Exception:  # noqa: BLE001
        rec["modified_transition_count"] = NA

    if fresh_verdict == "VER" and not final_certs and rec["task_predicate_pass"]:
        return finish("VERIFIED_SUCCESS")
    return finish("VALIDATION_FAILURE", error_type=f"REVERIFY_{fresh_verdict}")


if __name__ == "__main__":
    sys.exit(main())

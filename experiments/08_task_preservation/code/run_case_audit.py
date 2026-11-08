#!/usr/bin/env python3
"""Reconstruct one frozen adjustment case on a fresh platform and evaluate the
R3-2 task-preservation predicate.

argv: method evaluation_id params_json L H expected_json
expected_json: {"status","final_model_hash","modified_transition_count","CI"}
Prints one JSON record.  No original file is modified."""
import json, os, sys, time
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"code"/"frozen_src"))
sys.path.insert(0, str(ROOT/"code"))
from src.benchmarks.rmt_fms_generator import generate_rmt_fms
from src.verifier import verify
from src.repair.algorithm import repair, lexicographic_objective
from src.repair.exhaustive import exhaustive_repair
from src.repair.global_constraint_repair import global_constraint_repair
from src.repair.task_constraint import AlwaysTrueTaskConstraint
from src.exact_confirmation.lp_solver import compute_completion_time_interval
from predicate import select_reference, baseline_times, evaluate

NA = "NA"
def model_hash(tpn):
    import hashlib
    data = {"places": sorted(tpn.places.keys()),
            "transitions": sorted([{"name": n, "label": t.label, "fault": t.is_fault,
                "earliest": str(t.interval.earliest), "latest": str(t.interval.latest)}
                for n, t in tpn.transitions.items()], key=lambda x: x["name"]),
            "arcs": sorted(f"{a.from_node}->{a.to_node}" for a in tpn.arcs),
            "initial_marking": sorted(tpn.initial_marking.items()),
            "completion_markings": [sorted(m.items()) for m in tpn.completion_markings]}
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]

def frac(x):
    return NA if x is None else str(x)

def main():
    if len(sys.argv) < 7: print(json.dumps({"status":"BAD_ARGV"})); return 2
    method, eid, params_json, L, H, expected_json = sys.argv[1:7]
    params = json.loads(params_json); L = int(L); H = float(H)
    expected = json.loads(expected_json)
    out = {"evaluation_id": eid, "method": method, "expected_status": expected.get("status")}
    t0 = time.time()
    try:
        tpn, gl, gh = generate_rmt_fms(**params, repair_domain="extended")
        out.update({"L": gl, "H": gh,
                    "initial_model_hash": model_hash(tpn),
                    "n_adjustable": sum(1 for t in tpn.transitions.values() if t.is_adjustable)})
        v0 = verify(tpn, gl, gh, complete_set=True)
        out["initial_verdict"] = v0.get("result")
        out["initial_certs"] = len(v0.get("certificates") or [])
        certs = v0.get("certificates") or []
        ref = select_reference(eid, certs) if certs else None
        if ref:
            base = baseline_times(tpn, gh, ref, compute_completion_time_interval)
            out["reference"] = {"regime": ref["regime"], "n_normal": len(ref["normal"]),
                                "n_fault": len(ref["fault"]),
                                "n_normal_available": ref["n_normal_available"],
                                "n_fault_available": ref["n_fault_available"],
                                "baseline_undetermined": len(base["undetermined"])}
        candidate = None
        if method == "cpgld":
            res = repair(tpn, certs, gl, gh, verifier_fn=lambda t: verify(t, gl, gh, complete_set=True),
                         task_constraint=AlwaysTrueTaskConstraint(), objective_variant="O0")
            candidate = res.repaired_tpn
        elif method == "coquand":
            res = global_constraint_repair(tpn, certs, gh)
            candidate = res.get("modified_tpn")
        elif method == "exhaustive":
            res = exhaustive_repair(tpn, certs, gl, gh,
                verifier_fn=lambda t: verify(t, gl, gh, complete_set=True),
                task_constraint=AlwaysTrueTaskConstraint(), max_scope_combinations=200_000)
            candidate = res.repaired_tpn
        if candidate is None:
            out["reconstruction"] = {"candidate": False}
            out["status"] = "NO_CANDIDATE"; out["wall_s"] = round(time.time()-t0,2)
            print(json.dumps(out)); return 0
        h = model_hash(candidate)
        mc = sum(1 for n, t in candidate.transitions.items()
                 if n in tpn.transitions and t.interval != tpn.transitions[n].interval)
        vf = verify(candidate, gl, gh, complete_set=True)
        certs_final = vf.get("certificates") or []
        try:
            obj = lexicographic_objective(candidate, certs_final, tpn, "O0")
            ci = str(float(obj[2])) if len(obj) > 2 else NA
        except Exception:
            ci = NA
        out["reconstruction"] = {"candidate": True, "final_model_hash": h, "modified_transition_count": mc,
            "fresh_verdict": vf.get("result"), "fresh_certs": len(certs_final), "CI": ci,
            "hash_match": h == expected.get("final_model_hash"),
            "modified_match": str(mc) == str(expected.get("modified_transition_count")),
            "CI_match": (ci != NA and expected.get("CI") not in (None, "NA")
                         and abs(float(ci) - float(expected.get("CI"))) < 1e-6)}
        success = vf.get("result") == "VER" and not certs_final
        out["fresh_success"] = success
        if success and ref:
            ev = evaluate(candidate, gh, ref, base, compute_completion_time_interval)
            out["predicate"] = {"path_pass": ev["path_pass"], "lost_normal": len(ev["lost_normal"]),
                "lost_fault": len(ev["lost_fault"]), "undetermined": len(ev["undetermined"]),
                "perf_tiers": ev["perf_tiers"], "psi_pass": ev["psi_pass"],
                "normal_rows": ev["normal_rows"], "fault_rows": ev["fault_rows"]}
        out["status"] = "RECONSTRUCTED_SUCCESS" if success else "RECONSTRUCTED_OTHER"
    except Exception as exc:
        out["status"] = "ERROR"; out["error"] = f"{type(exc).__name__}: {exc}"[:300]
    out["wall_s"] = round(time.time()-t0, 2)
    print(json.dumps(out, default=str)); return 0

if __name__ == "__main__":
    sys.exit(main())

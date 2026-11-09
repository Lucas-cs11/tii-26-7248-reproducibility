#!/usr/bin/env python3
"""Reconstruct one frozen case with full interval/verification evidence."""
import csv, gzip, hashlib, json, os, sys
from pathlib import Path

EXP = Path(__file__).resolve().parents[3]
OUT = EXP / "results/writing_readiness_audit/REPRESENTATIVE_EXACT_CERTIFICATES"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(EXP / "code/frozen_src"))
sys.path.insert(0, str(EXP / "code"))
from src.benchmarks.rmt_fms_generator import generate_rmt_fms
from src.verifier import verify
from src.repair.algorithm import repair, lexicographic_objective
from src.repair.global_constraint_repair import global_constraint_repair
from src.repair.exhaustive import exhaustive_repair
from src.repair.task_constraint import AlwaysTrueTaskConstraint
from src.exact_confirmation.lp_solver import compute_completion_time_interval, _solve_lp
from predicate import select_reference, baseline_times, evaluate

PARAMS = ["n_machines","n_parts","ops_per_part","wip_bound","unobservable_ratio",
          "fault_locations","interval_width_factor","adjustable_ratio","seed"]
INT = {"n_machines","n_parts","ops_per_part","wip_bound","fault_locations","seed"}


def model_hash(tpn):
    data = {
        "places": sorted(tpn.places.keys()),
        "transitions": sorted([
            {"name": n, "label": t.label, "fault": t.is_fault,
             "earliest": str(t.interval.earliest), "latest": str(t.interval.latest)}
            for n, t in tpn.transitions.items()], key=lambda x: x["name"]),
        "arcs": sorted(f"{a.from_node}->{a.to_node}" for a in tpn.arcs),
        "initial_marking": sorted(tpn.initial_marking.items()),
        "completion_markings": [sorted(m.items()) for m in tpn.completion_markings],
    }
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]


def model_definition(tpn):
    return {
        "places": sorted(tpn.places.keys()),
        "transitions": {name: {"label": t.label, "is_fault": t.is_fault,
            "is_adjustable": t.is_adjustable,
            "interval": [str(t.interval.earliest), str(t.interval.latest)]}
            for name, t in sorted(tpn.transitions.items())},
        "arcs": sorted([a.from_node, a.to_node] for a in tpn.arcs),
        "initial_marking": dict(sorted(tpn.initial_marking.items())),
        "completion_markings": [dict(sorted(m.items())) for m in tpn.completion_markings],
    }


def interval_map(tpn):
    return {name: {"earliest": str(t.interval.earliest), "latest": str(t.interval.latest),
                   "is_fault": t.is_fault, "is_adjustable": t.is_adjustable}
            for name, t in tpn.transitions.items()}


def main(eid, method, label=None):
    with gzip.open(EXP / "data/frozen/full_amb_population.csv.gz", "rt") as handle:
        for row in csv.DictReader(handle):
            if row["evaluation_id"] == eid:
                break
        else:
            raise SystemExit(f"unknown evaluation {eid}")
    params = {k: (int(row[k]) if k in INT else float(row[k])) for k in PARAMS}
    L, H = int(row["L"]), float(row["H"])
    with gzip.open(EXP / f"data/frozen/full_adjustment_{method}.csv.gz", "rt") as handle:
        for rec in csv.DictReader(handle):
            if rec["evaluation_id"] == eid:
                break
    tpn, genL, genH = generate_rmt_fms(**params, repair_domain="extended")
    if genL != L or abs(genH - H) > 1e-9:
        raise SystemExit(f"LH mismatch {genL}/{genH} vs {L}/{H}")
    initial_verify = verify(tpn, genL, genH, complete_set=True)
    certs = initial_verify.get("certificates") or []
    reference = select_reference(eid, certs)
    baseline = baseline_times(tpn, genH, reference, compute_completion_time_interval)
    if method == "cpgld":
        res = repair(tpn, certs, genL, genH,
                     verifier_fn=lambda t: verify(t, genL, genH, complete_set=True),
                     task_constraint=AlwaysTrueTaskConstraint(), objective_variant="O0")
        candidate = res.repaired_tpn
    elif method == "coquand":
        res = global_constraint_repair(tpn, certs, genH)
        candidate = res["modified_tpn"]
    else:
        res = exhaustive_repair(tpn, certs, genL, genH,
                    verifier_fn=lambda t: verify(t, genL, genH, complete_set=True),
                    task_constraint=AlwaysTrueTaskConstraint(), max_scope_combinations=200_000)
        candidate = res.repaired_tpn
    if candidate is None:
        raise SystemExit("no candidate")
    fresh = verify(candidate, genL, genH, complete_set=True)
    pred = evaluate(candidate, genH, reference, baseline, compute_completion_time_interval)
    changes = {}
    for name, t in candidate.transitions.items():
        old = tpn.transitions[name].interval
        if old != t.interval:
            changes[name] = {
                "before": [str(old.earliest), str(old.latest)],
                "after": [str(t.interval.earliest), str(t.interval.latest)],
                "is_fault": t.is_fault,
            }
    numeric = {}
    for cls, rows in (("normal", pred["normal_rows"]), ("fault", pred["fault_rows"])):
        for row in rows:
            if row["status"] == "LOST":
                word = tuple(row["word"])
                min_res = _solve_lp(candidate, word, genH, minimize=True)
                max_res = _solve_lp(candidate, word, genH, minimize=False)
                numeric[f"{cls}:{','.join(word)}"] = {
                    "min_status": min_res.status.value, "max_status": max_res.status.value,
                    "min_value": min_res.value, "max_value": max_res.value,
                }
    payload = {
        "evaluation_id": eid, "method": method,
        "original_parameters": params, "L": genL, "H": genH,
        "initial_model_hash": model_hash(tpn),
        "original_model": model_definition(tpn),
        "candidate_model": model_definition(candidate) if 'candidate' in locals() and candidate is not None else None,
        "initial_verdict": initial_verify.get("result"),
        "initial_certificates": len(certs),
        "reference": {
            "regime": reference["regime"],
            "normal_words": [list(w) for w in reference["normal"]],
            "fault_words": [list(w) for w in reference["fault"]],
            "normal_available": reference["n_normal_available"],
            "fault_available": reference["n_fault_available"],
        },
        "original_frozen_record": rec,
        "reconstruction": {
            "candidate_model_hash": model_hash(candidate),
            "fresh_verdict": fresh.get("result"),
            "fresh_certificates": len(fresh.get("certificates") or []),
            "fresh_certificate_mode": fresh.get("certificate_mode"),
            "fresh_enumeration_complete": fresh.get("enumeration_complete"),
            "interval_changes": changes,
            "CI": str(lexicographic_objective(candidate, fresh.get("certificates") or [], tpn, "O0")[2]),
            "modified_transition_count": len(changes),
            "expected_final_model_hash": rec["final_model_hash"],
            "hash_match": model_hash(candidate) == rec["final_model_hash"],
        },
        "predicate": pred,
        "baseline_completion_intervals": {
            "normal": [[list(w), [str(iv[0]), str(iv[1])]] for w, iv in baseline["normal"].items()],
            "fault": [[list(w), [str(iv[0]), str(iv[1])]] for w, iv in baseline["fault"].items()],
            "undetermined": baseline["undetermined"],
        },
        "numeric_status_for_lost_words": numeric,
        "provenance": {
            "source": "experiments/08_task_preservation/code/frozen_src (read-only)",
            "runner": "results/writing_readiness_audit/scripts/reconstruct_case.py",
            "solver": "scipy.optimize.linprog (HiGHS) floating-point LP; Fraction display only",
        },
    }
    target = OUT / (label or eid)
    target.mkdir(exist_ok=True)
    (target / "certificate.json").write_text(json.dumps(payload, indent=2, default=str) + "\n")
    print(json.dumps({
        "case": eid, "method": method,
        "candidate_hash": payload["reconstruction"]["candidate_model_hash"],
        "expected_hash": rec["final_model_hash"],
        "hash_match": payload["reconstruction"]["hash_match"],
        "fresh_verdict": fresh.get("result"),
        "fresh_certificates": payload["reconstruction"]["fresh_certificates"],
        "changes": len(changes),
        "path_pass": pred["path_pass"],
        "psi_pass": pred["psi_pass"],
        "lost_word_numeric_status": numeric,
        "certificate": str(target / "certificate.json"),
    }, indent=2, default=str))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)

#!/usr/bin/env python3
"""Unit tests for the R3-2 task-preservation predicate (frozen code, real models)."""
import csv, gzip, json, sys, traceback
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADJ = ROOT
sys.path.insert(0, str(ROOT/"code"/"frozen_src"))
sys.path.insert(0, str(ROOT/"code"))
from src.benchmarks.rmt_fms_generator import generate_rmt_fms
from src.verifier import verify
from src.exact_confirmation.lp_solver import compute_completion_time_interval
from src.model.tpn import Interval
from predicate import select_reference, baseline_times, evaluate

PARAMS = ["n_machines","n_parts","ops_per_part","wip_bound","unobservable_ratio",
          "fault_locations","interval_width_factor","adjustable_ratio","seed"]
INT = {"n_machines","n_parts","ops_per_part","wip_bound","fault_locations","seed"}

def row_params(row):
    return {k:(int(row[k]) if k in INT else float(row[k])) for k in PARAMS}

def load_pop(n=6):
    with gzip.open(ROOT/"data/frozen/full_amb_population.csv.gz","rt") as f:
        rows = [r for r in csv.DictReader(f) if r["n_machines"]=="2" and r["n_parts"]=="1" and r["ops_per_part"]=="2"]
    rows.sort(key=lambda r:(float(r["interval_width_factor"]), float(r["adjustable_ratio"]), r["seed"]))
    return rows[:n]

def main():
    tests = {}
    rows = load_pop(6)
    cases = []
    for row in rows:
        tpn, L, H = generate_rmt_fms(**row_params(row), repair_domain="extended")
        v = verify(tpn, L, H, complete_set=True)
        if v.get("result") != "AMB" or not v.get("certificates"):
            continue
        certs = v["certificates"]
        ref = select_reference(row["evaluation_id"], certs)
        base = baseline_times(tpn, H, ref, compute_completion_time_interval)
        cand = evaluate(tpn, H, ref, base, compute_completion_time_interval)
        case = {"evaluation_id": row["evaluation_id"], "L": L, "H": H, "certs": len(certs),
                "regime": ref["regime"], "n_normal": len(ref["normal"]), "n_fault": len(ref["fault"]),
                "self_path_pass": cand["path_pass"], "self_tiers": cand["perf_tiers"],
                "self_psi": cand["psi_pass"], "baseline_undetermined": len(base["undetermined"])}
        # lost normal: move one transition of a selected normal word beyond H
        if ref["normal"] and base["normal"]:
            word = ref["normal"][0]; t_name = word[0]
            try:
                moved = tpn.copy_with_interval(t_name, Interval(Fraction(H)+1, Fraction(H)+2))
                iv = compute_completion_time_interval(moved, word, H)
                case["lost_normal_test"] = {"word": list(word), "transition": t_name,
                    "feasible_after_move": iv is not None, "as_expected": iv is None}
            except Exception as e:
                case["lost_normal_test"] = {"error": f"{type(e).__name__}: {e}"}
        # lost fault
        if ref["fault"]:
            word = ref["fault"][0]; t_name = word[0]
            try:
                moved = tpn.copy_with_interval(t_name, Interval(Fraction(H)+1, Fraction(H)+2))
                iv = compute_completion_time_interval(moved, word, H)
                case["lost_fault_test"] = {"word": list(word), "transition": t_name,
                    "feasible_after_move": iv is not None, "as_expected": iv is None}
            except Exception as e:
                case["lost_fault_test"] = {"error": f"{type(e).__name__}: {e}"}
        cases.append(case)
    # tolerance math test with synthetic oracle
    class Fake:
        def __init__(self, tmap): self.tmap = tmap
    ref = {"normal":[("a",)], "fault":[("b",)], "regime":"full", "K":3,
           "n_normal_available":1, "n_fault_available":1}
    base = {"normal":{("a",):(Fraction(10),Fraction(10))}, "fault":{("b",):(Fraction(5),Fraction(5))}, "undetermined":[]}
    def oracle_delta(delta):
        def f(model, word, H):
            if word == ("a",): return (Fraction(10)+delta, Fraction(10)+delta)
            if word == ("b",): return (Fraction(5), Fraction(5))
        return f
    e0 = evaluate(None, 100, ref, base, oracle_delta(Fraction(0)))
    e5 = evaluate(None, 100, ref, base, oracle_delta(Fraction(1,2)))   # exactly 5%
    e6 = evaluate(None, 100, ref, base, oracle_delta(Fraction(6,10)))  # 6% -> fail 0/5, pass 10
    tests["tolerance"] = {"delta0": e0["psi_pass"], "delta5pct": e5["psi_pass"], "delta6pct": e6["psi_pass"]}
    out = {"cases": cases, "tolerance": tests["tolerance"]}
    checks = {
      "all_self_path_pass": all(c["self_path_pass"] and all(c["self_tiers"].values()) and all(c["self_psi"].values()) for c in cases),
      "lost_normal_expected": all(c.get("lost_normal_test",{}).get("as_expected") for c in cases if "lost_normal_test" in c),
      "lost_fault_expected": all(c.get("lost_fault_test",{}).get("as_expected") for c in cases if "lost_fault_test" in c),
      "tolerance_delta0_pass": tests["tolerance"]["delta0"]=={"0":True,"5":True,"10":True},
      "tolerance_delta5_pass": tests["tolerance"]["delta5pct"]=={"0":False,"5":True,"10":True},
      "tolerance_delta6_match": tests["tolerance"]["delta6pct"]=={"0":False,"5":False,"10":True},
    }
    out["checks"] = checks
    out["PASS"] = all(checks.values()) and len(cases) >= 3
    print(json.dumps(out, indent=2))
    return 0 if out["PASS"] else 1

if __name__ == "__main__":
    sys.exit(main())

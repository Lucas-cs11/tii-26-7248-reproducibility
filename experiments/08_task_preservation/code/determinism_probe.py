#!/usr/bin/env python3
"""Probe: can the adjusted model be deterministically reconstructed by rerunning
the frozen per-case runner?  Compares recorded status / final_model_hash / CI /
modified-transition count with a fresh rerun."""
import csv, gzip, json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADJ = ROOT
PY = sys.executable
RUN = str(ROOT/"code/run_case_audit.py")
POP = ROOT/"data/frozen/full_amb_population.csv.gz"
PARAMS = ["n_machines","n_parts","ops_per_part","wip_bound","unobservable_ratio","fault_locations","interval_width_factor","adjustable_ratio","seed"]
INT = {"n_machines","n_parts","ops_per_part","wip_bound","fault_locations","seed"}

def load(p):
    with gzip.open(p,'rt',newline='') as f: return list(csv.DictReader(f))

def params_of(row):
    return {k:(int(row[k]) if k in INT else float(row[k])) for k in PARAMS}

def main(sample_per_method=4):
    pop = {r["evaluation_id"]: r for r in load(POP)}
    out = {"methods": {}, "cases": []}
    for method in ("cpgld","coquand","exhaustive"):
        rows = load(ROOT/f"data/frozen/full_adjustment_{method}.csv.gz")
        succ = [r for r in rows if r["status"]=="VERIFIED_SUCCESS"]
        succ.sort(key=lambda r:(float(r["runtime_seconds"]), int(r["n_machines"]), r["evaluation_id"]))
        picks = succ[::max(1,len(succ)//sample_per_method)][:sample_per_method]
        method_cases = []
        for rec in picks:
            row = pop[rec["evaluation_id"]]
            cmd = [PY, RUN, method, rec["evaluation_id"], json.dumps(params_of(row)), str(row["L"]), str(row["H"])]
            t0=time.perf_counter()
            try:
                p = subprocess.run(cmd, capture_output=True, text=True, timeout=900,
                                   env={**__import__("os").environ, "PYTHONHASHSEED":"0",
                                        "OPENBLAS_NUM_THREADS":"1","OMP_NUM_THREADS":"1",
                                        "MKL_NUM_THREADS":"1","VECLIB_MAXIMUM_THREADS":"1","NUMEXPR_NUM_THREADS":"1"})
                fresh = json.loads(p.stdout.strip().splitlines()[-1]) if p.stdout.strip() else {}
            except Exception as e:
                fresh = {"status":"PROBE_ERROR","error":str(e)[:200]}
            wall = round(time.perf_counter()-t0,2)
            checks = {
              "status": fresh.get("status")==rec["status"],
              "final_model_hash": (fresh.get("final_model_hash") or "").strip()==rec["final_model_hash"],
              "modified_transition_count": str(fresh.get("modified_transition_count"))==str(rec["modified_transition_count"]),
              "CI": (str(fresh.get("CI"))[:10]==str(rec["CI"])[:10]) if fresh.get("CI") not in (None,"NA") else False,
            }
            case = {"method":method,"evaluation_id":rec["evaluation_id"],"recorded_status":rec["status"],
                    "fresh_status":fresh.get("status"),"checks":checks,"fresh_hash":fresh.get("final_model_hash"),
                    "recorded_hash":rec["final_model_hash"],"wall_s":wall}
            method_cases.append(case); out["cases"].append(case)
        out["methods"][method] = {
            "sampled":len(method_cases),
            "status_match":sum(c["checks"]["status"] for c in method_cases),
            "hash_match":sum(c["checks"]["final_model_hash"] for c in method_cases),
            "all_checks_match":sum(all(c["checks"].values()) for c in method_cases),
        }
    out["deterministic"] = all(v["all_checks_match"]==v["sampled"] for v in out["methods"].values())
    print(json.dumps(out, indent=2))
    return 0 if out["deterministic"] else 1

if __name__=="__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv)>1 else 4))

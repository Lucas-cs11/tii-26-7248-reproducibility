#!/usr/bin/env python3
"""Cross-platform compatibility probe: reconstruct a few frozen successes per
method on the current platform and compare status/hash/modified count/CI with the
frozen records."""
import csv, gzip, json, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/"data"/"frozen"; PY = sys.executable; RUN = ROOT/"code"/"run_case_audit.py"
PARAMS = ["n_machines","n_parts","ops_per_part","wip_bound","unobservable_ratio",
          "fault_locations","interval_width_factor","adjustable_ratio","seed"]
INT = {"n_machines","n_parts","ops_per_part","wip_bound","fault_locations","seed"}
def load(p):
    with gzip.open(p,"rt") as f: return list(csv.DictReader(f))
def main(n=3):
    pop = {r["evaluation_id"]: r for r in load(DATA/"full_amb_population.csv.gz")}
    cases=[]; summary={}
    for method in ("cpgld","coquand","exhaustive"):
        rows=[r for r in load(DATA/f"full_adjustment_{method}.csv.gz") if r["status"]=="VERIFIED_SUCCESS"]
        rows.sort(key=lambda r:(float(r["runtime_seconds"]), r["evaluation_id"]))
        picks=rows[::max(1,len(rows)//n)][:n]
        ok=0; details=[]
        for rec in picks:
            row=pop[rec["evaluation_id"]]
            params={k:(int(row[k]) if k in INT else float(row[k])) for k in PARAMS}
            exp={k:rec[k] for k in ("status","final_model_hash","modified_transition_count","CI")}
            p=subprocess.run([PY,str(RUN),method,rec["evaluation_id"],json.dumps(params),
                              str(row["L"]),str(row["H"]),json.dumps(exp)],
                             capture_output=True,text=True,timeout=2400)
            out=json.loads(p.stdout.strip().splitlines()[-1]) if p.stdout.strip() else {}
            r=out.get("reconstruction",{})
            match=bool(r.get("candidate") and r.get("hash_match") and r.get("modified_match") and r.get("CI_match"))
            ok+=match; details.append({"evaluation_id":rec["evaluation_id"],"match":match,
                "fresh_status":r.get("fresh_verdict"),"hash_match":r.get("hash_match"),
                "modified_match":r.get("modified_match"),"CI_match":r.get("CI_match")})
        summary[method]={"sampled":len(picks),"exact_matches":ok,"details":details}
        cases.extend(details)
    result={"platform":sys.platform,"python":sys.version.split()[0],"PASS":all(v["exact_matches"]==v["sampled"] for v in summary.values()),
            "methods":summary}
    print(json.dumps(result,indent=2))
    return 0 if result["PASS"] else 1
if __name__=="__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv)>1 else 3))

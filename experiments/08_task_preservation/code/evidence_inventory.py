#!/usr/bin/env python3
"""Read-only verification of the frozen adjustment evidence."""
import csv, gzip, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADJ = ROOT
POP = ROOT/"data/frozen/full_amb_population.csv.gz"
POP_META = json.loads((Path(str(ROOT/"data/frozen/full_amb_population.csv.gz"))).read_text())
VAL = json.loads((ADJ/"validation/full_adjustment_validation.json").read_text())
PARAM_FIELDS = ["n_machines","n_parts","ops_per_part","wip_bound","unobservable_ratio","fault_locations","interval_width_factor","adjustable_ratio","seed"]

def sha256(p):
    h = hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda: f.read(1<<20), b''): h.update(c)
    return h.hexdigest()

def load_csvgz(p):
    with gzip.open(p,'rt', newline='') as f:
        return list(csv.DictReader(f))

def main():
    out = {"population": {}, "methods": {}, "checks": []}
    rows = load_csvgz(POP)
    ids = [r["evaluation_id"] for r in rows]
    out["population"] = {
        "path": str(POP), "rows": len(rows), "unique_ids": len(set(ids)),
        "sha256": sha256(POP), "sha256_matches_meta": sha256(POP)==POP_META["population_sha256"],
        "frozen_at": POP_META.get("frozen_at"), "no_dedup": POP_META.get("no_dedup")}
    out["checks"].append(("population_rows_16038", len(rows)==16038))
    out["checks"].append(("population_unique", len(set(ids))==16038))
    out["checks"].append(("population_sha_matches_meta", out["population"]["sha256_matches_meta"]))
    all_ids=set(ids)
    expected={"cpgld":14830,"coquand":9097,"exhaustive":2005}
    for m in ("cpgld","coquand","exhaustive"):
        r = load_csvgz(ROOT/f"data/frozen/full_adjustment_{m}.csv.gz")
        st = {}
        succ=set()
        for x in r:
            st[x["status"]] = st.get(x["status"],0)+1
            if x["status"]=="VERIFIED_SUCCESS": succ.add(x["evaluation_id"])
        v = VAL["methods"].get(m, {})
        out["methods"][m] = {"records": len(r), "unique_ids": len({x['evaluation_id'] for x in r}),
            "status_counts": st, "success": len(succ),
            "expected_success": expected[m], "success_matches_validation": len(succ)==v.get("success_count"),
            "all_ids_in_population": succ <= all_ids,
            "validation_status_counts_match": st==v.get("status_counts"),
            "has_final_model_hash": all('final_model_hash' in x and x['final_model_hash'] not in ('','NA') for x in r if x['status']=='VERIFIED_SUCCESS')}
        out["checks"].append((f"{m}_success_count", len(succ)==expected[m]))
        out["checks"].append((f"{m}_status_counts_match_validation", st==v.get("status_counts")))
    out["validation_generated_at"] = VAL.get("generated_at")
    out["PASS"] = all(ok for _,ok in out["checks"])
    print(json.dumps(out, indent=2))
    return 0 if out["PASS"] else 1

if __name__=="__main__":
    sys.exit(main())

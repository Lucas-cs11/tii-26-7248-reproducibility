#!/usr/bin/env python3
"""Aggregate pilot shard outputs and audit them (missing/duplicate/hash/predicate
consistency)."""
import argparse, glob, json, sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--dir",type=Path,default=ROOT/"results"/"pilot")
    ap.add_argument("--manifest",type=Path,default=ROOT/"protocol"/"pilot_manifest.json")
    a=ap.parse_args(); man=json.loads(a.manifest.read_text())
    records=[]; bad=[]
    for f in sorted(a.dir.glob("shard_*.jsonl")):
        for line in f.read_text().splitlines():
            line=line.strip()
            if not line: continue
            try: records.append(json.loads(line))
            except json.JSONDecodeError: bad.append(str(f))
    expected={(c["evaluation_id"],m) for c in man["cells"] for m in man["methods"]}
    got=[(r["evaluation_id"],r["method"]) for r in records]
    counts=Counter(got); dup=[k for k,v in counts.items() if v>1]
    missing=sorted(expected-set(got)); extra=sorted(set(got)-expected)
    recon_mismatch=[r for r in records if r.get("reconstruction",{}).get("candidate") and not all(
        r["reconstruction"].get(k) for k in ("hash_match","modified_match","CI_match"))]
    predicate=Counter(); psi=Counter()
    for r in records:
        rec=r.get("reconstruction",{}); pr=r.get("predicate")
        if not rec.get("candidate"): predicate["no_candidate"]+=1; continue
        if not r.get("fresh_success"): predicate["not_fresh_success"]+=1; continue
        if not pr: predicate["no_predicate"]+=1; continue
        ps=pr.get("psi_pass",{})
        for t in ("0","5","10"): psi[t]+=1 if ps.get(t) else 0
        predicate["path_pass" if pr.get("path_pass") else "path_fail"]+=1
    out={"records":len(records),"bad_files":bad,"expected_cases":len(expected),
         "unique_cases":len(counts),"duplicates":dup,"missing":len(missing),"extra":len(extra),
         "reconstruction_mismatch":len(recon_mismatch),
         "predicate_counts":dict(predicate),"psi_pass_counts":dict(psi),
         "status_counts":dict(Counter(r.get("status") for r in records)),
         "PASS":not bad and not dup and not missing and not extra and not recon_mismatch}
    print(json.dumps(out,indent=2)); return 0 if out["PASS"] else 1
if __name__=="__main__": sys.exit(main())

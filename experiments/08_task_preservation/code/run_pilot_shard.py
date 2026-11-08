#!/usr/bin/env python3
"""Run one shard of the R3-2 Phase-A pilot: for each sampled evaluation and each
of the three methods, invoke run_case_audit.py as a subprocess with hard timeout,
write raw JSONL + per-shard metrics."""
import argparse, json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
RUN = ROOT/"code"/"run_case_audit.py"
MANIFEST = ROOT/"protocol"/"pilot_manifest.json"
PARAMS = ["n_machines","n_parts","ops_per_part","wip_bound","unobservable_ratio",
          "fault_locations","interval_width_factor","adjustable_ratio","seed"]
INT = {"n_machines","n_parts","ops_per_part","wip_bound","fault_locations","seed"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", type=int, required=True)
    ap.add_argument("--shards", type=int, required=True)
    ap.add_argument("--out", type=Path, default=ROOT/"results"/"pilot")
    ap.add_argument("--verify-timeout", type=float, default=120)
    ap.add_argument("--repair-timeout", type=float, default=300)
    args = ap.parse_args()
    man = json.loads(MANIFEST.read_text())
    tasks = man["cells"][args.shard::args.shards]
    out = args.out; out.mkdir(parents=True, exist_ok=True)
    raw = out/f"shard_{args.shard:03d}.jsonl"
    metrics = {"shard": args.shard, "shards": args.shards, "cells": len(tasks), "cases": 0,
               "status_counts": {}, "reconstruction_mismatch": 0, "wall_s": 0.0}
    t0 = time.time()
    with raw.open("w") as fh:
        for cell in tasks:
            params = {k:(int(cell[k]) if k in INT else float(cell[k])) for k in PARAMS}
            for method in ("cpgld","coquand","exhaustive"):
                exp = cell["expected"][method]
                cmd = [PY, str(RUN), method, cell["evaluation_id"], json.dumps(params),
                       str(cell["L"]), str(cell["H"]), json.dumps(exp)]
                try:
                    p = subprocess.run(cmd, capture_output=True, text=True,
                        timeout=args.verify_timeout*2 + args.repair_timeout + 300,
                        env={**os.environ, "PYTHONHASHSEED":"0",
                             "OPENBLAS_NUM_THREADS":"1","OMP_NUM_THREADS":"1",
                             "MKL_NUM_THREADS":"1","VECLIB_MAXIMUM_THREADS":"1","NUMEXPR_NUM_THREADS":"1"})
                    line = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else "{}"
                    rec = json.loads(line)
                except Exception as exc:
                    rec = {"evaluation_id": cell["evaluation_id"], "method": method,
                           "status": "INFRA_TIMEOUT_OR_ERROR", "error": f"{type(exc).__name__}: {exc}"[:200]}
                fh.write(json.dumps(rec, default=str) + "\n")
                metrics["cases"] += 1
                metrics["status_counts"][rec.get("status","?")] = metrics["status_counts"].get(rec.get("status","?"),0)+1
                if rec.get("reconstruction",{}).get("candidate") and not all(
                        rec["reconstruction"].get(k) for k in ("hash_match","modified_match","CI_match")):
                    metrics["reconstruction_mismatch"] += 1
    metrics["wall_s"] = round(time.time()-t0,2)
    (out/f"shard_{args.shard:03d}_metrics.json").write_text(json.dumps(metrics, indent=2)+"\n")
    print(json.dumps(metrics)); return 0

if __name__ == "__main__":
    sys.exit(main())

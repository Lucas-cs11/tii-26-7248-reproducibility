#!/usr/bin/env python3
"""Build the frozen 10% stratified Phase-A pilot manifest (evaluation-ID sampling,
paired across the three methods)."""
import csv, gzip, hashlib, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/"data"/"frozen"
PARAMS = ["n_machines","n_parts","ops_per_part","wip_bound","unobservable_ratio",
          "fault_locations","interval_width_factor","adjustable_ratio","seed"]
FRACTION = 0.10

def load(p):
    with gzip.open(p,"rt") as f: return list(csv.DictReader(f))

def main():
    pop = load(DATA/"full_amb_population.csv.gz")
    res = {}
    for m in ("cpgld","coquand","exhaustive"):
        res[m] = {r["evaluation_id"]: r for r in load(DATA/f"full_adjustment_{m}.csv.gz")}
    strata = {}
    for row in pop:
        eid = row["evaluation_id"]
        key = (row["n_machines"], row["n_parts"], row["ops_per_part"], row["wip_bound"],
               f"{float(row['unobservable_ratio']):.2f}", f"{float(row['adjustable_ratio']):.2f}",
               f"{float(row['interval_width_factor']):.2f}",
               res["cpgld"][eid]["status"], res["coquand"][eid]["status"],
               res["exhaustive"][eid]["status"])
        strata.setdefault(key, []).append(row)
    selected = []
    for key, rows in strata.items():
        rows.sort(key=lambda r: hashlib.sha256(("pilot|"+r["evaluation_id"]).encode()).hexdigest())
        take = max(1, math.ceil(len(rows)*FRACTION))
        selected.extend(rows[:take])
    selected.sort(key=lambda r: r["evaluation_id"])
    cells = []
    for row in selected:
        eid = row["evaluation_id"]
        cell = {k: row[k] for k in PARAMS}
        cell.update({"evaluation_id": eid, "L": int(row["L"]), "H": float(row["H"]),
                     "stratum": [row["n_machines"], row["n_parts"], row["ops_per_part"],
                                 row["wip_bound"], row["unobservable_ratio"],
                                 row["adjustable_ratio"], row["interval_width_factor"]],
                     "expected": {m: {k: res[m][eid].get(k) for k in
                        ("status","final_model_hash","modified_transition_count","CI")}
                        for m in res}})
        cells.append(cell)
    manifest = {"schema": "r3-2-phaseA-pilot-manifest-1", "sampling": "stratified 10% by evaluation id",
        "fraction": FRACTION, "population": len(pop), "strata": len(strata),
        "cell_count": len(cells), "cells": cells,
        "methods": ["cpgld","coquand","exhaustive"], "hash_selection": "sha256('pilot|'+evaluation_id)",
        "predicate": {"K": 3, "full_threshold": 32, "tolerance_tiers_percent": [0,5,10],
                      "tolerance_basis": "earliest completion time of each selected normal certificate word on N0"},
        "inputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(DATA.glob("*.gz"))}}
    out = ROOT/"protocol"/"pilot_manifest.json"
    out.write_text(json.dumps(manifest, indent=2)+"\n")
    body = out.read_bytes()
    (ROOT/"protocol"/"pilot_manifest.sha256").write_text(hashlib.sha256(body).hexdigest()+"\n")
    print(json.dumps({"cells": len(cells), "strata": len(strata), "selected_fraction": len(cells)/len(pop),
                      "sha256": hashlib.sha256(body).hexdigest()}))
    return 0

if __name__ == "__main__":
    sys.exit(main())

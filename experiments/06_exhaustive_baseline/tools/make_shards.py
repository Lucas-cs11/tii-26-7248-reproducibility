#!/usr/bin/env python3
"""Split the frozen AMB population into deterministic shards for GitHub Actions.

Usage:
    python tools/make_shards.py --n 40         # full-run shards
    python tools/make_shards.py --calib 40     # calibration sample
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POP = os.path.join(ROOT, "population/full_amb_population.csv.gz")
OUT = os.path.join(ROOT, "shards")


def load_population():
    with gzip.open(POP, "rt", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40, help="number of full-run shards")
    ap.add_argument("--calib", type=int, default=0, help="emit a calibration sample of this size")
    ap.add_argument("--seed", type=int, default=20261102)
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    rows = load_population()
    print(f"population: {len(rows)}")

    if args.calib:
        rng = random.Random(args.seed)
        sample = rng.sample(rows, min(args.calib, len(rows)))
        path = os.path.join(OUT, "calib.json")
        with open(path, "w") as f:
            json.dump(sample, f)
        print(f"calibration sample: {len(sample)} -> {path}")
        return 0

    n = args.n
    shards = [[] for _ in range(n)]
    for i, r in enumerate(rows):
        shards[i % n].append(r)
    index = []
    for k, shard in enumerate(shards):
        name = f"shard_{k:03d}.json"
        with open(os.path.join(OUT, name), "w") as f:
            json.dump(shard, f)
        index.append({"shard": k, "file": f"shards/{name}", "n": len(shard),
                      "ids": [r["evaluation_id"] for r in shard]})
        print(f"  {name}: {len(shard)} cases")
    with open(os.path.join(OUT, "index.json"), "w") as f:
        json.dump({"n_shards": n, "total": len(rows), "shards": index}, f, indent=1)
    print(f"wrote {n} shards + index.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

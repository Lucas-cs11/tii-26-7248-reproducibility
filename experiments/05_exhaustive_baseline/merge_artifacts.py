#!/usr/bin/env python3
"""Merge GitHub Actions shard artifacts into a single checkpoint JSONL.

Usage (local machine):
    python tools/merge_artifacts.py --artifacts ./gh_artifacts \
        --out /Users/lucas/tii_tpn_full_adjustment/checkpoints/exhaustive.jsonl

Layout expected: <artifacts>/<anything>/checkpoints/exhaustive.jsonl (one per shard).
Deduplicates by evaluation_id, keeps the first occurrence, and reports counts.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
from collections import Counter


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifacts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--append", action="store_true", help="append to existing out instead of rewriting")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.artifacts, "**", "exhaustive.jsonl"), recursive=True))
    print(f"artifact files: {len(files)}")

    existing = {}
    if args.append and os.path.exists(args.out):
        with open(args.out, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                existing[r["evaluation_id"]] = r
        print(f"existing records: {len(existing)}")

    merged = dict(existing)
    parsed = bad = dup = 0
    for path in files:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    bad += 1
                    continue
                parsed += 1
                eid = r.get("evaluation_id")
                if eid in merged:
                    dup += 1
                    continue
                merged[eid] = r

    status = Counter(r.get("status") for r in merged.values())
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    tmp = args.out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for eid in sorted(merged):
            f.write(json.dumps(merged[eid], ensure_ascii=False) + "\n")
    os.replace(tmp, args.out)

    print(f"parsed={parsed} parse_errors={bad} duplicates_skipped={dup}")
    print(f"out={args.out} records={len(merged)}")
    print("status:", dict(status))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

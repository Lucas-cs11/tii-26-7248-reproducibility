import csv, gzip, hashlib, json, sys
from pathlib import Path
shard = int(sys.argv[1])
plain = Path(f"results/complete_fullcov_{shard:03d}.csv")
gz = Path(f"results/complete_fullcov_{shard:03d}.csv.gz")
mf = Path(f"results/shard_manifest_{shard:03d}.json")
meta = json.loads(mf.read_text())
rows = []
if plain.exists():
    rows = list(csv.DictReader(plain.open(newline="")))
    with gzip.open(gz, "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    plain.unlink()
if gz.exists():
    meta["output_sha256"] = hashlib.sha256(gz.read_bytes()).hexdigest()
    meta["output_bytes"] = gz.stat().st_size
meta["actual_records"] = len(rows)
meta["timeout_records"] = sum(1 for r in rows if r.get("execution_status") == "TIMEOUT")
meta["completed_records"] = sum(1 for r in rows if r.get("execution_status") == "COMPLETED")
keys = [(r.get("model_id"), r.get("relative_H_level")) for r in rows]
meta["duplicate_combinations"] = len(keys) - len(set(keys))
meta["status"] = "ok" if rows else "EMPTY"
mf.write_text(json.dumps(meta, indent=1))
print("finalized", shard, len(rows))

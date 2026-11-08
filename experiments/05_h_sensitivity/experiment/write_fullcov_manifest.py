import hashlib, json, os, platform, sys
from pathlib import Path
shard = sys.argv[1]
coh = Path(f"cohorts/complete/remaining/shards/shard_{int(shard):03d}.csv")
out = Path(f"results/complete_fullcov_{int(shard):03d}.csv.gz")
meta = {
  "experiment": "baseline_H_complete_analysis_full_coverage",
  "shard_id": f"fullcov_shard_{int(shard):03d}",
  "workflow_run_id": os.environ.get("GITHUB_RUN_ID", ""),
  "job_id": os.environ.get("GITHUB_JOB", ""),
  "source_sha": os.environ.get("GITHUB_SHA", ""),
  "cohort_sha": hashlib.sha256(coh.read_bytes()).hexdigest(),
  "python": platform.python_version(),
  "runner_image": platform.platform(),
  "workers": 4,
  "h_ratios": [0.8, 1.0, 1.2, 1.5, 2.0],
  "analysis_mode": "COMPLETE_SET",
  "timeout_s": 180,
  "H_axis": "H = H_base * H_ratio",
  "models": len(list(__import__("csv").DictReader(coh.open()))),
  "expected_combinations": 5 * len(list(__import__("csv").DictReader(coh.open()))),
}
Path("results").mkdir(exist_ok=True)
Path(f"results/shard_manifest_{int(shard):03d}.json").write_text(json.dumps(meta, indent=1))
print("manifest", shard)

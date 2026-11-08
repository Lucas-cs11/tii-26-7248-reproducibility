import hashlib, json, os, platform, sys
from pathlib import Path
shard = sys.argv[1]
coh = Path("cohorts/complete/baselineH_shards/shard_%03d.csv" % int(shard))
meta = {
  "experiment": "baseline_H_complete_analysis",
  "shard_id": "baselineH_shard_%03d" % int(shard),
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
}
Path("results/shard_manifest_%s.json" % shard).write_text(json.dumps(meta, indent=1))
print("manifest written for shard", shard)

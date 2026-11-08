from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main() -> None:
    with (ROOT / "cohorts" / "threshold_smoke.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        baselines = {row["model_id"]: row for row in csv.DictReader(handle)}
    with (ROOT / "results" / "h_threshold_smoke.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        results = list(csv.DictReader(handle))

    selected = results[:3] + [
        row
        for row in results
        if row["completion_state_below_threshold"]
        == "BOTH_CLASSES_DISTINGUISHABLE"
    ][:3]
    for row in selected:
        baseline = baselines[row["model_id"]]
        for side in ("below", "above"):
            payload = {
                "baseline": baseline,
                "action": "completion",
                "H": float(row[f"threshold_{'lower' if side == 'below' else 'upper'}_bound"]),
                "verdict": row[f"{side}_verdict"],
            }
            process = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "analysis_step.py"),
                    json.dumps(payload, separators=(",", ":")),
                ],
                capture_output=True,
                text=True,
                timeout=180,
            )
            output = json.loads(process.stdout)["result"]
            print(json.dumps({
                "model_id": row["model_id"],
                "side": side,
                "old_state": row[f"completion_state_{side}_threshold"],
                "new_state": output["completion_state"],
                "normal_exists": output["normal_complete_exists"],
                "faulty_exists": output["faulty_complete_exists"],
                "temporal_states": output["completion_temporal_states"],
                "trace_records": output["completion_trace_records"],
            }, separators=(",", ":")))


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "h_sensitivity_config.json").read_text())
WORKER = ROOT / "complete_analysis_worker.py"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=CONFIG["workers"])
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    _require_disk_safety()

    with args.cohort.open(newline="", encoding="utf-8") as handle:
        models = list(csv.DictReader(handle))
    completed = _completed_ids(args.output) if args.resume else set()
    models = [model for model in models if model["model_id"] not in completed]
    if not models:
        print("no pending complete-analysis models", flush=True)
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if args.resume and args.output.exists() else "w"
    with args.output.open(mode, newline="", encoding="utf-8") as handle:
        writer = None
        started = time.perf_counter()
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            futures = {executor.submit(_run_worker, model): model for model in models}
            for index, future in enumerate(as_completed(futures), 1):
                rows = future.result()
                if writer is None:
                    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                    if handle.tell() == 0:
                        writer.writeheader()
                writer.writerows(rows)
                handle.flush()
                complete = sum(
                    row["execution_status"] == "COMPLETED"
                    and row["enumeration_complete"]
                    and row["candidate_words_processed_all"]
                    for row in rows
                )
                print(
                    f"completed_models={index}/{len(models)} model={rows[0]['model_id']} "
                    f"complete_levels={complete}/{len(rows)} "
                    f"elapsed_s={time.perf_counter() - started:.1f}",
                    flush=True,
                )
                _require_disk_safety()
    return 0


def _run_worker(model: dict) -> list[dict]:
    levels = len(CONFIG["complete_analysis_relative_levels"])
    limit = CONFIG["complete_analysis_timeout_seconds_per_level"] * levels + 30
    process = subprocess.Popen(
        [sys.executable, str(WORKER), json.dumps(model, separators=(",", ":"))],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=limit)
        if process.returncode == 0:
            return json.loads(stdout)
        error = (stderr or stdout or "worker failed").strip()[-2000:]
        status = "ERROR"
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        error = f"model worker timeout after {limit}s"
        status = "TIMEOUT"
    return [_failure(model, level, status, error) for level in CONFIG["complete_analysis_relative_levels"]]


def _failure(model: dict, relative_level: float, status: str, error: str) -> dict:
    H = float(model["H_amb_star"]) * relative_level
    return {
        "model_id": model["model_id"],
        "model_hash": model["model_hash"],
        "cohort_type": model["cohort_type"],
        "cohort_rank": model["cohort_rank"],
        "stratum": model["stratum"],
        "threshold_quantile_bin": model["threshold_quantile_bin"],
        "H_amb_star": model["H_amb_star"],
        "H_amb_ratio": model["H_amb_ratio"],
        "relative_H_level": relative_level,
        "H": H,
        "H_over_H_base": H / float(model["H_base"]),
        "order_rotation": model["order_rotation"],
        "order_position": None,
        "verdict": "INC",
        "execution_status": status,
        "inconclusive_reason": status,
        "certificate_mode": "COMPLETE_SET",
        "enumeration_complete": False,
        "candidate_words_processed_all": False,
        "certificate_count": None,
        "scg_classes": None,
        "scg_edges": None,
        "sync_states": None,
        "candidate_words": None,
        "candidate_words_processed": None,
        "temporal_states": None,
        "trace_records": None,
        "terminal_pairs": None,
        "lp_calls": None,
        "enclosure_rejected_pairs": None,
        "terminal_normal_records": None,
        "terminal_faulty_records": None,
        "terminal_pair_candidates": None,
        "confirmed_critical_pairs": None,
        "runtime_scg": None,
        "runtime_sync": None,
        "runtime_expansion": None,
        "runtime_lp": None,
        "runtime_total": None,
        "wall_runtime_s": (
            CONFIG["complete_analysis_timeout_seconds_per_level"]
            if status == "TIMEOUT"
            else None
        ),
        "peak_memory_mb": None,
        "error": error,
    }


def _completed_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["model_id"]] = counts.get(row["model_id"], 0) + 1
    expected = len(CONFIG["complete_analysis_relative_levels"])
    return {model_id for model_id, count in counts.items() if count >= expected}


def _require_disk_safety() -> None:
    free_mb = shutil.disk_usage(ROOT).free / 1024 / 1024
    experiment_mb = sum(
        path.stat().st_size
        for path in ROOT.rglob("*")
        if path.is_file()
    ) / 1024 / 1024
    if free_mb < CONFIG["minimum_free_disk_mb"]:
        raise SystemExit(f"disk safety stop: free_mb={free_mb:.1f}")
    if experiment_mb > CONFIG["maximum_experiment_size_mb"]:
        raise SystemExit(f"experiment size safety stop: size_mb={experiment_mb:.1f}")


if __name__ == "__main__":
    raise SystemExit(main())

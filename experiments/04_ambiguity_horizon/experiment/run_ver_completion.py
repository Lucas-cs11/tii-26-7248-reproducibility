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
WORKER = ROOT / "ver_completion_worker.py"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "h_ver_completion_raw.csv")
    parser.add_argument("--workers", type=int, default=CONFIG["workers"])
    parser.add_argument("--max-models", type=int)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    _require_disk_safety()
    with Path(CONFIG["source_raw_csv"]).open(newline="", encoding="utf-8") as handle:
        models = [
            row
            for row in csv.DictReader(handle)
            if row["H_ratio"] == "0.5" and row["verdict"] == "VER"
        ]
    if len(models) != 20412:
        raise SystemExit(f"expected 20412 baseline VER models, found {len(models)}")
    if args.max_models is not None:
        models = models[:args.max_models]
    completed = _completed_ids(args.output) if args.resume else set()
    models = [model for model in models if model["model_id"] not in completed]
    if not models:
        print("no pending VER completion tasks", flush=True)
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if args.resume and args.output.exists() else "w"
    with args.output.open(mode, newline="", encoding="utf-8") as handle:
        writer = None
        started = time.perf_counter()
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            futures = {executor.submit(_run_worker, model): model for model in models}
            for index, future in enumerate(as_completed(futures), 1):
                row = future.result()
                if writer is None:
                    writer = csv.DictWriter(handle, fieldnames=list(row))
                    if handle.tell() == 0:
                        writer.writeheader()
                writer.writerow(row)
                handle.flush()
                if index % 10 == 0 or row["completion_status"] != "COMPLETE":
                    print(
                        f"completed={index}/{len(models)} model={row['model_id']} "
                        f"status={row['completion_status']} state={row['completion_state']} "
                        f"elapsed_s={time.perf_counter() - started:.1f}",
                        flush=True,
                    )
                _require_disk_safety()
    return 0


def _run_worker(baseline: dict) -> dict:
    limit = CONFIG["timeout_seconds_per_analysis"]
    process = subprocess.Popen(
        [sys.executable, str(WORKER), json.dumps(baseline, separators=(",", ":"))],
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
        error = f"worker timeout after {limit}s"
        status = "TIMEOUT"
    return {
        "model_id": baseline["model_id"],
        "baseline_model_hash": baseline["model_hash"],
        **model_params_for_failure(baseline),
        "L": baseline["L"],
        "H_base": baseline["H_base"],
        "generated_model_hash": None,
        "model_hash_match": None,
        "structural_candidate_words": baseline["candidate_words"],
        "structural_h_insensitive": baseline["candidate_words"] == "0",
        "completion_status": status,
        "completion_state": "UNAVAILABLE",
        "normal_complete_exists": None,
        "faulty_complete_exists": None,
        "completion_sync_states": None,
        "completion_temporal_states": None,
        "completion_trace_records": None,
        "runtime_total_s": limit if status == "TIMEOUT" else None,
        "peak_memory_mb": None,
        "python_version": None,
        "numpy_version": None,
        "scipy_version": None,
        "error": error,
    }


def model_params_for_failure(row: dict) -> dict:
    return {
        name: row[name]
        for name in (
            "n_machines",
            "n_parts",
            "ops_per_part",
            "wip_bound",
            "unobservable_ratio",
            "fault_locations",
            "interval_width_factor",
            "adjustable_ratio",
            "seed",
        )
    }


def _completed_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["model_id"] for row in csv.DictReader(handle)}


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

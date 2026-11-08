from __future__ import annotations

import argparse
import csv
import json
import os
import signal
import shutil
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "h_sensitivity_config.json").read_text())
WORKER = ROOT / "threshold_worker.py"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", type=Path, default=ROOT / "cohorts" / "threshold_smoke.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "h_threshold_smoke.csv")
    parser.add_argument("--workers", type=int, default=CONFIG["workers"])
    parser.add_argument("--baseline-verdict", choices=("AMB", "VER"))
    parser.add_argument("--max-models", type=int)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    _require_disk_safety()
    with args.cohort.open(newline="", encoding="utf-8") as handle:
        models = list(csv.DictReader(handle))
    if args.baseline_verdict:
        models = [
            model
            for model in models
            if model["H_ratio"] == "0.5"
            and model["verdict"] == args.baseline_verdict
        ]
    if args.max_models is not None:
        models = models[:args.max_models]
    completed = _completed_ids(args.output) if args.resume else set()
    tasks = [
        {
            "baseline": model,
            "timeout_seconds": CONFIG["timeout_seconds_per_analysis"],
            "direct_timeout_seconds": CONFIG["direct_timeout_seconds"],
            "threshold_upper_ratio": CONFIG["threshold_upper_ratio"],
            "epsilon_ratio": CONFIG["threshold_epsilon_ratio"],
            "bisection_iterations": CONFIG["threshold_bisection_iterations"],
            "witness_descent_max_iterations": CONFIG["witness_descent_max_iterations"],
        }
        for model in models
        if model["model_id"] not in completed
    ]
    if not tasks:
        print("no pending threshold tasks", flush=True)
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if args.resume and args.output.exists() else "w"
    handle = args.output.open(mode, newline="", encoding="utf-8")
    writer = None
    buffered: list[dict] = []
    started = time.perf_counter()
    executor = ProcessPoolExecutor(max_workers=args.workers)
    stop_reason = None
    try:
        try:
            futures = {executor.submit(_run_worker, task): task for task in tasks}
            for index, future in enumerate(as_completed(futures), 1):
                row = future.result()
                if writer is None and "H_base" in row:
                    writer = csv.DictWriter(handle, fieldnames=list(row), extrasaction="ignore")
                    if handle.tell() == 0:
                        writer.writeheader()
                    writer.writerows(buffered)
                    buffered = []
                if writer is None:
                    buffered.append(row)
                else:
                    writer.writerow(row)
                handle.flush()
                print(
                    f"completed={index}/{len(tasks)} model={row['model_id']} "
                    f"method={row.get('threshold_method')} status={row['execution_status']} "
                    f"validation={row['validation_status']} elapsed_s={time.perf_counter() - started:.1f}",
                    flush=True,
                )
                _require_disk_safety()
        except BaseException as exc:  # disk safety stop, Ctrl-C, worker blow-up
            stop_reason = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            # Never block on pending futures: cancel them so the run stops
            # promptly instead of silently churning through the remaining
            # queue with results discarded (observed 2026-11-02).
            try:
                executor.shutdown(wait=False, cancel_futures=True)
            except TypeError:  # Python < 3.9
                executor.shutdown(wait=False)
            if stop_reason:
                print(f"STOPPED_EARLY reason={stop_reason}", flush=True)
    finally:
        if stop_reason:
            # Hard cleanup: worker subprocesses are spawned with
            # start_new_session=True, so they survive a pool kill and keep
            # burning CPU with results discarded.  Kill them explicitly and
            # exit without running concurrent.futures' blocking atexit join.
            try:
                subprocess.run(["pkill", "-9", "-f", str(WORKER)], timeout=10)
            except Exception:
                pass
            try:
                handle.close()
            except Exception:
                pass
            os._exit(1)
        if writer is None and buffered:
            writer = csv.DictWriter(handle, fieldnames=list(buffered[0]), extrasaction="ignore")
            if handle.tell() == 0:
                writer.writeheader()
            writer.writerows(buffered)
        handle.close()
    return 0


def _run_worker(task: dict) -> dict:
    limit = CONFIG["threshold_case_timeout_seconds"]
    try:
        process = subprocess.Popen(
            [sys.executable, str(WORKER), json.dumps(task, separators=(",", ":"))],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        stdout, stderr = process.communicate(timeout=limit)
        if process.returncode == 0:
            return json.loads(stdout)
        error = (stderr or stdout or "worker failed").strip()[-2000:]
        status = "ERROR"
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            if process.poll() is None:
                process.kill()
        process.communicate()
        error = f"worker timeout after {limit}s"
        status = "TIMEOUT"
    except Exception as exception:
        error = f"{type(exception).__name__}: {exception}"
        status = "ERROR"
    return {
        "model_id": task["baseline"]["model_id"],
        "threshold_method": None,
        "execution_status": status,
        "validation_status": "FAIL",
        "error": error,
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

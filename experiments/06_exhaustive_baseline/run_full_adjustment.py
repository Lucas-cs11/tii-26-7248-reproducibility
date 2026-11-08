#!/usr/bin/env python3
"""Driver: run the three adjustment methods independently over the FULL 16,038
AMB population, with checkpoint/resume.

Guarantees:
  * every (evaluation_id, method) pair is executed exactly once unless it was
    already recorded as a terminal record in the checkpoint file;
  * no method's outcome gates another method's execution;
  * per-case subprocess with hard wall-clock kill (verify + repair + verify + margin);
  * BLAS/OpenMP thread oversubscription disabled via environment.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import queue
import subprocess
import sys
import threading
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POP = ROOT / "population/full_amb_population.csv.gz"
RESULTS = ROOT / "results"
CKPT = ROOT / "checkpoints"
LOGS = ROOT / "logs"
RUN_CASE = ROOT / "tools/run_case.py"
_venv_py = ROOT / ".venv/bin/python"
PY = _venv_py if _venv_py.exists() else Path(sys.executable)

METHODS = ["cpgld", "coquand", "exhaustive"]

ENV = dict(os.environ)
ENV.update({
    "OPENBLAS_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "PYTHONHASHSEED": "0",
    "PATH": str(ROOT / ".venv/bin") + ":" + os.environ.get("PATH", ""),
})


def load_population():
    rows = []
    with gzip.open(POP, "rt", newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def ckpt_path(method: str) -> Path:
    return CKPT / f"{method}.jsonl"


def load_done(method: str):
    """Return dict evaluation_id -> record, and set of duplicate keys found."""
    p = ckpt_path(method)
    done, dup = {}, set()
    if not p.exists():
        return done, dup
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            eid = rec.get("evaluation_id")
            if eid in done:
                dup.add(eid)
            done[eid] = rec
    return done, dup


def append_record(method: str, rec: dict, lock: threading.Lock):
    with lock:
        with open(ckpt_path(method), "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())


def run_one(method: str, row: dict, hard_timeout: float):
    params = {
        "n_machines": int(row["n_machines"]),
        "n_parts": int(row["n_parts"]),
        "ops_per_part": int(row["ops_per_part"]),
        "wip_bound": int(row["wip_bound"]),
        "unobservable_ratio": float(row["unobservable_ratio"]),
        "fault_locations": int(row["fault_locations"]),
        "interval_width_factor": float(row["interval_width_factor"]),
        "adjustable_ratio": float(row["adjustable_ratio"]),
        "seed": int(row["seed"]),
    }
    cmd = [
        str(PY), str(RUN_CASE), method, row["evaluation_id"],
        json.dumps(params), str(row["L"]), str(row["H"]),
    ]
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=hard_timeout, env=ENV,
            cwd=str(ROOT),
        )
        out = (proc.stdout or "").strip().splitlines()
        if not out:
            return {
                "evaluation_id": row["evaluation_id"], "method": method,
                "status": "ERROR", "error_type": f"NO_OUTPUT:rc={proc.returncode}",
                "stderr": (proc.stderr or "")[-300:],
                "runtime_seconds": round(time.perf_counter() - t0, 4),
            }
        rec = json.loads(out[-1])
        if "stderr" in proc.stderr and proc.returncode != 0:
            rec.setdefault("stderr", (proc.stderr or "")[-300:])
        return rec
    except subprocess.TimeoutExpired:
        return {
            "evaluation_id": row["evaluation_id"], "method": method,
            "status": "TIMEOUT", "timeout_phase": "hard_kill",
            "timeout_seconds": hard_timeout,
            "runtime_seconds": round(time.perf_counter() - t0, 4),
        }
    except Exception as e:  # noqa: BLE001
        return {
            "evaluation_id": row["evaluation_id"], "method": method,
            "status": "ERROR", "error_type": f"{type(e).__name__}:{e}"[:200],
            "runtime_seconds": round(time.perf_counter() - t0, 4),
        }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--methods", default=",".join(METHODS))
    ap.add_argument("--limit", type=int, default=0, help="limit cases per method (smoke)")
    ap.add_argument("--tag", default="")
    ap.add_argument("--ids-file", default="", help="JSON list of population rows to restrict to (smoke)")
    ap.add_argument("--verify-timeout", type=float, default=120.0)
    ap.add_argument("--repair-timeout", type=float, default=300.0)
    args = ap.parse_args()

    if args.workers < 1 or args.workers > 10:
        sys.exit("workers must be 1..10")

    hard_timeout = args.verify_timeout + args.repair_timeout + args.verify_timeout + 90
    RESULTS.mkdir(parents=True, exist_ok=True)
    CKPT.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)

    env_out = {k: ENV[k] for k in (
        "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "PYTHONHASHSEED")}
    with open(LOGS / f"run_env{args.tag}.json", "w") as f:
        json.dump({"env": env_out, "workers": args.workers,
                   "verify_timeout": args.verify_timeout,
                   "repair_timeout": args.repair_timeout,
                   "hard_timeout": hard_timeout,
                   "started": datetime.now().isoformat(timespec="seconds")},
                  f, indent=1)

    pop = load_population()
    print(f"population: {len(pop)} rows", flush=True)
    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    lock = threading.Lock()

    ids_filter = None
    if args.ids_file:
        with open(args.ids_file) as f:
            ids_filter = {r["evaluation_id"] for r in json.load(f)}
        pop = [r for r in pop if r["evaluation_id"] in ids_filter]
        print(f"ids-file filter: {len(pop)} cases", flush=True)

    for method in methods:
        done, dup = load_done(method)
        todo = [r for r in pop if r["evaluation_id"] not in done]
        if args.limit:
            todo = todo[: args.limit]
        total = len(todo)
        print(f"\n[{method}] already_done={len(done)} duplicates={len(dup)} todo={total}",
              flush=True)
        if total == 0:
            continue

        cnt = Counter()
        q: queue.Queue = queue.Queue()
        for r in todo:
            q.put(r)
        t_start = time.perf_counter()
        stop = threading.Event()

        mon = threading.Thread(
            target=_monitor, args=(method, t_start, q, lock, stop, args.workers),
            daemon=True)
        mon.start()

        def worker():
            while not stop.is_set():
                try:
                    row = q.get_nowait()
                except queue.Empty:
                    return
                rec = run_one(method, row, hard_timeout)
                rec.setdefault("method", method)
                append_record(method, rec, lock)
                with lock:
                    cnt[rec.get("status", "UNKNOWN")] += 1
                    n = sum(cnt.values())
                    if n % 25 == 0 or n == total:
                        el = time.perf_counter() - t_start
                        rate = n / el if el > 0 else 0
                        eta = (total - n) / rate / 3600 if rate > 0 else float("inf")
                        print(f"[{method}] {n}/{total} elapsed={el/60:.1f}min "
                              f"rate={rate*3600:.0f}/h eta={eta:.1f}h "
                              f"status={dict(cnt)}", flush=True)
                q.task_done()

        threads = [threading.Thread(target=worker, daemon=True)
                   for _ in range(args.workers)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        stop.set()
        el = time.perf_counter() - t_start
        print(f"[{method}] DONE {sum(cnt.values())} cases in {el/60:.1f} min: "
              f"{dict(cnt)}", flush=True)
        with open(LOGS / f"method_summary{args.tag}.json", "a") as f:
            f.write(json.dumps({"method": method, "counts": dict(cnt),
                                "elapsed_s": round(el, 1),
                                "finished": datetime.now().isoformat(timespec="seconds")}) + "\n")

    return 0


def _monitor(method, t_start, q, lock, stop, workers):
    while not stop.is_set():
        time.sleep(300)
        if stop.is_set():
            return
        try:
            out = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=10).stdout
            swap = subprocess.run(["sysctl", "-n", "vm.swapusage"], capture_output=True,
                                  text=True, timeout=10).stdout.strip()
        except Exception:  # noqa: BLE001
            out, swap = "", ""
        with lock:
            remaining = q.qsize()
        with open(LOGS / "resource_monitor.log", "a") as f:
            f.write(json.dumps({
                "ts": datetime.now().isoformat(timespec="seconds"),
                "method": method, "remaining": remaining, "workers": workers,
                "elapsed_min": round((time.perf_counter() - t_start) / 60, 1),
                "swap": swap}) + "\n")


if __name__ == "__main__":
    sys.exit(main())

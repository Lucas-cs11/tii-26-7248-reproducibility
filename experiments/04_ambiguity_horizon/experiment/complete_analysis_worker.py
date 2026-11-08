from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "h_sensitivity_config.json").read_text())
STEP = ROOT / "analysis_step.py"


def main() -> None:
    model = json.loads(sys.argv[1])
    levels = CONFIG["complete_analysis_relative_levels"]
    rotation = int(model["order_rotation"])
    ordered_levels = levels[rotation:] + levels[:rotation]
    rows = []
    for order_position, relative_level in enumerate(ordered_levels):
        rows.append(_run_level(model, relative_level, order_position))
    print(json.dumps(rows, separators=(",", ":")))


def _run_level(model: dict, relative_level: float, order_position: int) -> dict:
    # baseline-normalized Experiment B: H = H_base * H_ratio (NOT H_amb_star)
    H = float(model["H_base"]) * relative_level
    payload = {
        "baseline": model,
        "action": "complete_analysis",
        "H": H,
    }
    started = time.perf_counter()
    process = subprocess.Popen(
        [sys.executable, str(STEP), json.dumps(payload, separators=(",", ":"))],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(
            timeout=CONFIG["complete_analysis_timeout_seconds_per_level"]
        )
        if process.returncode != 0:
            return _failure(
                model,
                relative_level,
                H,
                order_position,
                "ERROR",
                stderr or stdout,
                time.perf_counter() - started,
            )
        output = json.loads(stdout)
        result = output["result"]
        stats = result["stats"]
        return {
            "model_id": model["model_id"],
            "model_hash": output["model_hash"],
            "cohort_type": model["cohort_type"],
            "cohort_rank": model["cohort_rank"],
            "stratum": model["stratum"],
            "threshold_quantile_bin": model["threshold_quantile_bin"],
            "H_amb_star": model["H_amb_star"],
            "H_amb_ratio": model["H_amb_ratio"],
            "relative_H_level": relative_level,
            "H_base": float(model["H_base"]),
            "H_ratio": relative_level,
            "H_value": H,
            "H": H,
            "H_over_H_base": H / output["H_base"],
            "order_rotation": model["order_rotation"],
            "order_position": order_position,
            "verdict": result["verdict"],
            "execution_status": "COMPLETED",
            "inconclusive_reason": result["inconclusive_reason"],
            "certificate_mode": result["certificate_mode"],
            "enumeration_complete": result["enumeration_complete"],
            "candidate_words_processed_all": (
                stats["candidate_words_processed"] == stats["candidate_words"]
            ),
            "certificate_count": result["certificate_count"],
            **stats,
            "wall_runtime_s": time.perf_counter() - started,
            "peak_memory_mb": output["peak_memory_mb"],
            "error": None,
        }
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        return _failure(
            model,
            relative_level,
            H,
            order_position,
            "TIMEOUT",
            "level timeout",
            time.perf_counter() - started,
        )


def _failure(
    model: dict,
    relative_level: float,
    H: float,
    order_position: int,
    status: str,
    error: str,
    wall_runtime_s: float,
) -> dict:
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
        "H_base": float(model["H_base"]),
        "H_ratio": relative_level,
        "H_value": H,
        "H": H,
        "H_over_H_base": H / float(model["H_base"]),
        "order_rotation": model["order_rotation"],
        "order_position": order_position,
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
        "wall_runtime_s": wall_runtime_s,
        "peak_memory_mb": None,
        "error": error.strip()[-2000:],
    }


if __name__ == "__main__":
    main()

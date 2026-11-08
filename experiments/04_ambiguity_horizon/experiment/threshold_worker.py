from __future__ import annotations

import hashlib
import json
import os
import platform
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import numpy
import scipy

from experiment_common import model_hash, model_params, peak_memory_mb
from src.benchmarks.rmt_fms_generator import generate_rmt_fms
from src.model.validation import validate_model


STEP = ROOT / "analysis_step.py"


class StepTimeout(Exception):
    pass


def main() -> None:
    task = json.loads(sys.argv[1])
    started = time.perf_counter()
    row = _base_row(task)
    try:
        tpn, L, H_base = generate_rmt_fms(**model_params(task["baseline"]))
        errors = validate_model(tpn)
        if errors:
            raise ValueError("VALIDATION: " + "; ".join(errors))
        generated_hash = model_hash(tpn)
        row.update({
            "L": L,
            "H_base": H_base,
            "generated_model_hash": generated_hash,
            "model_hash_match": generated_hash == task["baseline"]["model_hash"],
            "n_places": len(tpn.places),
            "n_transitions": len(tpn.transitions),
        })
        if not row["model_hash_match"]:
            raise ValueError("MODEL_HASH_MISMATCH")

        witness_started = time.perf_counter()
        witness = _run_step(
            task,
            "witness",
            H=task["threshold_upper_ratio"] * H_base,
        )
        if witness["verdict"] != "AMB":
            raise ValueError(f"WITNESS_NOT_AMBIGUOUS: {witness['verdict']}")
        epsilon = max(H_base * task["epsilon_ratio"], 1.0e-7)
        search_upper = min(
            task["threshold_upper_ratio"] * H_base,
            witness["H_witness"] + epsilon,
        )
        row.update({
            "witness_H": witness["H_witness"],
            "witness_ratio": witness["H_witness"] / H_base,
            "witness_runtime_s": time.perf_counter() - witness_started,
            "search_upper_H": search_upper,
            "search_upper_ratio": search_upper / H_base,
        })

        direct_started = time.perf_counter()
        try:
            direct = _run_step(
                task,
                "direct",
                H=search_upper,
                timeout_seconds=task["direct_timeout_seconds"],
            )
            row["direct_runtime_s"] = time.perf_counter() - direct_started
            _record_direct(row, direct, H_base)
        except StepTimeout:
            direct = {"status": "TIMEOUT"}
            row["direct_status"] = "TIMEOUT"
            row["direct_runtime_s"] = time.perf_counter() - direct_started

        direct_valid = False
        if direct["status"] == "OPTIMAL":
            direct_valid = _validate_direct(row, task, tpn, L, H_base, direct)

        if direct_valid:
            row["threshold_method"] = "DIRECT_COUPLED_LP"
        elif _run_witness_descent(row, task, H_base, witness):
            pass
        else:
            _run_bisection(row, task, H_base, search_upper / H_base)

        if row["validation_status"] == "PASS":
            _record_completion_profiles(row, task)
        row["execution_status"] = "COMPLETED"
    except StepTimeout:
        row["execution_status"] = "TIMEOUT"
        row["validation_status"] = "FAIL"
        row["error"] = "analysis timeout"
    except Exception as error:
        row["execution_status"] = "ERROR"
        row["validation_status"] = "FAIL"
        row["error"] = f"{type(error).__name__}: {error}"
    row["runtime_total_s"] = time.perf_counter() - started
    row["peak_memory_mb"] = peak_memory_mb()
    print(json.dumps(row, separators=(",", ":")))


def _base_row(task: dict) -> dict:
    baseline = task["baseline"]
    return {
        "model_id": baseline["model_id"],
        "baseline_model_hash": baseline["model_hash"],
        "baseline_verdict": baseline["verdict"],
        **model_params(baseline),
        "L": None,
        "H_base": None,
        "generated_model_hash": None,
        "model_hash_match": False,
        "n_places": None,
        "n_transitions": None,
        "witness_H": None,
        "witness_ratio": None,
        "witness_runtime_s": None,
        "search_upper_H": None,
        "search_upper_ratio": None,
        "threshold_method": None,
        "direct_status": None,
        "direct_enumeration_complete": None,
        "direct_runtime_s": None,
        "witness_descent_iterations": 0,
        "witness_descent_status": None,
        "H_amb_star": None,
        "H_amb_ratio": None,
        "threshold_lower_bound": None,
        "threshold_upper_bound": None,
        "threshold_precision": None,
        "epsilon": None,
        "below_verdict": None,
        "above_verdict": None,
        "completion_state_below_threshold": None,
        "completion_state_above_threshold": None,
        "normal_complete_below": None,
        "faulty_complete_below": None,
        "normal_complete_above": None,
        "faulty_complete_above": None,
        "H_comp_normal_below": None,
        "H_comp_faulty_below": None,
        "H_comp_normal_above": None,
        "H_comp_faulty_above": None,
        "completion_minima_status_below": None,
        "completion_minima_status_above": None,
        "critical_pair_id": None,
        "observable_word": None,
        "normal_sequence": None,
        "faulty_sequence": None,
        "critical_overlap_max": None,
        "direct_candidate_words": None,
        "direct_candidate_words_processed": None,
        "direct_temporal_states": None,
        "direct_trace_records": None,
        "direct_terminal_pair_candidates": None,
        "direct_threshold_bound_pruned_pairs": None,
        "direct_terminal_pairs": None,
        "direct_lp_calls": None,
        "direct_confirmed_critical_pairs": None,
        "validation_status": "FAIL",
        "execution_status": "ERROR",
        "runtime_total_s": None,
        "peak_memory_mb": None,
        "python_version": platform.python_version(),
        "numpy_version": numpy.__version__,
        "scipy_version": scipy.__version__,
        "error": None,
    }


def _record_direct(row: dict, direct: dict, H_base: float) -> None:
    row["direct_status"] = direct["status"]
    row["direct_enumeration_complete"] = direct.get("enumeration_complete")
    if direct["status"] != "OPTIMAL":
        return
    row.update({
        "H_amb_star": direct["H_amb_star"],
        "H_amb_ratio": direct["H_amb_star"] / H_base,
        "critical_pair_id": direct["critical_pair_id"],
        "observable_word": json.dumps(direct["observable_word"], separators=(",", ":")),
        "normal_sequence": json.dumps(direct["normal_sequence"], separators=(",", ":")),
        "faulty_sequence": json.dumps(direct["faulty_sequence"], separators=(",", ":")),
        "critical_overlap_max": direct["critical_overlap_max"],
    })
    for source, target in (
        ("candidate_words", "direct_candidate_words"),
        ("candidate_words_processed", "direct_candidate_words_processed"),
        ("temporal_states", "direct_temporal_states"),
        ("trace_records", "direct_trace_records"),
        ("terminal_pair_candidates", "direct_terminal_pair_candidates"),
        ("threshold_bound_pruned_pairs", "direct_threshold_bound_pruned_pairs"),
        ("terminal_pairs", "direct_terminal_pairs"),
        ("lp_calls", "direct_lp_calls"),
        ("confirmed_critical_pairs", "direct_confirmed_critical_pairs"),
    ):
        row[target] = direct["stats"].get(source)


def _validate_direct(
    row: dict,
    task: dict,
    tpn,
    L: int,
    H_base: float,
    direct: dict,
) -> bool:
    epsilon = max(H_base * task["epsilon_ratio"], 1.0e-7)
    H_minus = max(0.0, direct["H_amb_star"] - epsilon)
    H_plus = direct["H_amb_star"] + epsilon
    below = _run_step(task, "verdict", H=H_minus)
    above = _run_step(task, "verdict", H=H_plus)
    row.update({
        "epsilon": epsilon,
        "threshold_lower_bound": H_minus,
        "threshold_upper_bound": H_plus,
        "threshold_precision": H_plus - H_minus,
        "below_verdict": below["verdict"],
        "above_verdict": above["verdict"],
        "validation_status": (
            "PASS"
            if below["verdict"] == "VER" and above["verdict"] == "AMB"
            else "FAIL"
        ),
    })
    return row["validation_status"] == "PASS"


def _run_witness_descent(
    row: dict,
    task: dict,
    H_base: float,
    initial_witness: dict,
) -> bool:
    epsilon = max(H_base * task["epsilon_ratio"], 1.0e-7)
    current = initial_witness
    for iteration in range(1, task["witness_descent_max_iterations"] + 1):
        if current["H_witness"] <= 0:
            row["witness_descent_status"] = "THRESHOLD_AT_ZERO_UNVALIDATED"
            return False
        probe_H = max(0.0, current["H_witness"] - epsilon)
        try:
            probe = _run_step(task, "witness", H=probe_H)
        except StepTimeout:
            row["witness_descent_status"] = "TIMEOUT"
            return False
        row["witness_descent_iterations"] = iteration
        if probe["verdict"] == "VER":
            pair_payload = json.dumps(
                [
                    current["observable_word"],
                    current["normal_sequence"],
                    current["faulty_sequence"],
                ],
                separators=(",", ":"),
            )
            row.update({
                "threshold_method": "MONOTONIC_WITNESS_DESCENT",
                "H_amb_star": current["H_witness"],
                "H_amb_ratio": current["H_witness"] / H_base,
                "threshold_lower_bound": probe_H,
                "threshold_upper_bound": current["H_witness"],
                "threshold_precision": current["H_witness"] - probe_H,
                "epsilon": epsilon,
                "below_verdict": "VER",
                "above_verdict": "AMB",
                "critical_pair_id": hashlib.sha256(pair_payload.encode()).hexdigest()[:20],
                "observable_word": json.dumps(current["observable_word"], separators=(",", ":")),
                "normal_sequence": json.dumps(current["normal_sequence"], separators=(",", ":")),
                "faulty_sequence": json.dumps(current["faulty_sequence"], separators=(",", ":")),
                "validation_status": "PASS",
                "witness_descent_status": "PASS",
            })
            return True
        if probe["verdict"] != "AMB":
            row["witness_descent_status"] = f"INCONCLUSIVE_{probe['verdict']}"
            return False
        if probe["H_witness"] >= current["H_witness"] - epsilon / 2:
            row["witness_descent_status"] = "NUMERICAL_STALL"
            return False
        current = probe

    row["witness_descent_status"] = "ITERATION_LIMIT"
    return False


def _run_bisection(
    row: dict,
    task: dict,
    H_base: float,
    search_upper_ratio: float,
) -> None:
    lower_ratio = 0.0
    upper_ratio = search_upper_ratio
    lower = _run_step(task, "verdict", H=0.0)
    upper = _run_step(task, "verdict", H=upper_ratio * H_base)
    if lower["verdict"] == "INC" or upper["verdict"] != "AMB":
        row.update({
            "threshold_method": "BISECTION_FAILED",
            "below_verdict": lower["verdict"],
            "above_verdict": upper["verdict"],
            "validation_status": "FAIL",
        })
        return
    if lower["verdict"] == "AMB":
        upper_ratio = 0.0
    else:
        for _ in range(task["bisection_iterations"]):
            middle_ratio = (lower_ratio + upper_ratio) / 2
            middle = _run_step(task, "verdict", H=middle_ratio * H_base)
            if middle["verdict"] == "INC":
                row.update({
                    "threshold_method": "BISECTION_FAILED",
                    "below_verdict": lower["verdict"],
                    "above_verdict": middle["verdict"],
                    "validation_status": "FAIL",
                })
                return
            if middle["verdict"] == "AMB":
                upper_ratio = middle_ratio
                upper = middle
                continue
            lower_ratio = middle_ratio
            lower = middle

    row.update({
        "threshold_method": "MONOTONIC_BISECTION",
        "H_amb_star": upper_ratio * H_base,
        "H_amb_ratio": upper_ratio,
        "threshold_lower_bound": lower_ratio * H_base,
        "threshold_upper_bound": upper_ratio * H_base,
        "threshold_precision": (upper_ratio - lower_ratio) * H_base,
        "below_verdict": lower["verdict"],
        "above_verdict": upper["verdict"],
        "validation_status": "PASS",
    })


def _record_completion_profiles(row: dict, task: dict) -> None:
    try:
        below = _run_step(
            task,
            "completion",
            H=row["threshold_lower_bound"],
            verdict=row["below_verdict"],
        )
    except StepTimeout:
        below = _timed_out_completion()
    try:
        above = _run_step(
            task,
            "completion",
            H=row["threshold_upper_bound"],
            verdict=row["above_verdict"],
        )
    except StepTimeout:
        above = _timed_out_completion()
    row.update({
        "completion_state_below_threshold": below["completion_state"],
        "completion_state_above_threshold": above["completion_state"],
        "normal_complete_below": below["normal_complete_exists"],
        "faulty_complete_below": below["faulty_complete_exists"],
        "normal_complete_above": above["normal_complete_exists"],
        "faulty_complete_above": above["faulty_complete_exists"],
        "H_comp_normal_below": below["H_comp_normal"],
        "H_comp_faulty_below": below["H_comp_faulty"],
        "H_comp_normal_above": above["H_comp_normal"],
        "H_comp_faulty_above": above["H_comp_faulty"],
        "completion_minima_status_below": below.get("completion_minima_status", "UNAVAILABLE"),
        "completion_minima_status_above": above.get("completion_minima_status", "UNAVAILABLE"),
    })
    if below["status"] != "COMPLETE" or above["status"] != "COMPLETE":
        row["error"] = "completion profile unavailable"


def _run_step(task: dict, action: str, **fields):
    timeout = fields.pop("timeout_seconds", task["timeout_seconds"])
    payload = {"baseline": task["baseline"], "action": action, **fields}
    try:
        process = subprocess.Popen(
            [sys.executable, str(STEP), json.dumps(payload, separators=(",", ":"))],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as error:
        try:
            process.kill()
        except ProcessLookupError:
            pass
        process.communicate()
        raise StepTimeout(action) from error
    if process.returncode != 0:
        error = (stderr or stdout or "analysis step failed").strip()[-2000:]
        raise RuntimeError(f"{action}: {error}")
    output = json.loads(stdout)
    if output["model_hash"] != task["baseline"]["model_hash"]:
        raise RuntimeError(f"{action}: MODEL_HASH_MISMATCH")
    return output["result"]


def _timed_out_completion() -> dict:
    return {
        "status": "TIMEOUT",
        "completion_state": "UNAVAILABLE",
        "normal_complete_exists": None,
        "faulty_complete_exists": None,
        "H_comp_normal": None,
        "H_comp_faulty": None,
        "completion_minima_status": "UNAVAILABLE_TIMEOUT",
    }


if __name__ == "__main__":
    main()

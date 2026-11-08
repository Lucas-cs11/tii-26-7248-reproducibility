from __future__ import annotations

import json
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import numpy
import scipy

from experiment_common import model_hash, model_params, peak_memory_mb
from src.benchmarks.rmt_fms_generator import generate_rmt_fms
from src.h_sensitivity import completion_profile
from src.model.validation import validate_model


def main() -> None:
    baseline = json.loads(sys.argv[1])
    started = time.perf_counter()
    row = {
        "model_id": baseline["model_id"],
        "baseline_model_hash": baseline["model_hash"],
        **model_params(baseline),
        "L": None,
        "H_base": None,
        "generated_model_hash": None,
        "model_hash_match": False,
        "structural_candidate_words": None,
        "structural_h_insensitive": None,
        "completion_status": "ERROR",
        "completion_state": "UNAVAILABLE",
        "normal_complete_exists": None,
        "faulty_complete_exists": None,
        "completion_sync_states": None,
        "completion_temporal_states": None,
        "completion_trace_records": None,
        "runtime_total_s": None,
        "peak_memory_mb": None,
        "python_version": platform.python_version(),
        "numpy_version": numpy.__version__,
        "scipy_version": scipy.__version__,
        "error": None,
    }
    try:
        tpn, L, H_base = generate_rmt_fms(**model_params(baseline))
        errors = validate_model(tpn)
        if errors:
            raise ValueError("VALIDATION: " + "; ".join(errors))
        generated_hash = model_hash(tpn)
        if generated_hash != baseline["model_hash"]:
            raise ValueError("MODEL_HASH_MISMATCH")
        profile = completion_profile(tpn, L, H_base, "VER")
        row.update({
            "L": L,
            "H_base": H_base,
            "generated_model_hash": generated_hash,
            "model_hash_match": True,
            "structural_candidate_words": profile.get("structural_candidate_words"),
            "structural_h_insensitive": profile.get("structural_candidate_words") == 0,
            "completion_status": profile["status"],
            "completion_state": profile["completion_state"],
            "normal_complete_exists": profile["normal_complete_exists"],
            "faulty_complete_exists": profile["faulty_complete_exists"],
            "completion_sync_states": profile.get("completion_sync_states"),
            "completion_temporal_states": profile.get("completion_temporal_states"),
            "completion_trace_records": profile.get("completion_trace_records"),
        })
    except Exception as error:
        row["error"] = f"{type(error).__name__}: {error}"
    row["runtime_total_s"] = time.perf_counter() - started
    row["peak_memory_mb"] = peak_memory_mb()
    print(json.dumps(row, separators=(",", ":")))


if __name__ == "__main__":
    main()

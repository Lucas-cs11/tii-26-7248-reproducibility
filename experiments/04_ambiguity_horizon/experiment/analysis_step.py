from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from experiment_common import model_hash, model_params, peak_memory_mb
from src.benchmarks.rmt_fms_generator import generate_rmt_fms
from src.h_sensitivity import completion_profile, direct_ambiguity_threshold
from src.model.validation import validate_model
from src.verifier import verify


def main() -> None:
    task = json.loads(sys.argv[1])
    tpn, L, H_base = generate_rmt_fms(**model_params(task["baseline"]))
    errors = validate_model(tpn)
    if errors:
        raise ValueError("VALIDATION: " + "; ".join(errors))
    generated_hash = model_hash(tpn)
    if generated_hash != task["baseline"]["model_hash"]:
        raise ValueError("MODEL_HASH_MISMATCH")

    if task["action"] == "witness":
        output = verify(tpn, L, task["H"])
        result = {
            "verdict": output["result"],
            "inconclusive_reason": output.get("inconclusive_reason"),
            "stats": output["stats"],
        }
        if output["result"] == "AMB":
            certificate = output["certificates"][0]
            result.update({
                "H_witness": float(certificate.overlap[0]),
                "observable_word": certificate.phi,
                "normal_sequence": certificate.sigma_N,
                "faulty_sequence": certificate.sigma_F,
            })
    elif task["action"] == "direct":
        result = direct_ambiguity_threshold(tpn, L, task["H"])
    elif task["action"] == "verdict":
        output = verify(tpn, L, task["H"])
        result = {
            "verdict": output["result"],
            "inconclusive_reason": output.get("inconclusive_reason"),
            "enumeration_complete": output["enumeration_complete"],
            "stats": output["stats"],
        }
    elif task["action"] == "completion":
        result = completion_profile(tpn, L, task["H"], task["verdict"])
    elif task["action"] == "complete_analysis":
        output = verify(tpn, L, task["H"], complete_set=True)
        result = {
            "verdict": output["result"],
            "inconclusive_reason": output.get("inconclusive_reason"),
            "certificate_mode": output["certificate_mode"],
            "enumeration_complete": output["enumeration_complete"],
            "certificate_count": len(output["certificates"]),
            "stats": output["stats"],
        }
    else:
        raise ValueError(f"unknown action: {task['action']}")

    print(json.dumps({
        "model_hash": generated_hash,
        "L": L,
        "H_base": H_base,
        "peak_memory_mb": peak_memory_mb(),
        "result": result,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()

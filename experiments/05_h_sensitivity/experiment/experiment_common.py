from __future__ import annotations

import csv
import hashlib
import json
import platform
import resource
from pathlib import Path


PARAM_FIELDS = [
    "n_machines",
    "n_parts",
    "ops_per_part",
    "wip_bound",
    "unobservable_ratio",
    "fault_locations",
    "interval_width_factor",
    "adjustable_ratio",
    "seed",
]


def load_baseline_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            row
            for row in csv.DictReader(handle)
            if row["H_ratio"] == "0.5"
        ]


def model_params(row: dict) -> dict:
    return {
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


def model_hash(tpn) -> str:
    data = {
        "places": sorted(tpn.places),
        "transitions": sorted((
            {
                "name": name,
                "label": transition.label,
                "fault": transition.is_fault,
                "adjustable": transition.is_adjustable,
                "earliest": str(transition.interval.earliest),
                "latest": str(transition.interval.latest),
            }
            for name, transition in tpn.transitions.items()
        ), key=lambda item: item["name"]),
        "arcs": sorted(f"{arc.from_node}->{arc.to_node}" for arc in tpn.arcs),
        "initial_marking": sorted(tpn.initial_marking.items()),
        "completion_markings": [
            sorted(marking.items())
            for marking in tpn.completion_markings
        ],
    }
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def peak_memory_mb() -> float:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if platform.system() == "Linux":
        return value / 1024
    return value / 1024 / 1024

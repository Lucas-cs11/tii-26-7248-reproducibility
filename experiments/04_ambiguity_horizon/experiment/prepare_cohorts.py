from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from experiment_common import load_baseline_rows


ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "h_sensitivity_config.json").read_text())
SOURCE_RAW = Path(CONFIG["source_raw_csv"])
SOURCE_VALIDATION = Path(CONFIG["source_validation_json"])
SMOKE = ROOT / "cohorts" / "threshold_smoke.csv"
FEATURES = [
    ("n_parts",),
    ("ops_per_part",),
    ("n_parts", "ops_per_part"),
    ("wip_bound",),
    ("unobservable_ratio",),
    ("fault_locations",),
    ("interval_width_factor",),
    ("adjustable_ratio",),
]


def main() -> None:
    validation = json.loads(SOURCE_VALIDATION.read_text())
    if not validation.get("pass"):
        raise SystemExit("source H-sweep validation did not pass")
    rows = load_baseline_rows(SOURCE_RAW)
    if len(rows) != 36450:
        raise SystemExit(f"expected 36450 baseline rows, found {len(rows)}")
    ambiguous = [row for row in rows if row["verdict"] == "AMB"]
    if len(ambiguous) != 16038:
        raise SystemExit(f"expected 16038 baseline AMB rows, found {len(ambiguous)}")

    selected: list[dict] = []
    available = {row["model_id"]: row for row in ambiguous}
    seen = {feature: set() for feature in FEATURES}
    while len(selected) < CONFIG["threshold_smoke_models"]:
        choice = min(
            available.values(),
            key=lambda row: (
                -sum(_feature_value(row, feature) not in seen[feature] for feature in FEATURES),
                _stable_rank(row["model_id"]),
            ),
        )
        selected.append(choice)
        available.pop(choice["model_id"])
        for feature in FEATURES:
            seen[feature].add(_feature_value(choice, feature))

    SMOKE.parent.mkdir(parents=True, exist_ok=True)
    with SMOKE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(selected[0]))
        writer.writeheader()
        writer.writerows(selected)

    print(json.dumps({
        "source_rows": len(rows),
        "source_ambiguous": len(ambiguous),
        "smoke_models": len(selected),
        "coverage": {
            "+".join(feature): sorted(seen[feature])
            for feature in FEATURES
        },
        "output": str(SMOKE),
    }, indent=2))


def _feature_value(row: dict, feature: tuple[str, ...]):
    value = tuple(row[name] for name in feature)
    if len(value) == 1:
        return value[0]
    return value


def _stable_rank(model_id: str) -> str:
    payload = f"{CONFIG['cohort_seed']}:{model_id}".encode()
    return hashlib.sha256(payload).hexdigest()


if __name__ == "__main__":
    main()

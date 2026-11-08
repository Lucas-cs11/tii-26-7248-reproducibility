from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "h_sensitivity_config.json").read_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=Path, default=ROOT / "results" / "h_threshold_amb_raw.csv")
    parser.add_argument("--size", type=int, required=True)
    parser.add_argument("--cohort-type", choices=("PILOT", "FORMAL"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with args.threshold.open(newline="", encoding="utf-8") as handle:
        threshold_rows = [
            row
            for row in csv.DictReader(handle)
            if row["execution_status"] == "COMPLETED"
            and row["validation_status"] == "PASS"
            and row["H_amb_ratio"]
        ]
    if len(threshold_rows) < args.size:
        raise SystemExit(
            f"need {args.size} validated thresholds, found {len(threshold_rows)}"
        )
    with Path(CONFIG["source_raw_csv"]).open(newline="", encoding="utf-8") as handle:
        baselines = {
            row["model_id"]: row
            for row in csv.DictReader(handle)
            if row["H_ratio"] == "0.5"
        }

    ranked = sorted(threshold_rows, key=lambda row: float(row["H_amb_ratio"]))
    count = len(ranked)
    enriched = []
    for index, threshold in enumerate(ranked):
        baseline = baselines[threshold["model_id"]]
        quantile_bin = min(4, index * 5 // count)
        enriched.append({
            **baseline,
            "H_amb_star": threshold["H_amb_star"],
            "H_amb_ratio": threshold["H_amb_ratio"],
            "threshold_method": threshold["threshold_method"],
            "threshold_validation_status": threshold["validation_status"],
            "threshold_quantile_bin": quantile_bin,
            "stratum": "|".join((
                baseline["n_parts"],
                baseline["ops_per_part"],
                baseline["wip_bound"],
                baseline["unobservable_ratio"],
                baseline["interval_width_factor"],
                str(quantile_bin),
            )),
        })

    strata: dict[str, list[dict]] = {}
    for row in enriched:
        strata.setdefault(row["stratum"], []).append(row)
    for rows in strata.values():
        rows.sort(key=lambda row: _stable_rank(row["model_id"]))
    selected = []
    while len(selected) < args.size:
        progressed = False
        for stratum in sorted(strata):
            if strata[stratum] and len(selected) < args.size:
                selected.append(strata[stratum].pop(0))
                progressed = True
        if not progressed:
            break

    for rank, row in enumerate(selected):
        row["cohort_type"] = args.cohort_type
        row["cohort_rank"] = rank
        row["order_rotation"] = int(_stable_rank(row["model_id"]), 16) % len(
            CONFIG["complete_analysis_relative_levels"]
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(selected[0]))
        writer.writeheader()
        writer.writerows(selected)
    print(json.dumps({
        "cohort_type": args.cohort_type,
        "eligible": len(enriched),
        "selected": len(selected),
        "strata_selected": len({row["stratum"] for row in selected}),
        "output": str(args.output),
    }, indent=2))


def _stable_rank(model_id: str) -> str:
    return hashlib.sha256(
        f"{CONFIG['cohort_seed']}:{model_id}".encode()
    ).hexdigest()


if __name__ == "__main__":
    main()

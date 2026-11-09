#!/usr/bin/env python3
"""Independent recomputation of all R3-2 pilot statistics (no hard-coded rates)."""
import csv, glob, gzip, hashlib, json
from collections import Counter
from pathlib import Path

EXP = Path(__file__).resolve().parents[3]
RESULTS = EXP / "results/pilot_full"
DATA = EXP / "data/frozen"
OUT = EXP / "results/writing_readiness_audit"
OUT.mkdir(parents=True, exist_ok=True)
METHODS = ("cpgld", "coquand", "exhaustive")
PARAMS = ["n_machines","n_parts","ops_per_part","wip_bound","unobservable_ratio",
          "fault_locations","interval_width_factor","adjustable_ratio","seed"]


def load_gz(path):
    with gzip.open(path, "rt") as handle:
        return list(csv.DictReader(handle))


def main():
    population = {row["evaluation_id"]: row for row in load_gz(DATA / "full_amb_population.csv.gz")}
    original = {}
    for method in METHODS:
        for row in load_gz(DATA / f"full_adjustment_{method}.csv.gz"):
            original[(row["evaluation_id"], method)] = row
    manifest = json.loads((EXP / "protocol/pilot_manifest.json").read_text())
    cells = manifest["cells"]
    ids = {cell["evaluation_id"] for cell in cells}
    records = []
    for path in sorted(RESULTS.glob("shard_*.jsonl")):
        for line in path.read_text().splitlines():
            if line.strip():
                records.append(json.loads(line))
    byid = {(r["evaluation_id"], r["method"]): r for r in records}
    duplicate_count = len(records) - len(byid)
    if duplicate_count:
        raise SystemExit(f"duplicate evaluation-method records: {duplicate_count}")
    if len(records) != len(cells) * len(METHODS):
        raise SystemExit(f"record count mismatch {len(records)} != {len(cells)*3}")
    if set(r["evaluation_id"] for r in records) - ids:
        raise SystemExit("records outside frozen pilot manifest")

    summary = {"coverage": {
        "records": len(records), "unique_evaluation_method": len(byid),
        "unique_evaluations": len({r["evaluation_id"] for r in records}),
        "pilot_evaluations": len(cells), "population_evaluations": len(population),
        "population_sha256": hashlib.sha256((DATA/"full_amb_population.csv.gz").read_bytes()).hexdigest(),
        "pilot_manifest_sha256": hashlib.sha256((EXP/"protocol/pilot_manifest.json").read_bytes()).hexdigest(),
        "duplicates": duplicate_count,
    }, "methods": {}, "all": {}, "paired": {}, "path_regimes": {}, "flips": {}, "unresolved": {}}
    for method in METHODS:
        rows = [r for r in records if r["method"] == method]
        attempts = len(rows)
        expected_success = sum(original[(r["evaluation_id"], method)]["status"] == "VERIFIED_SUCCESS" for r in rows)
        exact = sum(original[(r["evaluation_id"], method)]["status"] == "VERIFIED_SUCCESS"
                    and bool(r.get("reconstruction", {}).get("hash_match")) for r in rows)
        mismatch = sum(original[(r["evaluation_id"], method)]["status"] == "VERIFIED_SUCCESS"
                       and not r.get("reconstruction", {}).get("hash_match")
                       and r.get("status") != "INFRA_TIMEOUT_OR_ERROR" for r in rows)
        fresh = [r for r in rows if r.get("fresh_success")]
        pred = [r["predicate"] for r in fresh if "predicate" in r]
        n = len(pred)
        flips = Counter(original[(r["evaluation_id"], method)]["status"] for r in rows
                        if original[(r["evaluation_id"], method)]["status"] != "VERIFIED_SUCCESS"
                        and r.get("fresh_success"))
        compute_limit = Counter(original[(r["evaluation_id"], method)]["status"] for r in rows
                                if r.get("status") == "INFRA_TIMEOUT_OR_ERROR")
        entry = {
            "attempts": attempts,
            "expected_original_successes": expected_success,
            "exact_reconstructions": exact,
            "original_success_true_mismatch": mismatch,
            "fresh_successes": len(fresh),
            "predicate_checked": n,
            "path_pass": sum(p["path_pass"] for p in pred),
            "psi0": sum(p["psi_pass"].get("0", False) for p in pred),
            "psi5": sum(p["psi_pass"].get("5", False) for p in pred),
            "psi10": sum(p["psi_pass"].get("10", False) for p in pred),
            "lost_normal_cases": sum(p["lost_normal"] > 0 for p in pred),
            "lost_normal_words": sum(p["lost_normal"] for p in pred),
            "lost_fault_cases": sum(p["lost_fault"] > 0 for p in pred),
            "lost_fault_words": sum(p["lost_fault"] for p in pred),
            "undetermined_cases": sum(p["undetermined"] > 0 for p in pred),
            "flips_by_original_status": dict(flips),
            "compute_limit_by_original_status": dict(compute_limit),
        }
        for name, value in (("path_pass", entry["path_pass"]), ("psi0", entry["psi0"]),
                            ("psi5", entry["psi5"]), ("psi10", entry["psi10"])):
            entry[f"{name}_rate_successes"] = round(value / n, 6) if n else None
            entry[f"{name}_rate_attempts"] = round(value / attempts, 6)
        for regime in ("full", "sampled"):
            subset = [p for p in pred if p.get("regime") is None]  # marker retained below
            rr = [r for r in fresh if "predicate" in r and r.get("reference", {}).get("regime") == regime]
            pp = [r["predicate"] for r in rr]
            entry[f"{regime}_n"] = len(rr)
            entry[f"{regime}_path_pass"] = sum(p["path_pass"] for p in pp)
            entry[f"{regime}_psi0"] = sum(p["psi_pass"].get("0", False) for p in pp)
            entry[f"{regime}_psi10"] = sum(p["psi_pass"].get("10", False) for p in pp)
        summary["methods"][method] = entry

    # Cohorts with distinct provenance and comparability.
    def cohort_stats(rows):
        pred = [r["predicate"] for r in rows if r.get("fresh_success") and "predicate" in r]
        n = len(pred)
        return {
            "n": n,
            "path_pass": sum(p["path_pass"] for p in pred),
            "psi0": sum(p["psi_pass"].get("0", False) for p in pred),
            "psi5": sum(p["psi_pass"].get("5", False) for p in pred),
            "psi10": sum(p["psi_pass"].get("10", False) for p in pred),
            "lost_normal_cases": sum(p["lost_normal"] > 0 for p in pred),
            "lost_fault_cases": sum(p["lost_fault"] > 0 for p in pred),
            "undetermined_cases": sum(p["undetermined"] > 0 for p in pred),
        }
    original_success_again = [r for r in records
        if original[(r["evaluation_id"], r["method"])]["status"] == "VERIFIED_SUCCESS"
        and r.get("fresh_success")]
    exact_reconstruction = [r for r in original_success_again
        if r.get("reconstruction", {}).get("hash_match")]
    flipped = [r for r in records
        if original[(r["evaluation_id"], r["method"])]["status"] != "VERIFIED_SUCCESS"
        and r.get("fresh_success")]
    summary["cohorts"] = {
        "original_success_again": cohort_stats(original_success_again),
        "exact_reconstruction": cohort_stats(exact_reconstruction),
        "flips": cohort_stats(flipped),
    }
    for cohort_name, subset in (("original_success_again", original_success_again),
                                ("exact_reconstruction", exact_reconstruction),
                                ("flips", flipped)):
        summary["cohorts"][cohort_name]["by_method"] = {
            method: cohort_stats([r for r in subset if r["method"] == method])
            for method in METHODS
        }

    pred_all = [r["predicate"] for r in records if r.get("fresh_success") and "predicate" in r]
    n = len(pred_all)
    summary["all"] = {
        "attempts": len(records), "fresh_successes": n,
        "path_pass": sum(p["path_pass"] for p in pred_all),
        "psi0": sum(p["psi_pass"].get("0", False) for p in pred_all),
        "psi5": sum(p["psi_pass"].get("5", False) for p in pred_all),
        "psi10": sum(p["psi_pass"].get("10", False) for p in pred_all),
        "lost_normal_cases": sum(p["lost_normal"] > 0 for p in pred_all),
        "lost_normal_words": sum(p["lost_normal"] for p in pred_all),
        "lost_fault_cases": sum(p["lost_fault"] > 0 for p in pred_all),
        "lost_fault_words": sum(p["lost_fault"] for p in pred_all),
        "undetermined_cases": sum(p["undetermined"] > 0 for p in pred_all),
    }
    for name in ("path_pass", "psi0", "psi5", "psi10"):
        summary["all"][f"{name}_rate_successes"] = round(summary["all"][name] / n, 6)
        summary["all"][f"{name}_rate_attempts"] = round(summary["all"][name] / len(records), 6)

    common = {eid for eid in ids if all(byid.get((eid, m), {}).get("fresh_success") for m in METHODS)}
    summary["paired"] = {"common_evaluations": len(common), "methods": {}}
    for method in METHODS:
        rows = [byid[(eid, method)] for eid in common if "predicate" in byid[(eid, method)]]
        pred = [r["predicate"] for r in rows]
        summary["paired"]["methods"][method] = {
            "n": len(rows),
            "path_pass": sum(p["path_pass"] for p in pred),
            "psi0": sum(p["psi_pass"].get("0", False) for p in pred),
            "psi5": sum(p["psi_pass"].get("5", False) for p in pred),
            "psi10": sum(p["psi_pass"].get("10", False) for p in pred),
        }
    common_original = [eid for eid in common
        if all(original[(eid, m)]["status"] == "VERIFIED_SUCCESS" for m in METHODS)]
    summary["paired"]["common_original_success_evaluations"] = len(common_original)
    summary["paired"]["original_success_methods"] = {}
    for method in METHODS:
        summary["paired"]["original_success_methods"][method] = cohort_stats(
            [byid[(eid, method)] for eid in common_original])
    summary["paired"]["discordant_fresh_common"] = {
        metric: sum(len({byid[(eid, m)]["predicate"][metric] if metric == "path_pass"
                         else byid[(eid, m)]["predicate"]["psi_pass"][metric[-1]]
                         for m in METHODS}) > 1 for eid in common)
        for metric in ("path_pass", "psi0", "psi5", "psi10")
    }

    for regime in ("full", "sampled"):
        rows = [r for r in records if r.get("fresh_success") and "predicate" in r
                and r.get("reference", {}).get("regime") == regime]
        pred = [r["predicate"] for r in rows]
        summary["path_regimes"][regime] = {
            "n": len(rows),
            "path_pass": sum(p["path_pass"] for p in pred),
            "psi0": sum(p["psi_pass"].get("0", False) for p in pred),
            "psi5": sum(p["psi_pass"].get("5", False) for p in pred),
            "psi10": sum(p["psi_pass"].get("10", False) for p in pred),
        }
    summary["unresolved"] = {
        "infra_timeout_or_error": sum(r.get("status") == "INFRA_TIMEOUT_OR_ERROR" for r in records),
        "originally_success_compute_limit": sum(
            original[(r["evaluation_id"], r["method"])]["status"] == "VERIFIED_SUCCESS"
            and r.get("status") == "INFRA_TIMEOUT_OR_ERROR" for r in records),
        "other_compute_limit": sum(
            original[(r["evaluation_id"], r["method"])]["status"] != "VERIFIED_SUCCESS"
            and r.get("status") == "INFRA_TIMEOUT_OR_ERROR" for r in records),
        "true_reconstruction_mismatch": sum(
            original[(r["evaluation_id"], r["method"])]["status"] == "VERIFIED_SUCCESS"
            and not r.get("reconstruction", {}).get("hash_match")
            and r.get("status") != "INFRA_TIMEOUT_OR_ERROR" for r in records),
    }
    (OUT / "statistics.json").write_text(json.dumps(summary, indent=2) + "\n")

    # Flat table used by the manuscript: one row per method/tier/denominator.
    with (OUT / "FINAL_TASK_PRESERVATION_STATISTICS.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["scope", "method", "metric", "numerator", "denominator", "rate"])
        for method in METHODS:
            entry = summary["methods"][method]
            for metric in ("path_pass", "psi0", "psi5", "psi10"):
                writer.writerow(["fresh_successes", method, metric,
                                 entry[metric], entry["predicate_checked"],
                                 entry[f"{metric}_rate_successes"]])
                writer.writerow(["attempts", method, metric,
                                 entry[metric], entry["attempts"], entry[f"{metric}_rate_attempts"]])
        for metric in ("path_pass", "psi0", "psi5", "psi10"):
            writer.writerow(["fresh_successes", "ALL", metric, summary["all"][metric], n,
                             summary["all"][f"{metric}_rate_successes"]])
            writer.writerow(["attempts", "ALL", metric, summary["all"][metric], len(records),
                             summary["all"][f"{metric}_rate_attempts"]])
        for cohort_name, cohort in summary["cohorts"].items():
            for metric in ("path_pass", "psi0", "psi5", "psi10"):
                writer.writerow([cohort_name, "ALL", metric, cohort[metric], cohort["n"],
                                 round(cohort[metric] / cohort["n"], 6) if cohort["n"] else None])
            for method, method_cohort in cohort["by_method"].items():
                for metric in ("path_pass", "psi0", "psi5", "psi10"):
                    writer.writerow([cohort_name, method, metric, method_cohort[metric], method_cohort["n"],
                                     round(method_cohort[metric] / method_cohort["n"], 6) if method_cohort["n"] else None])

        for regime, entry in summary["path_regimes"].items():
            for metric in ("path_pass", "psi0", "psi5", "psi10"):
                writer.writerow([f"reference_{regime}", "ALL", metric, entry[metric], entry["n"],
                                 round(entry[metric] / entry["n"], 6) if entry["n"] else None])
        for method, entry in summary["paired"]["methods"].items():
            for metric in ("path_pass", "psi0", "psi5", "psi10"):
                writer.writerow(["paired_fresh_common", method, metric, entry[metric], entry["n"],
                                 round(entry[metric] / entry["n"], 6) if entry["n"] else None])
        for method, entry in summary["paired"]["original_success_methods"].items():
            for metric in ("path_pass", "psi0", "psi5", "psi10"):
                writer.writerow(["paired_original_success", method, metric, entry[metric], entry["n"],
                                 round(entry[metric] / entry["n"], 6) if entry["n"] else None])

    print(json.dumps({"records": len(records), "unique_evaluations": summary["coverage"]["unique_evaluations"],
                      "all": summary["all"], "paired": summary["paired"]}, indent=2))


if __name__ == "__main__":
    main()

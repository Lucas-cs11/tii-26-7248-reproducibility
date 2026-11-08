import json
p = "experiment/h_sensitivity_config.json"
d = json.load(open(p))
d["timeout_seconds_per_analysis"] = 900
d["threshold_case_timeout_seconds"] = 36000
json.dump(d, open(p, "w"), indent=2)
print("budgets:", d["timeout_seconds_per_analysis"], d["threshold_case_timeout_seconds"])

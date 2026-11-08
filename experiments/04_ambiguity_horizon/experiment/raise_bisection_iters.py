import json
p = "experiment/h_sensitivity_config.json"
d = json.load(open(p))
print("old bisection_iterations:", d.get("threshold_bisection_iterations"))
d["threshold_bisection_iterations"] = 20
# the 6 bisection models are heavy: give the verdict runs room
d["timeout_seconds_per_analysis"] = 900
d["threshold_case_timeout_seconds"] = 36000
json.dump(d, open(p, "w"), indent=2)
print("new:", d["threshold_bisection_iterations"], d["timeout_seconds_per_analysis"], d["threshold_case_timeout_seconds"])

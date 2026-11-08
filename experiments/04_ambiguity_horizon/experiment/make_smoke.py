import csv, sys
n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
rows = list(csv.DictReader(open("cohorts/shard_000.csv")))
with open("cohorts/smoke.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows[:n])
print(f"smoke cohort: {min(n, len(rows))} rows")

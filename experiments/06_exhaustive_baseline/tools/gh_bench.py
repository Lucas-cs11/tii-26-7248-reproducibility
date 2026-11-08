#!/usr/bin/env python3
"""Runner-speed benchmark for GitHub Actions calibration.

Prints a JSON line with the wall time of two fixed CPU workloads so the
per-case computation budget (verify 120 s / repair 300 s on the reference
Apple M4 machine) can be re-scaled for the runner.

Reference values measured on the M4 development machine:
    loop20m_s   = 0.87   (mean of 3)
    lp_smoke_s  = see below (filled at runtime)
"""
import json
import time
import platform


def loop20m() -> float:
    t = time.perf_counter()
    s = 0
    for i in range(20_000_000):
        s += i
    return time.perf_counter() - t


def lp_smoke() -> float:
    """A small but representative scipy/HiGHS LP workload."""
    import numpy as np
    from scipy.optimize import linprog
    rng = np.random.default_rng(0)
    t = time.perf_counter()
    n = 0
    for _ in range(200):
        A = rng.random((8, 6))
        b = rng.random(8) + 1.0
        c = rng.random(6)
        linprog(c, A_ub=A, b_ub=b, bounds=[(0, None)] * 6, method="highs")
        n += 1
    return (time.perf_counter() - t) / n


def main() -> None:
    import sys
    l1 = loop20m()
    l2 = loop20m()
    lp = lp_smoke()
    out = {
        "runner": platform.platform(),
        "python": platform.python_version(),
        "loop20m_s": round(min(l1, l2), 4),
        "lp_ms_per_solve": round(lp * 1000, 3),
        "ref_m4_loop20m_s": 0.87,
        "loop_ratio_vs_m4": round(min(l1, l2) / 0.87, 3),
    }
    print("BENCH " + json.dumps(out), flush=True)
    print(f"::notice::loop20m={out['loop20m_s']}s ratio_vs_M4={out['loop_ratio_vs_m4']}x "
          f"lp={out['lp_ms_per_solve']}ms/solve", flush=True)


if __name__ == "__main__":
    main()

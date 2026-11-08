"""Non-trivial task-preservation predicate for R3-2 (independent verification).

Reference set: distinct certificate normal/fault words of N0.  Selection is
deterministic (SHA-256 keyed by evaluation id), K=3 per class for large
certificate sets; the full set is used when it is small (<=32 words).
Path condition: each selected word must stay timed-feasible in the candidate.
Performance condition: earliest completion of each selected normal word may not
exceed its N0 baseline by more than the tier tolerance (0, 5%, 10% of baseline;
absolute 0 when the baseline is 0).
"""
from __future__ import annotations
import hashlib, json
from fractions import Fraction

def _word(cert, cls):
    w = getattr(cert, "sigma_N" if cls == "N" else "sigma_F", None)
    if w is None and isinstance(cert, dict):
        w = cert.get("sigma_N" if cls == "N" else "sigma_F")
    return tuple(w)

def select_reference(evaluation_id, certificates, K=3, full_threshold=32):
    normal = sorted({_word(c, "N") for c in certificates})
    fault = sorted({_word(c, "F") for c in certificates})
    def ranked(words, cls):
        return sorted(words, key=lambda w: hashlib.sha256(
            f"{evaluation_id}|{cls}|{','.join(w)}".encode()).hexdigest())
    full = (len(normal) <= full_threshold and len(fault) <= full_threshold)
    return {
        "regime": "full" if full else "sampled",
        "K": K,
        "normal": normal if full else ranked(normal, "N")[:K],
        "fault": fault if full else ranked(fault, "F")[:K],
        "n_normal_available": len(normal),
        "n_fault_available": len(fault),
    }

def baseline_times(tpn, H, reference, compute_iv):
    out = {"normal": {}, "fault": {}, "undetermined": []}
    for word in reference["normal"]:
        try:
            iv = compute_iv(tpn, word, H)
        except Exception:
            iv = None
        if iv is None:
            out["undetermined"].append({"class": "normal", "word": list(word), "why": "baseline_infeasible_or_error"})
        else:
            out["normal"][word] = iv
    for word in reference["fault"]:
        try:
            iv = compute_iv(tpn, word, H)
        except Exception:
            iv = None
        if iv is None:
            out["undetermined"].append({"class": "fault", "word": list(word), "why": "baseline_infeasible_or_error"})
        else:
            out["fault"][word] = iv
    return out

def evaluate(candidate, H, reference, baseline, compute_iv, tiers=("0", "5", "10")):
    """Evaluate psi_path and psi_perf on candidate.  Returns a JSON-able dict."""
    lost_normal, lost_fault, undetermined = [], [], []
    normal_rows, fault_rows = [], []
    for word in reference["normal"]:
        try:
            iv = compute_iv(candidate, word, H)
        except Exception:
            iv = None
        if iv is None:
            lost_normal.append(list(word)); normal_rows.append({"word": list(word), "status": "LOST"})
            continue
        base = baseline["normal"].get(word)
        if base is None:
            undetermined.append({"class": "normal", "word": list(word), "why": "no_baseline"})
            normal_rows.append({"word": list(word), "status": "NO_BASELINE"}); continue
        t0, t1 = base
        trend = {"word": list(word), "status": "RETAINED", "t_min": str(iv[0]), "t_min_base": str(t0), "delta": str(iv[0] - t0)}
        for tier in tiers:
            if tier == "0" or t0 == 0:
                tol = Fraction(0)
            else:
                tol = Fraction(int(tier), 100) * t0
            trend[f"tier_{tier}"] = bool(iv[0] <= t0 + tol)
        normal_rows.append(trend)
    for word in reference["fault"]:
        try:
            iv = compute_iv(candidate, word, H)
        except Exception:
            iv = None
        if iv is None:
            lost_fault.append(list(word)); fault_rows.append({"word": list(word), "status": "LOST"})
        else:
            fault_rows.append({"word": list(word), "status": "RETAINED", "t_min": str(iv[0])})
    perf = {tier: all(row.get(f"tier_{tier}", False) for row in normal_rows if row.get("status") == "RETAINED")
            if any(row.get("status") == "RETAINED" for row in normal_rows) else False for tier in tiers}
    path_pass = not lost_normal and not lost_fault
    return {
        "path_pass": path_pass,
        "lost_normal": lost_normal,
        "lost_fault": lost_fault,
        "undetermined": undetermined,
        "perf_tiers": perf,
        "psi_pass": {tier: bool(path_pass and perf[tier] and not undetermined) for tier in tiers},
        "normal_rows": normal_rows,
        "fault_rows": fault_rows,
    }

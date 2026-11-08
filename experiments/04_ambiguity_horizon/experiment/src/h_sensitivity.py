from __future__ import annotations

import hashlib
import json
import math
import time
from collections import deque
from dataclasses import dataclass
from typing import Optional

from .exact_confirmation.lp_solver import (
    LPStatus,
    compute_min_completion_time,
    confirm_ambiguity,
)
from .model.tpn import TPN
from .scg.builder import build_scg
from .synchronizer.builder import (
    SyncState,
    build_synchronizer,
    reach_F,
    reach_N,
    synchronizer_transition,
)
from .temporal_expansion.builder import build_expansion
from .verifier import verify


@dataclass
class CompletionWords:
    normal: list[tuple[str, ...]]
    faulty: list[tuple[str, ...]]
    candidates: list[tuple[str, ...]]
    states: int


def direct_ambiguity_threshold(
    tpn: TPN,
    L: int,
    H_upper: float,
    budget: Optional[int] = None,
) -> dict:
    started = time.perf_counter()
    stats = {
        "candidate_words": 0,
        "candidate_words_processed": 0,
        "temporal_states": 0,
        "trace_records": 0,
        "terminal_normal_records": 0,
        "terminal_faulty_records": 0,
        "terminal_pair_candidates": 0,
        "enclosure_rejected_pairs": 0,
        "threshold_bound_pruned_pairs": 0,
        "terminal_pairs": 0,
        "lp_calls": 0,
        "confirmed_critical_pairs": 0,
        "runtime_total": 0.0,
    }
    scg = build_scg(tpn)
    if not scg.completion_ids:
        return _direct_failure("COMPLETION_UNREACHABLE", stats, started)
    if scg.has_zero_time_unobservable_cycle:
        return _direct_failure("ZERO_TIME_UNOBSERVABLE_CYCLE", stats, started)
    if scg.scg_state_limit_reached:
        return _direct_failure("SCG_STATE_LIMIT", stats, started)

    sync = build_synchronizer(tpn, scg.build_truncated(), L)
    stats["candidate_words"] = len(sync.candidate_words)
    best = None
    critical = None
    solver_unknown = False

    for word in sync.candidate_words:
        expansion = build_expansion(tpn, word, H_upper, budget=budget)
        stats["candidate_words_processed"] += 1
        if expansion == "INC":
            return _direct_failure("BUDGET_EXHAUSTED", stats, started)
        stats["temporal_states"] += len(expansion.nodes)
        stats["trace_records"] += sum(len(records) for records in expansion.records.values())
        stats["terminal_normal_records"] += len(expansion.terminal_normal)
        stats["terminal_faulty_records"] += len(expansion.terminal_faulty)
        stats["terminal_pair_candidates"] += (
            len(expansion.terminal_normal) * len(expansion.terminal_faulty)
        )

        pairs = []
        for _, normal in expansion.terminal_normal:
            for _, faulty in expansion.terminal_faulty:
                lower = max(normal.J_hat[0], faulty.J_hat[0])
                upper = _minimum_bound(normal.J_hat[1], faulty.J_hat[1])
                if _less_than_bound(upper, lower):
                    stats["enclosure_rejected_pairs"] += 1
                    continue
                pairs.append((float(lower), normal, faulty))

        for lower, normal, faulty in sorted(pairs, key=lambda item: item[0]):
            if best is not None and lower >= best - 1.0e-9:
                stats["threshold_bound_pruned_pairs"] += 1
                continue
            stats["terminal_pairs"] += 1
            stats["lp_calls"] += 1
            result = confirm_ambiguity(tpn, normal.sigma, faulty.sigma, H_upper)
            if result is None:
                continue
            if result.get("status") == "SOLVER_UNKNOWN":
                solver_unknown = True
                continue
            stats["confirmed_critical_pairs"] += 1
            threshold = float(result["overlap"][0])
            if best is not None and threshold >= best:
                continue
            best = threshold
            critical = (word, normal.sigma, faulty.sigma, result["overlap"])

    stats["runtime_total"] = time.perf_counter() - started
    if solver_unknown:
        return {
            "status": "INCOMPLETE_ENUMERATION",
            "verdict": "INC",
            "enumeration_complete": False,
            "inconclusive_reason": "SOLVER_UNKNOWN",
            "stats": stats,
        }
    if critical is None:
        return {
            "status": "NOT_AMBIGUOUS_AT_UPPER_BOUND",
            "verdict": "VER",
            "enumeration_complete": True,
            "inconclusive_reason": None,
            "stats": stats,
        }

    pair_payload = json.dumps(
        [critical[0], critical[1], critical[2]],
        separators=(",", ":"),
    )
    return {
        "status": "OPTIMAL",
        "verdict": "AMB",
        "enumeration_complete": True,
        "H_amb_star": best,
        "critical_pair_id": hashlib.sha256(pair_payload.encode()).hexdigest()[:20],
        "observable_word": critical[0],
        "normal_sequence": critical[1],
        "faulty_sequence": critical[2],
        "critical_overlap_max": float(critical[3][1]),
        "stats": stats,
    }


def _direct_failure(reason: str, stats: dict, started: float) -> dict:
    stats["runtime_total"] = time.perf_counter() - started
    return {
        "status": "INCOMPLETE_ENUMERATION",
        "verdict": "INC",
        "enumeration_complete": False,
        "inconclusive_reason": reason,
        "stats": stats,
    }


def _minimum_bound(a, b):
    if math.isinf(a):
        return b
    if math.isinf(b):
        return a
    return min(a, b)


def _less_than_bound(a, b) -> bool:
    if math.isinf(a):
        return False
    if math.isinf(b):
        return True
    return a < b


def validate_threshold(
    tpn: TPN,
    L: int,
    H_star: float,
    H_base: float,
    epsilon_ratio: float,
    budget: Optional[int] = None,
) -> dict:
    epsilon = max(H_base * epsilon_ratio, 1.0e-7)
    H_minus = max(0.0, H_star - epsilon)
    H_plus = H_star + epsilon
    below = verify(tpn, L, H_minus, budget=budget)
    above = verify(tpn, L, H_plus, budget=budget)
    return {
        "epsilon": epsilon,
        "H_minus": H_minus,
        "H_plus": H_plus,
        "below_verdict": below["result"],
        "below_status": below.get("inconclusive_reason"),
        "above_verdict": above["result"],
        "above_status": above.get("inconclusive_reason"),
        "pass": below["result"] == "VER" and above["result"] == "AMB",
    }


def bisection_ambiguity_threshold(
    tpn: TPN,
    L: int,
    H_base: float,
    iterations: int,
    budget: Optional[int] = None,
) -> dict:
    lower_ratio = 0.0
    upper_ratio = 0.5
    lower = verify(tpn, L, 0.0, budget=budget)
    upper = verify(tpn, L, upper_ratio * H_base, budget=budget)
    if upper["result"] != "AMB":
        return {
            "status": "UPPER_BOUND_NOT_AMBIGUOUS",
            "lower_verdict": lower["result"],
            "upper_verdict": upper["result"],
        }
    if lower["result"] == "AMB":
        return {
            "status": "THRESHOLD_AT_ZERO",
            "lower_ratio": 0.0,
            "upper_ratio": 0.0,
            "H_amb_star": 0.0,
        }
    if lower["result"] == "INC":
        return {
            "status": "LOWER_BOUND_INCONCLUSIVE",
            "lower_verdict": lower["result"],
            "upper_verdict": upper["result"],
        }

    for _ in range(iterations):
        middle_ratio = (lower_ratio + upper_ratio) / 2
        middle = verify(tpn, L, middle_ratio * H_base, budget=budget)
        if middle["result"] == "INC":
            return {
                "status": "MIDPOINT_INCONCLUSIVE",
                "lower_ratio": lower_ratio,
                "upper_ratio": upper_ratio,
                "midpoint_ratio": middle_ratio,
            }
        if middle["result"] == "AMB":
            upper_ratio = middle_ratio
            continue
        lower_ratio = middle_ratio

    return {
        "status": "INTERVAL",
        "lower_ratio": lower_ratio,
        "upper_ratio": upper_ratio,
        "H_amb_star": upper_ratio * H_base,
    }


def completion_profile(
    tpn: TPN,
    L: int,
    H: float,
    verdict: str,
    budget: Optional[int] = None,
    compute_minima: bool = False,
) -> dict:
    scg = build_scg(tpn)
    if not scg.completion_ids:
        return _unavailable_completion("COMPLETION_UNREACHABLE")
    if scg.has_zero_time_unobservable_cycle:
        return _unavailable_completion("ZERO_TIME_UNOBSERVABLE_CYCLE")
    if scg.scg_state_limit_reached:
        return _unavailable_completion("SCG_STATE_LIMIT")

    sync = build_synchronizer(tpn, scg.build_truncated(), L)
    expansion = build_expansion(
        tpn,
        (),
        H,
        budget=budget,
        accept_any_observation=True,
        stop_when_both_classes_complete=True,
        max_observations=L,
    )
    if expansion == "INC":
        return _unavailable_completion("BUDGET_EXHAUSTED")
    normal_sequences = {
        record.sigma for _, record in expansion.terminal_normal
    }
    faulty_sequences = {
        record.sigma for _, record in expansion.terminal_faulty
    }

    normal_min, normal_nonoptimal = (
        _minimum_completion(tpn, normal_sequences, H)
        if compute_minima
        else (None, 0)
    )
    faulty_min, faulty_nonoptimal = (
        _minimum_completion(tpn, faulty_sequences, H)
        if compute_minima
        else (None, 0)
    )
    normal_exists = bool(normal_sequences)
    faulty_exists = bool(faulty_sequences)
    return {
        "status": "COMPLETE",
        "completion_state": _completion_state(normal_exists, faulty_exists, verdict),
        "normal_complete_exists": normal_exists,
        "faulty_complete_exists": faulty_exists,
        "H_comp_normal": normal_min,
        "H_comp_faulty": faulty_min,
        "completion_minima_status": "COMPUTED" if compute_minima else "UNAVAILABLE_COST_GUARD",
        "normal_complete_sequences": len(normal_sequences),
        "faulty_complete_sequences": len(faulty_sequences),
        "normal_completion_words": None,
        "faulty_completion_words": None,
        "structural_candidate_words": len(sync.candidate_words),
        "completion_sync_states": len(sync.states),
        "completion_temporal_states": len(expansion.nodes),
        "completion_trace_records": sum(
            len(records) for records in expansion.records.values()
        ),
        "completion_lp_nonoptimal": normal_nonoptimal + faulty_nonoptimal,
    }


def collect_completion_words(tpn: TPN, scg, L: int) -> CompletionWords:
    initial_state = SyncState(
        X_N=reach_N(scg, tpn, frozenset({scg.initial_id}), ""),
        X_F=reach_F(scg, tpn, frozenset({scg.initial_id}), ""),
    )
    states = {initial_state.key(): initial_state}
    queue = deque([((), initial_state.key())])
    normal: list[tuple[str, ...]] = []
    faulty: list[tuple[str, ...]] = []
    candidates: list[tuple[str, ...]] = []

    while queue:
        word, key = queue.popleft()
        state = states[key]
        normal_complete = bool(state.X_N & scg.completion_ids)
        faulty_complete = bool(state.X_F & scg.completion_ids)
        if normal_complete:
            normal.append(word)
        if faulty_complete:
            faulty.append(word)
        if normal_complete and faulty_complete:
            candidates.append(word)
        if len(word) >= L or (not state.X_N and not state.X_F):
            continue

        for label in sorted(tpn.observable_alphabet):
            next_state = synchronizer_transition(scg, tpn, state, label)
            if not next_state.X_N and not next_state.X_F:
                continue
            next_key = next_state.key()
            if next_key not in states:
                states[next_key] = next_state
            queue.append((word + (label,), next_key))

    return CompletionWords(
        normal=normal,
        faulty=faulty,
        candidates=candidates,
        states=len(states),
    )


def _minimum_completion(
    tpn: TPN,
    sequences: set[tuple[str, ...]],
    H: float,
) -> tuple[Optional[float], int]:
    values: list[float] = []
    nonoptimal = 0
    for sequence in sequences:
        result = compute_min_completion_time(tpn, sequence, H)
        if result.status == LPStatus.OPTIMAL:
            values.append(result.value)
            continue
        nonoptimal += 1
    return (min(values) if values else None, nonoptimal)


def _completion_state(normal_exists: bool, faulty_exists: bool, verdict: str) -> str:
    if not normal_exists and not faulty_exists:
        return "NO_COMPLETE_RUN"
    if normal_exists and not faulty_exists:
        return "NORMAL_ONLY"
    if faulty_exists and not normal_exists:
        return "FAULTY_ONLY"
    if verdict == "AMB":
        return "AMBIGUOUS"
    return "BOTH_CLASSES_DISTINGUISHABLE"


def _unavailable_completion(reason: str) -> dict:
    return {
        "status": "UNAVAILABLE",
        "completion_state": "UNAVAILABLE",
        "normal_complete_exists": None,
        "faulty_complete_exists": None,
        "H_comp_normal": None,
        "H_comp_faulty": None,
        "reason": reason,
    }

"""Versioned entry point for the semantics-corrected v6 benchmark families."""
from __future__ import annotations

from typing import Tuple

from .legacy_families import FAMILY_SPECS, generate_legacy_model
from ..model.tpn import TPN


def generate_family_model(v6_family: str, seed: int, **overrides) -> Tuple[TPN, int, float, dict]:
    """Generate a model without reusing any v5 result identity."""
    tpn, default_l, default_h, attributes = generate_legacy_model(
        v6_family, seed, **overrides
    )
    attributes = dict(attributes)
    attributes.update({
        "benchmark_version": "v6",
        "generator_semantics": "strong-time-corrected-immediate-route-choice",
        "benchmark_family": v6_family,
    })
    return tpn, default_l, default_h, attributes

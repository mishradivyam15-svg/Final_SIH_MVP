"""
Deterministic SIF-potential and IOGP Life-Saving Rule classification.

Implements the "high-energy hazard + uncontrolled exposure" precursor
definition used by the DEKRA / EEI Serious Injury and Fatality (SIF)
research the OIL problem statement itself cites: incidents involving a
recognized high-energy source are the ones that correlate with fatality
potential, regardless of the incident's actual outcome severity.
Low-energy hazards (e.g. a same-level slip/trip/fall) are excluded even
when frequent, since frequency and fatality potential diverge (DEKRA /
Martin & Black 2015 — non-fatal incidents fell 51% over 15 years while
fatalities fell only 25.5%).

This module is a pure, deterministic post-processor over already
extracted signals (hazard / exposure / barrier_failure). It does not
call the ML model and has no effect on hazard/exposure predictions —
it only interprets their output.
"""

from __future__ import annotations

# High-energy hazard sources, per the DEKRA/EEI SIF-precursor energy
# model. Hazards outside this set (currently only same-level
# slip/trip/fall) are treated as low-energy.
HIGH_ENERGY_HAZARDS = frozenset({
    "working_at_height",
    "moving_machinery",
    "mobile_equipment",
    "electrical_energy",
    "excavation",
    "falling_object",
    "line_of_fire",
    "lifting_operation",
    "stored_energy",
    "confined_space",
    "fire_or_hot_work",
    "hydrocarbon_or_process_hazard",
    "chemical_exposure",
})

# hazard -> IOGP Life-Saving Rule. Only hazard categories with a genuine
# 1:1 correspondence are mapped; everything else is left unmapped
# rather than forced onto the nearest rule. Three of IOGP's nine rules
# — Bypassing Safety Controls, Work Authorization, and Driving — have
# no corresponding hazard category in the current extraction taxonomy
# and are intentionally never emitted by this mapping.
IOGP_RULE_MAP: dict[str, str] = {
    "working_at_height": "Working at Height",
    "confined_space": "Confined Space",
    "fire_or_hot_work": "Hot Work",
    "line_of_fire": "Line of Fire",
    "electrical_energy": "Energy Isolation",
    "stored_energy": "Energy Isolation",
    "lifting_operation": "Safe Mechanical Lifting",
}

# Severity label -> normalized 0-1 score, consumed by
# ai.prioritization's barrier-failure-severity component.
SEVERITY_SCORE: dict[str, float] = {"high": 1.0, "medium": 0.5, "low": 0.15}


def _normalize_key(value: str | None) -> str | None:
    """Accept either raw snake_case tokens or title-cased display text."""
    if not value:
        return None
    return value.strip().lower().replace(" ", "_")


def classify_sif(
    hazard: str | None,
    exposure: str | None,
    barrier_failure: str | None,
) -> dict[str, object]:
    """
    Derive SIF-potential and IOGP Life-Saving Rule tag from already
    extracted signals.

    Args:
        hazard, exposure, barrier_failure: extracted signal values, as
            either raw snake_case tokens (e.g. "working_at_height") or
            title-cased display text (e.g. "Working At Height").

    Returns:
        {
            "sif_potential": bool | None,
            "severity_potential": "high" | "medium" | "low" | None,
            "iogp_life_saving_rule": str | None,
        }

        All three are None when no hazard was detected — there is no
        evidence to classify from, so we do not guess.
    """
    hazard_key = _normalize_key(hazard)

    if hazard_key is None:
        return {
            "sif_potential": None,
            "severity_potential": None,
            "iogp_life_saving_rule": None,
        }

    is_high_energy = hazard_key in HIGH_ENERGY_HAZARDS
    has_exposure_evidence = bool(exposure) or bool(barrier_failure)

    if is_high_energy and has_exposure_evidence:
        # High-energy source AND a confirmed exposure pathway / failed
        # barrier — the classic SIF-precursor definition.
        severity = "high"
    elif is_high_energy:
        # High-energy source present, but no confirmed direct exposure
        # or barrier failure yet.
        severity = "medium"
    else:
        severity = "low"

    return {
        "sif_potential": severity in ("high", "medium"),
        "severity_potential": severity,
        "iogp_life_saving_rule": IOGP_RULE_MAP.get(hazard_key),
    }

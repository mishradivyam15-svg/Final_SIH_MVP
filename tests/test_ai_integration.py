"""Offline end-to-end AI ↔ backend integration tests."""

import json

from ai.clustering import ClusterEngine
from ai.prioritization import PrecursorEngine
from ai.relationship import RelationshipEngine
from ai.relationship_graph import RelationshipGraph


class DeterministicEmbeddingService:
    """Small deterministic embedding substitute for offline integration tests."""

    @staticmethod
    def embed_text(narrative):
        if narrative is None:
            return None

        text = narrative.casefold()

        if "electrical" in text or "energized" in text:
            return "electrical"

        return "maintenance"

    @staticmethod
    def cosine_similarity(first, second):
        if first is None or second is None:
            return 0.0

        return 1.0 if first == second else 0.0


def safety_report(
    report_id,
    *,
    timestamp="2026-01-10T09:00:00",
    site="Site-A",
    narrative=(
        "Worker entered a restricted maintenance area without authorization."
    ),
    hazard="working_at_height",
    activity="maintenance",
    equipment="ladder",
    barrier_failure="fall_protection_missing",
    exposure="elevated work area",
    severity_potential=0.6,
):
    """Create deterministic representative SafetyReport data."""

    return {
        "report_id": report_id,
        "timestamp": timestamp,
        "site": site,
        "source_type": "prototype",
        "narrative": narrative,
        "hazard": hazard,
        "activity": activity,
        "equipment": equipment,
        "barrier_failure": barrier_failure,
        "exposure": exposure,
        "severity_potential": severity_potential,
    }


def test_two_report_relationship_flow():
    """Verify SafetyReport → RelationshipResult → JSON."""

    reports = [
        safety_report("R001"),
        safety_report(
            "R002",
            timestamp="2026-01-12T09:00:00",
            narrative=(
                "Technician accessed the controlled maintenance zone "
                "without clearance."
            ),
        ),
    ]

    engine = RelationshipEngine(DeterministicEmbeddingService())

    result = engine.compare(reports[0], reports[1])

    assert result.source_report_id == "R001"
    assert result.target_report_id == "R002"
    assert result.is_related is True

    assert 0.0 <= result.semantic_similarity <= 1.0
    assert 0.0 <= result.hazard_match <= 1.0
    assert 0.0 <= result.activity_match <= 1.0
    assert 0.0 <= result.barrier_match <= 1.0
    assert 0.0 <= result.site_match <= 1.0
    assert 0.0 <= result.temporal_relation <= 1.0
    assert 0.0 <= result.relationship_strength <= 1.0

    assert result.evidence
    assert any("hazard" in item.lower() for item in result.evidence)
    assert any("temporal" in item.lower() or "days apart" in item.lower()
               for item in result.evidence)

    payload = result.as_dict()

    assert isinstance(payload, dict)
    assert json.loads(json.dumps(payload)) == payload


def test_multi_report_graph_grouping_and_precursor_flow():
    """Verify reports → graph → precursor group → priority output → JSON."""

    report_a = safety_report("R001")

    report_b = safety_report(
        "R002",
        timestamp="2026-01-12T09:00:00",
        narrative=(
            "Technician accessed the controlled maintenance zone "
            "without clearance."
        ),
    )

    report_c = safety_report(
        "R003",
        timestamp="2026-07-10T09:00:00",
        narrative="Electrical maintenance was performed on an energized panel.",
        hazard="electrical_energy",
        activity="electrical_work",
        equipment="electrical_panel",
        barrier_failure="lockout_missing",
        site="Site-B",
        exposure="energized equipment",
        severity_potential=0.9,
    )

    reports = [report_a, report_b, report_c]
    reports_by_id = {report["report_id"]: report for report in reports}

    relationship_engine = RelationshipEngine(
        DeterministicEmbeddingService()
    )

    graph = RelationshipGraph(relationship_engine).build(reports)

    assert graph.nodes == ("R001", "R002", "R003")

    # R001 and R002 are related.
    assert graph.get_edge("R001", "R002") is not None

    # R003 represents a different safety context.
    assert graph.get_edge("R001", "R003") is None
    assert graph.get_edge("R002", "R003") is None

    assert graph.neighbors("R001") == ["R002"]
    assert graph.neighbors("R002") == ["R001"]
    assert graph.neighbors("R003") == []

    graph_payload = graph.to_dict()

    assert isinstance(graph_payload, dict)
    assert len(graph_payload["nodes"]) == 3
    assert len(graph_payload["edges"]) == 1
    assert json.loads(json.dumps(graph_payload)) == graph_payload

    cluster_engine = ClusterEngine()
    grouping_result = cluster_engine.group(graph)

    assert len(grouping_result.groups) == 1

    group = grouping_result.groups[0]

    assert group.precursor_id == "P001"
    assert group.report_ids == ("R001", "R002")
    assert len(group.supporting_edges) == 1

    grouping_payload = grouping_result.to_dict()

    assert json.loads(json.dumps(grouping_payload)) == grouping_payload

    precursor_engine = PrecursorEngine()
    precursor_results = precursor_engine.summarize_all(
        grouping_result,
        reports_by_id,
    )

    assert len(precursor_results) == 1

    precursor = precursor_results[0]

    assert precursor.precursor_id == "P001"
    assert precursor.report_ids == ("R001", "R002")
    assert precursor.common_hazard == "working_at_height"
    assert precursor.common_barrier_failure == "fall_protection_missing"

    assert 0.0 <= precursor.priority_score <= 100.0
    assert precursor.priority in {"HIGH", "MEDIUM", "LOW"}
    assert precursor.evidence
    assert precursor.review_status == "pending_review"

    precursor_payload = precursor.as_dict()

    assert isinstance(precursor_payload, dict)
    assert precursor_payload["precursor_id"] == "P001"
    assert precursor_payload["report_ids"] == ["R001", "R002"]
    assert json.loads(json.dumps(precursor_payload)) == precursor_payload
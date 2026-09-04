import json

import pandas as pd

from ai.preprocessing import preprocess_report
from ai.extraction import extract_safety_signals
from ai.embeddings import EmbeddingService
from ai.relationship import RelationshipEngine
from ai.relationship_graph import RelationshipGraph
from ai.clustering import ClusterEngine
from ai.prioritization import PrecursorEngine


INPUT_FILE = "data/processed/annotation_sample.csv"


def build_reports():
    df = pd.read_csv(INPUT_FILE)

    reports = []

    for _, row in df.iterrows():
        raw_report = {
            "report_id": str(row["ID"]),
            "timestamp": row["EventDate"],
            "site": (
                f"{row['City']}, {row['State']}"
                if pd.notna(row["City"]) and pd.notna(row["State"])
                else None
            ),
            "source_type": "incident",
            "narrative": row["Final Narrative"],
        }

        preprocessed = preprocess_report(raw_report)
        extracted = extract_safety_signals(preprocessed)

        reports.append(extracted)

    return reports


def main():
    print("=" * 70)
    print("100-REPORT SAFETY PIPELINE VALIDATION - V1.1")
    print("=" * 70)

    reports = build_reports()

    print(f"Reports loaded: {len(reports)}")
    print(f"Expected unique pairs: {len(reports) * (len(reports) - 1) // 2}")

    # Relationship engine
    embedding_service = EmbeddingService()
    relationship_engine = RelationshipEngine(embedding_service)

    # Graph
    graph = RelationshipGraph(relationship_engine)
    graph.build(reports)

    print(f"Related pairs / graph edges: {len(graph.edges)}")

    # Clustering
    cluster_engine = ClusterEngine()
    grouping_result = cluster_engine.group(graph)

    print(f"Precursor groups: {len(grouping_result.groups)}")
    print(f"Ungrouped reports: {len(grouping_result.ungrouped_report_ids)}")

    # Prioritization
    reports_by_id = {
        report["report_id"]: report
        for report in reports
    }

    precursor_engine = PrecursorEngine()

    precursors = precursor_engine.summarize_all(
        grouping_result,
        reports_by_id,
    )

    print(f"Prioritized precursors: {len(precursors)}")

    print("\n" + "-" * 70)
    print("RELATED RELATIONSHIPS")
    print("-" * 70)

    for edge in graph.edges:
        print(
            f"\n{edge.source_report_id} <-> "
            f"{edge.target_report_id}"
        )

        print(
            f"Strength: {edge.relationship_strength:.3f}"
        )

        print(
            f"Semantic: {edge.semantic_similarity:.3f} | "
            f"Hazard: {edge.hazard_match:.3f} | "
            f"Activity: {edge.activity_match:.3f} | "
            f"Equipment: {edge.equipment_match:.3f} | "
            f"Exposure: {edge.exposure_match:.3f}"
        )

        print("Evidence:")

        for evidence in edge.evidence:
            print(f"  - {evidence}")

    print("\n" + "-" * 70)
    print("PRECURSOR GROUPS")
    print("-" * 70)

    for group in grouping_result.groups:
        print(
            f"\n{group.precursor_id}: "
            f"{', '.join(group.report_ids)}"
        )

        print(
            f"Supporting relationships: "
            f"{len(group.supporting_edges)}"
        )

    print("\n" + "-" * 70)
    print("PRIORITIZED PRECURSORS")
    print("-" * 70)

    for precursor in precursors:
        print(f"\n{precursor.precursor_id}")
        print(f"Title: {precursor.title}")
        print(f"Priority: {precursor.priority}")
        print(f"Score: {precursor.priority_score}/100")
        print(
            f"Reports: {', '.join(precursor.report_ids)}"
        )
        print(f"Common hazard: {precursor.common_hazard}")
        print(
            f"Common barrier: "
            f"{precursor.common_barrier_failure}"
        )
        print(f"Time window: {precursor.time_window}")

        print("Evidence:")

        for evidence in precursor.evidence:
            print(f"  - {evidence}")

    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
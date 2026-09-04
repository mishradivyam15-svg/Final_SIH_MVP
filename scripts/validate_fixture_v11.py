import json

from ai.embeddings import EmbeddingService
from ai.relationship import RelationshipEngine
from ai.relationship_graph import RelationshipGraph
from ai.clustering import ClusterEngine
from ai.prioritization import PrecursorEngine


FIXTURE_PATH = "data/processed/representative_safety_reports.json"


def main():
    with open(FIXTURE_PATH, "r", encoding="utf-8") as file:
        reports = json.load(file)

    reports_by_id = {
        report["report_id"]: report
        for report in reports
    }

    print("=" * 60)
    print("RELATIONSHIP / PRECURSOR V1.1 FIXTURE VALIDATION")
    print("=" * 60)

    print(f"Reports loaded: {len(reports)}")

    # 1. Relationship engine
    embedding_service = EmbeddingService()
    relationship_engine = RelationshipEngine(embedding_service)

    # 2. Graph
    graph = RelationshipGraph(relationship_engine)
    graph.build(reports)

    print(f"Graph nodes: {len(graph.nodes)}")
    print(f"Related pairs / graph edges: {len(graph.edges)}")

    print("\n" + "-" * 60)
    print("RELATED PAIRS")
    print("-" * 60)

    for edge in graph.edges:
        print(
            f"\n{edge.source_report_id} <-> {edge.target_report_id}"
        )
        print(f"Strength: {edge.relationship_strength:.3f}")
        print(f"Semantic: {edge.semantic_similarity:.3f}")
        print(f"Hazard: {edge.hazard_match:.3f}")
        print(f"Activity: {edge.activity_match:.3f}")
        print(f"Equipment: {edge.equipment_match:.3f}")
        print(f"Barrier: {edge.barrier_match:.3f}")
        print(f"Exposure: {edge.exposure_match:.3f}")
        print(f"Site: {edge.site_match:.3f}")
        print(f"Temporal: {edge.temporal_relation:.3f}")

        print("Evidence:")
        for evidence in edge.evidence:
            print(f"  - {evidence}")

    # 3. Clustering
    cluster_engine = ClusterEngine()
    grouping_result = cluster_engine.group(graph)

    print("\n" + "-" * 60)
    print("PRECURSOR GROUPS")
    print("-" * 60)

    print(f"Groups: {len(grouping_result.groups)}")
    print(
        f"Ungrouped reports: "
        f"{len(grouping_result.ungrouped_report_ids)}"
    )

    for group in grouping_result.groups:
        print(f"\n{group.precursor_id}")
        print(f"Reports: {', '.join(group.report_ids)}")
        print(f"Supporting edges: {len(group.supporting_edges)}")

    # 4. Prioritization
    precursor_engine = PrecursorEngine()
    precursors = precursor_engine.summarize_all(
        grouping_result,
        reports_by_id,
    )

    print("\n" + "-" * 60)
    print("PRIORITIZED PRECURSORS")
    print("-" * 60)

    print(f"Precursor outputs: {len(precursors)}")

    for precursor in precursors:
        print(f"\n{precursor.precursor_id}")
        print(f"Title: {precursor.title}")
        print(f"Priority: {precursor.priority}")
        print(f"Score: {precursor.priority_score}/100")
        print(f"Reports: {', '.join(precursor.report_ids)}")
        print(f"Common hazard: {precursor.common_hazard}")
        print(
            f"Common barrier failure: "
            f"{precursor.common_barrier_failure}"
        )
        print(f"Time window: {precursor.time_window}")

        print("Evidence:")
        for evidence in precursor.evidence:
            print(f"  - {evidence}")

    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
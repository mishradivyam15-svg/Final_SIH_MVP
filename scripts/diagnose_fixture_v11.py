import json

from ai.embeddings import EmbeddingService
from ai.relationship import RelationshipEngine
from ai.relationship_graph import RelationshipGraph


FIXTURE_PATH = "data/processed/representative_safety_reports.json"


def main():
    with open(FIXTURE_PATH, "r", encoding="utf-8") as file:
        reports = json.load(file)

    engine = RelationshipEngine(EmbeddingService())

    graph = RelationshipGraph(engine)

    # Keep ALL pairwise results for diagnosis.
    graph.build(
        reports,
        include_unrelated=True,
    )

    results = sorted(
        graph.edges,
        key=lambda result: result.relationship_strength,
        reverse=True,
    )

    print("=" * 70)
    print("V1.1 FIXTURE RELATIONSHIP DIAGNOSTICS")
    print("=" * 70)

    print(f"Reports: {len(reports)}")
    print(f"Pairwise results: {len(results)}")

    print("\nTOP 10 STRONGEST PAIRS")
    print("-" * 70)

    for index, result in enumerate(results[:10], start=1):
        print(
            f"\n#{index} "
            f"{result.source_report_id} <-> "
            f"{result.target_report_id}"
        )

        print(
            f"Strength={result.relationship_strength:.3f} | "
            f"Related={result.is_related}"
        )

        print(
            f"semantic={result.semantic_similarity:.3f} | "
            f"hazard={result.hazard_match:.3f} | "
            f"activity={result.activity_match:.3f} | "
            f"equipment={result.equipment_match:.3f}"
        )

        print(
            f"barrier={result.barrier_match:.3f} | "
            f"exposure={result.exposure_match:.3f} | "
            f"site={result.site_match:.3f} | "
            f"temporal={result.temporal_relation:.3f}"
        )

        print("Evidence:")

        for evidence in result.evidence:
            print(f"  - {evidence}")


if __name__ == "__main__":
    main()
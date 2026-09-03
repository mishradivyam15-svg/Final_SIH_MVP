import pandas as pd


INPUT_PATH = "data/raw/OSHA/January2015toNovember2025.csv"
OUTPUT_PATH = "data/processed/osha_candidates.csv"


EVENT_KEYWORDS = [
    # Working at height
    "fall to lower level",
    "fall from",
    
    # Line of fire / caught-between
    "caught",
    "compressed",
    "pinched",
    "entangled",
    "struck by",
    "struck against",

    # Vehicle / mobile equipment
    "vehicle",
    "forklift",

    # Electrical
    "electricity",
    "electrical",
    "electrocution",

    # Lifting
    "lifting",
    "crane",

    # Excavation
    "excavation",
    "trench",

    # Thermal / process safety
    "fire",
    "explosion",
    "chemical",
    "hot objects",
]


def build_candidate_corpus():

    df = pd.read_csv(INPUT_PATH, low_memory=False)

    event_title = (
        df["EventTitle"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.strip()
    )

    source_title = (
        df["SourceTitle"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.strip()
    )

    narrative = (
        df["Final Narrative"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    # Structured event/source information
    event_mask = event_title.str.contains(
        "|".join(EVENT_KEYWORDS),
        regex=True,
        na=False
    )

    # Additional narrative signals
    narrative_keywords = [
        "lockout",
        "tagout",
        "energized",
        "suspended load",
        "rigging",
        "sling",
        "confined space",
        "gas exposure",
        "hydrocarbon",
        "pipeline",
    ]

    narrative_mask = narrative.str.contains(
        "|".join(narrative_keywords),
        regex=True,
        na=False
    )

    # Equipment/source signals
    source_keywords = [
        "ladder",
        "scaffold",
        "crane",
        "forklift",
        "truck",
        "vehicle",
        "conveyor",
        "machinery",
        "roof",
        "pipeline",
    ]

    source_mask = source_title.str.contains(
        "|".join(source_keywords),
        regex=True,
        na=False
    )

    candidates = df[
        event_mask | narrative_mask | source_mask
    ].copy()

    # Remove exact duplicate narratives
    candidates = candidates.drop_duplicates(
        subset=["Final Narrative"]
    )

    candidates.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\nOriginal records:", len(df))
    print("Candidate records:", len(candidates))
    print(
        "Candidate percentage:",
        round(len(candidates) / len(df) * 100, 2),
        "%"
    )

    print("\nTop EventTitle categories:")
    print(
        candidates["EventTitle"]
        .value_counts()
        .head(30)
        .to_string()
    )


if __name__ == "__main__":
    build_candidate_corpus()
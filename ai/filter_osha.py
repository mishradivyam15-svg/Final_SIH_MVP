import pandas as pd


FILE_PATH = "data/raw/OSHA/January2015toNovember2025.csv"
OUTPUT_PATH = "data/processed/osha_candidates.csv"


KEYWORDS = [
    # Working at height
    "fall",
    "ladder",
    "scaffold",
    "roof",
    "elevated",
    "platform",

    # Line of fire / caught between
    "caught",
    "pinched",
    "crushed",
    "struck",
    "entangled",

    # Lifting
    "crane",
    "lifting",
    "lift",
    "rigging",
    "sling",
    "hoist",
    "suspended load",

    # Electrical
    "electrical",
    "electric",
    "energized",
    "electrocution",
    "voltage",

    # Vehicles / mobile equipment
    "forklift",
    "truck",
    "vehicle",
    "tanker",
    "tractor",
    "mobile equipment",

    # Excavation
    "excavation",
    "excavated",
    "trench",
    "trenching",
    "cave-in",

    # Confined space
    "confined space",
    "oxygen deficiency",
    "toxic gas",
    "gas exposure",

    # Maintenance / energy isolation
    "maintenance",
    "lockout",
    "lockout/tagout",
    "isolation",
    "shutdown",

    # Oil / process safety
    "pipeline",
    "hydrocarbon",
    "gas leak",
    "oil",
    "explosion",
    "fire",
    "flammable",
]


def create_candidate_corpus():

    df = pd.read_csv(FILE_PATH, low_memory=False)

    narrative = df["Final Narrative"].fillna("").str.lower()

    mask = narrative.str.contains(
        "|".join(KEYWORDS),
        regex=True,
        na=False
    )

    candidates = df[mask].copy()

    candidates.to_csv(OUTPUT_PATH, index=False)

    print("\nOriginal records:", len(df))
    print("Candidate records:", len(candidates))
    print(
        "Candidate percentage:",
        round(len(candidates) / len(df) * 100, 2),
        "%"
    )

    print("\nTop candidate EventTitle categories:")
    print(
        candidates["EventTitle"]
        .value_counts()
        .head(30)
        .to_string()
    )
    print("\n\nSample narratives by important EventTitle:")

    important_events = [
        "Other fall to lower level, unspecified",
        "Caught in running equipment or machinery during regular operation",
        "Caught in running equipment or machinery during maintenance, cleaning",
        "Compressed or pinched by shifting objects or equipment",
        "Struck by falling object or equipment, n.e.c.",
        "Pedestrian struck by vehicle in nonroadway area, unspecified",
    ]

    for event in important_events:

        event_rows = candidates[
            candidates["EventTitle"].astype(str).str.strip() == event.strip()
        ]

        print("\n" + "=" * 80)
        print(event)
        print("=" * 80)

        for narrative in event_rows["Final Narrative"].head(5):
            print("-", narrative)


if __name__ == "__main__":
    create_candidate_corpus()
import json
import pandas as pd

from ai.preprocessing import preprocess_report
from ai.extraction import extract_safety_signals


INPUT_FILE = "data/processed/annotation_sample.csv"
OUTPUT_FILE = "data/processed/representative_safety_reports.json"


# Reports selected to cover different safety scenarios.
REPRESENTATIVE_IDS = [
    "2020087536",  # working at height / forklift / unsafe positioning
    "2020032573",  # scissor lift / crane
    "2016054317",  # lifting / caught-between
    "2022087696",  # electrical work
    "2016054797",  # moving machinery / caught-in
    "2016098325",  # line of fire / falling object
    "2021098316",  # truck / caught-between
    "20191111493", # falling object / struck-by
    "2017087462",  # moving machinery / lockout-tagout
    "2024043119",  # slip/trip/fall
]


CORE_FIELDS = [
    "report_id",
    "timestamp",
    "site",
    "source_type",
    "narrative",
    "hazard",
    "activity",
    "equipment",
    "barrier_failure",
    "exposure",
    "severity_potential",
]


df = pd.read_csv(INPUT_FILE)

selected = df[df["ID"].astype(str).isin(REPRESENTATIVE_IDS)].copy()

missing_ids = set(REPRESENTATIVE_IDS) - set(selected["ID"].astype(str))

if missing_ids:
    raise ValueError(f"Could not find report IDs: {sorted(missing_ids)}")


reports = []

for _, row in selected.iterrows():

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

    # Apply the frozen preprocessing step.
    preprocessed = preprocess_report(raw_report)

    # Apply the frozen Extraction v1 implementation.
    extracted = extract_safety_signals(preprocessed)

    # Validate the required/core SafetyReport fields.
    missing_fields = [
        field for field in CORE_FIELDS
        if field not in extracted
    ]

    if missing_fields:
        raise ValueError(
            f"{raw_report['report_id']} is missing fields: "
            f"{missing_fields}"
        )

    reports.append(extracted)


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(reports, f, indent=2, ensure_ascii=False)


print("SafetyReport fixture created successfully.")
print(f"Input:  {INPUT_FILE}")
print(f"Output: {OUTPUT_FILE}")
print(f"Reports: {len(reports)}")
print(f"Core fields validated: {len(CORE_FIELDS)}")
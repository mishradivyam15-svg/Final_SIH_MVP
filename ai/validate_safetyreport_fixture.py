import json


INPUT_FILE = "data/processed/representative_safety_reports.json"

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

OPTIONAL_FIELDS = [
    "evidence",
]


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    reports = json.load(f)


if not isinstance(reports, list):
    raise ValueError("SafetyReport fixture must contain a list of reports.")


for report in reports:
    missing = [field for field in CORE_FIELDS if field not in report]

    if missing:
        raise ValueError(
            f"{report.get('report_id')} is missing fields: {missing}"
        )

    for field in CORE_FIELDS:
        if field in report and report[field] == "":
            raise ValueError(
                f"{report['report_id']} has an empty string for {field}. "
                "Unknown values should be null."
            )

    unexpected = [
        field
        for field in report
        if field not in CORE_FIELDS and field not in OPTIONAL_FIELDS
    ]

    if unexpected:
        raise ValueError(
            f"{report['report_id']} has unexpected fields: {unexpected}"
        )


print("SafetyReport fixture validation passed.")
print(f"Reports validated: {len(reports)}")
print(f"Core fields checked: {len(CORE_FIELDS)}")
print("Optional extraction metadata allowed: evidence")
import json
from pathlib import Path

import pandas as pd

from ai.extraction import extract_safety_signals


INPUT_FILE = "data/processed/representative_safety_reports.csv"
OUTPUT_FILE = "data/processed/extraction_evaluation_errors.csv"

FIELDS = [
    "hazard",
    "activity",
    "equipment",
    "barrier_failure",
    "exposure",
]


def parse_labels(value):
    """
    Convert a pipe-separated annotation value into a set of labels.
    Missing values become an empty set.
    """
    if pd.isna(value) or str(value).strip() == "":
        return set()

    return {
        label.strip()
        for label in str(value).split("|")
        if label.strip()
    }


def calculate_metrics(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0

    if precision + recall:
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = 0.0

    return precision, recall, f1


def main():
    print("Evaluating safety signal extraction...")

    df = pd.read_csv(INPUT_FILE)

    results = []
    error_rows = []

    totals = {
        field: {"tp": 0, "fp": 0, "fn": 0}
        for field in FIELDS
    }

    for _, row in df.iterrows():

        report = {
            "report_id": str(row["report_id"]),
            "timestamp": row["timestamp"],
            "site": row["site"],
            "source_type": row["source_type"],
            "narrative": row["narrative"],
        }

        prediction = extract_safety_signals(report)

        row_errors = []

        for field in FIELDS:

            gold = parse_labels(row[field])
            predicted = parse_labels(prediction.get(field))

            tp_labels = gold & predicted
            fp_labels = predicted - gold
            fn_labels = gold - predicted

            totals[field]["tp"] += len(tp_labels)
            totals[field]["fp"] += len(fp_labels)
            totals[field]["fn"] += len(fn_labels)

            if fp_labels or fn_labels:
                row_errors.append({
                    "field": field,
                    "gold": sorted(gold),
                    "predicted": sorted(predicted),
                    "false_positive": sorted(fp_labels),
                    "false_negative": sorted(fn_labels),
                })

        if row_errors:
            error_rows.append({
                "report_id": str(row["report_id"]),
                "narrative": row["narrative"],
                "errors": json.dumps(row_errors),
            })

        results.append(prediction)

    print()
    print("========== EXTRACTION BASELINE ==========")

    for field in FIELDS:
        tp = totals[field]["tp"]
        fp = totals[field]["fp"]
        fn = totals[field]["fn"]

        precision, recall, f1 = calculate_metrics(tp, fp, fn)

        print(f"\n{field.upper()}")
        print(f"TP: {tp}")
        print(f"FP: {fp}")
        print(f"FN: {fn}")
        print(f"Precision: {precision:.3f}")
        print(f"Recall:    {recall:.3f}")
        print(f"F1:        {f1:.3f}")

    print()
    print(f"Reports evaluated: {len(df)}")
    print(f"Reports with extraction errors: {len(error_rows)}")

    if error_rows:
        error_df = pd.DataFrame(error_rows)
        error_df.to_csv(OUTPUT_FILE, index=False)

        print(f"Detailed errors saved to: {OUTPUT_FILE}")
    else:
        print("No extraction errors found.")


if __name__ == "__main__":
    main()
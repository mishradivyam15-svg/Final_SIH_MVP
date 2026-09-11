"""
Training label construction pipeline.

Reads the OSHA Severe Injury Report dataset, applies the canonical
EventTitle → (hazard, exposure) mapping, and produces a labeled
training dataset with coverage and class-distribution statistics.

Usage:
    python -m ai.label_construction

Output:
    data/labeled/training_labels.csv

Does NOT modify the original dataset or any existing AI modules.
"""

import csv
import os
import sys
from collections import Counter

# ── Resolve import path ────────────────────────────────────────
# Ensure the repository root is on sys.path so that
# ``from ai.label_mapping import ...`` works when the script is
# run from the repository root.

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ai.label_mapping import (       # noqa: E402
    map_event_title,
    HAZARD_LABELS,
    EXPOSURE_LABELS,
    NARRATIVE_ONLY_LABELS,
)


# ── Paths ───────────────────────────────────────────────────────

DATA_PATH = os.path.join(REPO_ROOT, "data", "January2015toNovember2025.csv")
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "labeled")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "training_labels.csv")

# Columns to carry from the original dataset into the output
CARRY_COLUMNS = [
    "ID",
    "EventDate",
    "EventTitle",
    "Primary NAICS",
    "Hospitalized",
    "Amputation",
    "Loss of Eye",
    "Nature",
    "NatureTitle",
    "Part of Body",
    "Part of Body Title",
    "Event",
    "Source",
    "SourceTitle",
    "Final Narrative",
]

# Generated columns appended to the output
GENERATED_COLUMNS = [
    "hazard_label",
    "exposure_label",
    "mapping_confidence",
]


def run_pipeline():
    """Execute the full label-construction pipeline."""

    # ── 1. Read and map ─────────────────────────────────────────
    print("=" * 70)
    print("  SIF Precursor — Training Label Construction Pipeline")
    print("=" * 70)
    print()
    print(f"Input:  {DATA_PATH}")
    print(f"Output: {OUTPUT_PATH}")
    print()

    rows = []
    missing_event_title = 0

    with open(DATA_PATH, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            event_title = row.get("EventTitle", "").strip()
            mapping = map_event_title(event_title)

            out = {}
            for col in CARRY_COLUMNS:
                out[col] = row.get(col, "")
            out["hazard_label"] = mapping["hazard"] or ""
            out["exposure_label"] = mapping["exposure"] or ""
            out["mapping_confidence"] = mapping["confidence"] or ""

            rows.append(out)

            if not event_title:
                missing_event_title += 1

    total = len(rows)
    print(f"Total rows read:           {total:,}")
    print(f"Missing EventTitle:        {missing_event_title:,}")
    print()

    # ── 2. Write output ─────────────────────────────────────────
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fieldnames = CARRY_COLUMNS + GENERATED_COLUMNS
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    file_size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
    print(f"Output written:            {OUTPUT_PATH}")
    print(f"Output size:               {file_size_mb:.1f} MB")
    print(f"Output columns:            {len(fieldnames)}")
    print()

    # ── 3. Hazard statistics ────────────────────────────────────
    hazard_counter = Counter()
    exposure_counter = Counter()
    confidence_counter = Counter()
    both_null = 0
    hazard_only = 0
    exposure_only = 0
    both_mapped = 0

    for r in rows:
        h = r["hazard_label"] or None
        e = r["exposure_label"] or None
        c = r["mapping_confidence"] or None

        hazard_counter[h] += 1
        exposure_counter[e] += 1
        confidence_counter[c] += 1

        if h and e:
            both_mapped += 1
        elif h and not e:
            hazard_only += 1
        elif e and not h:
            exposure_only += 1
        else:
            both_null += 1

    print("=" * 70)
    print("  HAZARD LABEL DISTRIBUTION")
    print("=" * 70)
    print()
    print(f"  {'Label':<40s} {'Count':>8s} {'%':>7s}")
    print(f"  {'─' * 40} {'─' * 8} {'─' * 7}")

    hazard_mapped_total = 0
    for label in HAZARD_LABELS:
        count = hazard_counter.get(label, 0)
        pct = 100.0 * count / total
        marker = " *" if label in NARRATIVE_ONLY_LABELS else ""
        print(f"  {label:<40s} {count:>8,d} {pct:>6.1f}%{marker}")
        hazard_mapped_total += count

    null_count = hazard_counter.get(None, 0)
    pct = 100.0 * null_count / total
    print(f"  {'(null — unmapped)':<40s} {null_count:>8,d} {pct:>6.1f}%")
    print()
    print(f"  * = narrative-only label (zero EventTitle samples expected)")
    print(f"  Total mapped to a hazard:  {hazard_mapped_total:>8,d} "
          f"({100.0 * hazard_mapped_total / total:.1f}%)")
    print(f"  Total null:                {null_count:>8,d} "
          f"({100.0 * null_count / total:.1f}%)")
    print()

    print("=" * 70)
    print("  EXPOSURE LABEL DISTRIBUTION")
    print("=" * 70)
    print()
    print(f"  {'Label':<40s} {'Count':>8s} {'%':>7s}")
    print(f"  {'─' * 40} {'─' * 8} {'─' * 7}")

    exposure_mapped_total = 0
    for label in EXPOSURE_LABELS:
        count = exposure_counter.get(label, 0)
        pct = 100.0 * count / total
        print(f"  {label:<40s} {count:>8,d} {pct:>6.1f}%")
        exposure_mapped_total += count

    null_count_e = exposure_counter.get(None, 0)
    pct = 100.0 * null_count_e / total
    print(f"  {'(null — unmapped)':<40s} {null_count_e:>8,d} {pct:>6.1f}%")
    print()
    print(f"  Total mapped to an exposure: {exposure_mapped_total:>8,d} "
          f"({100.0 * exposure_mapped_total / total:.1f}%)")
    print(f"  Total null:                  {null_count_e:>8,d} "
          f"({100.0 * null_count_e / total:.1f}%)")
    print()

    print("=" * 70)
    print("  MAPPING CONFIDENCE DISTRIBUTION")
    print("=" * 70)
    print()
    for conf in ["high", "medium", "low", None]:
        count = confidence_counter.get(conf, 0)
        label = conf if conf else "(null)"
        pct = 100.0 * count / total
        print(f"  {label:<12s} {count:>8,d} ({pct:.1f}%)")
    print()

    print("=" * 70)
    print("  JOINT MAPPING SUMMARY")
    print("=" * 70)
    print()
    print(f"  Both hazard + exposure mapped: {both_mapped:>8,d} "
          f"({100.0 * both_mapped / total:.1f}%)")
    print(f"  Hazard only (exposure null):   {hazard_only:>8,d} "
          f"({100.0 * hazard_only / total:.1f}%)")
    print(f"  Exposure only (hazard null):   {exposure_only:>8,d} "
          f"({100.0 * exposure_only / total:.1f}%)")
    print(f"  Both null:                     {both_null:>8,d} "
          f"({100.0 * both_null / total:.1f}%)")
    print()

    # ── 4. Per-EventTitle mapping audit ─────────────────────────
    print("=" * 70)
    print("  PER-EVENTTITLE MAPPING AUDIT (all unique EventTitles)")
    print("=" * 70)
    print()

    # Build per-title stats
    title_map = {}
    for r in rows:
        title = r["EventTitle"]
        if title not in title_map:
            title_map[title] = {
                "count": 0,
                "hazard": r["hazard_label"] or "(null)",
                "exposure": r["exposure_label"] or "(null)",
                "confidence": r["mapping_confidence"] or "(null)",
            }
        title_map[title]["count"] += 1

    # Sort by count descending
    sorted_titles = sorted(title_map.items(),
                           key=lambda x: -x[1]["count"])

    # Print top 50 and bottom 20
    print(f"  {'EventTitle':<70s} {'N':>6s} {'Hazard':<25s} "
          f"{'Exposure':<25s} {'Conf':<7s}")
    print(f"  {'─' * 70} {'─' * 6} {'─' * 25} {'─' * 25} {'─' * 7}")
    for title, info in sorted_titles[:50]:
        t_display = title[:68] + ".." if len(title) > 70 else title
        print(f"  {t_display:<70s} {info['count']:>6,d} "
              f"{info['hazard']:<25s} {info['exposure']:<25s} "
              f"{info['confidence']:<7s}")

    if len(sorted_titles) > 50:
        print(f"  ... ({len(sorted_titles) - 50} more EventTitles) ...")
        print()
        print("  Last 20 (lowest count):")
        for title, info in sorted_titles[-20:]:
            t_display = title[:68] + ".." if len(title) > 70 else title
            print(f"  {t_display:<70s} {info['count']:>6,d} "
                  f"{info['hazard']:<25s} {info['exposure']:<25s} "
                  f"{info['confidence']:<7s}")
    print()

    # ── 5. Validation checks ────────────────────────────────────
    print("=" * 70)
    print("  VALIDATION")
    print("=" * 70)
    print()

    errors = []

    # Check 1: All hazard labels are valid
    for label in hazard_counter:
        if label is not None and label not in HAZARD_LABELS:
            errors.append(f"Invalid hazard label: {label}")

    # Check 2: All exposure labels are valid
    for label in exposure_counter:
        if label is not None and label not in EXPOSURE_LABELS:
            errors.append(f"Invalid exposure label: {label}")

    # Check 3: Row count matches input
    if total != 105996 and total != 105995:
        # Allow for 105995 (1 row has empty EventTitle) or 105996
        errors.append(f"Unexpected row count: {total} (expected ~105,996)")

    # Check 4: Output file exists and is non-empty
    if not os.path.exists(OUTPUT_PATH):
        errors.append("Output file does not exist")
    elif os.path.getsize(OUTPUT_PATH) < 1000:
        errors.append("Output file suspiciously small")

    # Check 5: No rows with confidence but both labels null
    orphan_conf = 0
    for r in rows:
        if r["mapping_confidence"] and not r["hazard_label"] and \
                not r["exposure_label"]:
            orphan_conf += 1
    if orphan_conf > 0:
        errors.append(f"{orphan_conf} rows have confidence but no labels")

    # Check 6: Every non-null label row has confidence
    missing_conf = 0
    for r in rows:
        if (r["hazard_label"] or r["exposure_label"]) and \
                not r["mapping_confidence"]:
            missing_conf += 1
    if missing_conf > 0:
        errors.append(f"{missing_conf} rows have labels but no confidence")

    # Check 7: All narratives are non-empty
    empty_narrative = sum(1 for r in rows if not r["Final Narrative"].strip())
    if empty_narrative > 0:
        errors.append(f"{empty_narrative} rows have empty Final Narrative")

    # Check 8: Narrative-only labels have zero samples
    for label in NARRATIVE_ONLY_LABELS:
        count = hazard_counter.get(label, 0)
        if count > 0:
            errors.append(
                f"Narrative-only label '{label}' has {count} samples "
                f"from EventTitle mapping (expected 0)"
            )

    if errors:
        print("  ❌ VALIDATION FAILED:")
        for e in errors:
            print(f"     • {e}")
    else:
        print("  ✅ All validation checks passed:")
        print(f"     • All hazard labels valid ({len(hazard_counter)-1} "
              f"unique + null)")
        print(f"     • All exposure labels valid ({len(exposure_counter)-1} "
              f"unique + null)")
        print(f"     • Row count: {total:,}")
        print(f"     • Output file: {file_size_mb:.1f} MB")
        print(f"     • No orphan confidence values")
        print(f"     • All labeled rows have confidence")
        print(f"     • All narratives non-empty")
        print(f"     • Narrative-only labels have 0 EventTitle samples")

    print()
    print("=" * 70)
    print("  Pipeline complete.")
    print("=" * 70)

    return len(errors) == 0


if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)

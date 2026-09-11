"""
PyTorch Dataset for SIF precursor safety-signal classification.

Loads training_labels.csv and provides temporal train/val/test splits.
Text input: Final Narrative only.
Labels: hazard (15 classes) and exposure (9 classes).
"""

import csv
import os
from typing import Optional

import torch
from torch.utils.data import Dataset

# ── Canonical label orderings ───────────────────────────────────
# Must match the model output indices exactly.

HAZARD_LABELS = [
    "null",                          # 0
    "working_at_height",             # 1
    "moving_machinery",              # 2
    "mobile_equipment",              # 3
    "electrical_energy",             # 4
    "excavation",                    # 5
    "falling_object",                # 6
    "line_of_fire",                  # 7
    "lifting_operation",             # 8  (zero-sample)
    "chemical_exposure",             # 9
    "stored_energy",                 # 10
    "slip_trip_fall",                # 11
    "confined_space",                # 12 (zero-sample)
    "fire_or_hot_work",              # 13
    "hydrocarbon_or_process_hazard", # 14 (zero-sample)
]

EXPOSURE_LABELS = [
    "null",                  # 0
    "fall_from_height",      # 1
    "caught_in",             # 2
    "caught_between",        # 3
    "struck_by",             # 4
    "electrical_exposure",   # 5
    "fire_exposure",         # 6
    "chemical_exposure",     # 7
    "falling_object_exposure", # 8
]

HAZARD_TO_IDX = {label: idx for idx, label in enumerate(HAZARD_LABELS)}
EXPOSURE_TO_IDX = {label: idx for idx, label in enumerate(EXPOSURE_LABELS)}

# Zero-sample hazard classes (weight = 0 during training)
ZERO_SAMPLE_HAZARD = {"lifting_operation", "confined_space",
                      "hydrocarbon_or_process_hazard"}

CONFIDENCE_WEIGHT = {"high": 1.0, "medium": 0.5, "low": 0.0}


def _parse_year(date_str: str) -> Optional[int]:
    """Extract year from M/D/YYYY format."""
    if not date_str or not date_str.strip():
        return None
    try:
        parts = date_str.strip().split("/")
        if len(parts) == 3:
            return int(parts[2])
    except (ValueError, IndexError):
        pass
    return None


def load_all_rows(csv_path: str) -> list[dict]:
    """Load the labeled CSV and parse years."""
    rows = []
    with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["_year"] = _parse_year(row.get("EventDate", ""))
            rows.append(row)
    return rows


def split_rows(rows: list[dict],
               confidence_filter: Optional[set] = None):
    """
    Split rows into train/val/test by temporal boundaries.

    Train: 2015-2022, Val: 2023, Test: 2024-2025.

    Args:
        rows: All rows from load_all_rows.
        confidence_filter: If provided, only keep training rows whose
            mapping_confidence is in this set. Val/test are unfiltered.

    Returns:
        (train_rows, val_rows, test_rows)
    """
    train, val, test = [], [], []
    for r in rows:
        y = r["_year"]
        if y is None:
            continue
        if y <= 2022:
            if confidence_filter:
                conf = r.get("mapping_confidence", "").strip()
                if conf not in confidence_filter:
                    continue
            train.append(r)
        elif y == 2023:
            val.append(r)
        else:
            test.append(r)
    return train, val, test


class SafetyDataset(Dataset):
    """PyTorch dataset for safety-signal classification."""

    def __init__(self, rows: list[dict], tokenizer=None, max_length: int = 128):
        """
        Args:
            rows: List of dicts from load_all_rows / split_rows.
            tokenizer: HuggingFace tokenizer.
            max_length: Max token length.
        """
        self.texts = []
        self.hazard_labels = []
        self.exposure_labels = []
        self.confidence_weights = []

        for r in rows:
            text = r.get("Final Narrative", "").strip()
            if not text:
                continue

            h_str = r.get("hazard_label", "").strip() or "null"
            e_str = r.get("exposure_label", "").strip() or "null"
            conf = r.get("mapping_confidence", "").strip()

            h_idx = HAZARD_TO_IDX.get(h_str, 0)
            e_idx = EXPOSURE_TO_IDX.get(e_str, 0)
            c_weight = CONFIDENCE_WEIGHT.get(conf, 1.0)

            self.texts.append(text)
            self.hazard_labels.append(h_idx)
            self.exposure_labels.append(e_idx)
            self.confidence_weights.append(c_weight)

        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        item = {
            "text": self.texts[idx],
            "hazard_label": self.hazard_labels[idx],
            "exposure_label": self.exposure_labels[idx],
            "confidence_weight": self.confidence_weights[idx],
        }

        if self.tokenizer is not None:
            encoded = self.tokenizer(
                self.texts[idx],
                max_length=self.max_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )
            item["input_ids"] = encoded["input_ids"].squeeze(0)
            item["attention_mask"] = encoded["attention_mask"].squeeze(0)

        return item

    def get_class_weights(self, device="cpu"):
        """
        Compute inverse-frequency class weights for hazard and exposure.
        Zero-sample classes get weight 0.
        """
        from collections import Counter

        n = len(self.hazard_labels)
        n_haz = len(HAZARD_LABELS)
        n_exp = len(EXPOSURE_LABELS)

        haz_counts = Counter(self.hazard_labels)
        exp_counts = Counter(self.exposure_labels)

        haz_weights = []
        for i, label in enumerate(HAZARD_LABELS):
            count = haz_counts.get(i, 0)
            if count == 0 or label in ZERO_SAMPLE_HAZARD:
                haz_weights.append(0.0)
            else:
                haz_weights.append(n / (n_haz * count))
        
        exp_weights = []
        for i in range(n_exp):
            count = exp_counts.get(i, 0)
            if count == 0:
                exp_weights.append(0.0)
            else:
                exp_weights.append(n / (n_exp * count))

        return (
            torch.tensor(haz_weights, dtype=torch.float, device=device),
            torch.tensor(exp_weights, dtype=torch.float, device=device),
        )

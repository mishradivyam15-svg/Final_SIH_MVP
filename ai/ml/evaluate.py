"""
Evaluation utilities for safety-signal classifier.

Computes macro F1, weighted F1, per-class P/R/F1, confusion matrices.
"""

import json
import os
import time
from collections import Counter

import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)

from ai.ml.dataset import HAZARD_LABELS, EXPOSURE_LABELS


def predict_transformer(model, dataloader, device):
    """Run inference and collect predictions + ground truth."""
    model.eval()
    all_haz_preds, all_exp_preds = [], []
    all_haz_true, all_exp_true = [], []

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)

            haz_logits, exp_logits = model(input_ids, attention_mask)

            all_haz_preds.extend(haz_logits.argmax(dim=1).cpu().tolist())
            all_exp_preds.extend(exp_logits.argmax(dim=1).cpu().tolist())
            all_haz_true.extend(batch["hazard_label"].tolist())
            all_exp_true.extend(batch["exposure_label"].tolist())

    return all_haz_true, all_haz_preds, all_exp_true, all_exp_preds


def compute_metrics(y_true, y_pred, label_names, task_name="task"):
    """Compute all metrics for one classification head."""
    # Filter to labels that appear in truth or predictions
    present_labels = sorted(set(y_true) | set(y_pred))
    present_names = [label_names[i] for i in present_labels]

    macro_f1 = f1_score(y_true, y_pred, average="macro",
                        labels=present_labels, zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, average="weighted",
                           labels=present_labels, zero_division=0)
    accuracy = accuracy_score(y_true, y_pred)

    # Per-class
    report_dict = classification_report(
        y_true, y_pred,
        labels=present_labels,
        target_names=present_names,
        output_dict=True,
        zero_division=0,
    )
    report_str = classification_report(
        y_true, y_pred,
        labels=present_labels,
        target_names=present_names,
        zero_division=0,
    )

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=present_labels)

    # Null class (index 0) metrics
    null_metrics = report_dict.get(label_names[0], {})

    return {
        "task": task_name,
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "accuracy": float(accuracy),
        "null_precision": float(null_metrics.get("precision", 0)),
        "null_recall": float(null_metrics.get("recall", 0)),
        "null_f1": float(null_metrics.get("f1-score", 0)),
        "report_str": report_str,
        "report_dict": report_dict,
        "confusion_matrix": cm.tolist(),
        "present_labels": present_labels,
        "present_names": present_names,
    }


def save_confusion_matrix(cm, labels, title, filepath):
    """Save confusion matrix as a heatmap image."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    fig, ax = plt.subplots(figsize=(max(8, len(labels)), max(6, len(labels) * 0.7)))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=labels, yticklabels=labels, ax=ax,
        linewidths=0.5,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(title)
    plt.tight_layout()
    plt.savefig(filepath, dpi=120, bbox_inches="tight")
    plt.close(fig)


def evaluate_and_save(experiment_name, haz_true, haz_pred, exp_true, exp_pred,
                      output_dir, training_time=None):
    """Full evaluation pipeline: compute metrics, save reports and plots."""
    os.makedirs(output_dir, exist_ok=True)

    haz_metrics = compute_metrics(
        haz_true, haz_pred, HAZARD_LABELS, "hazard"
    )
    exp_metrics = compute_metrics(
        exp_true, exp_pred, EXPOSURE_LABELS, "exposure"
    )

    # Summary
    summary = {
        "experiment": experiment_name,
        "training_time_seconds": training_time,
        "hazard": {
            "macro_f1": haz_metrics["macro_f1"],
            "weighted_f1": haz_metrics["weighted_f1"],
            "accuracy": haz_metrics["accuracy"],
            "null_precision": haz_metrics["null_precision"],
            "null_recall": haz_metrics["null_recall"],
            "null_f1": haz_metrics["null_f1"],
        },
        "exposure": {
            "macro_f1": exp_metrics["macro_f1"],
            "weighted_f1": exp_metrics["weighted_f1"],
            "accuracy": exp_metrics["accuracy"],
            "null_precision": exp_metrics["null_precision"],
            "null_recall": exp_metrics["null_recall"],
            "null_f1": exp_metrics["null_f1"],
        },
    }

    # Save JSON summary
    with open(os.path.join(output_dir, "metrics.json"), "w") as f:
        json.dump(summary, f, indent=2)

    # Save classification reports
    with open(os.path.join(output_dir, "hazard_report.txt"), "w") as f:
        f.write(f"Experiment: {experiment_name}\n")
        f.write(f"Task: Hazard Classification (15 classes)\n\n")
        f.write(haz_metrics["report_str"])

    with open(os.path.join(output_dir, "exposure_report.txt"), "w") as f:
        f.write(f"Experiment: {experiment_name}\n")
        f.write(f"Task: Exposure Classification (9 classes)\n\n")
        f.write(exp_metrics["report_str"])

    # Save confusion matrices
    save_confusion_matrix(
        np.array(haz_metrics["confusion_matrix"]),
        haz_metrics["present_names"],
        f"{experiment_name} — Hazard Confusion Matrix",
        os.path.join(output_dir, "hazard_confusion.png"),
    )
    save_confusion_matrix(
        np.array(exp_metrics["confusion_matrix"]),
        exp_metrics["present_names"],
        f"{experiment_name} — Exposure Confusion Matrix",
        os.path.join(output_dir, "exposure_confusion.png"),
    )

    # Print summary
    print(f"\n{'='*60}")
    print(f"  {experiment_name} — TEST SET RESULTS")
    print(f"{'='*60}")
    print(f"  {'Metric':<25s} {'Hazard':>10s} {'Exposure':>10s}")
    print(f"  {'─'*25} {'─'*10} {'─'*10}")
    print(f"  {'Macro F1':<25s} {haz_metrics['macro_f1']:>10.4f} "
          f"{exp_metrics['macro_f1']:>10.4f}")
    print(f"  {'Weighted F1':<25s} {haz_metrics['weighted_f1']:>10.4f} "
          f"{exp_metrics['weighted_f1']:>10.4f}")
    print(f"  {'Accuracy':<25s} {haz_metrics['accuracy']:>10.4f} "
          f"{exp_metrics['accuracy']:>10.4f}")
    print(f"  {'Null P':<25s} {haz_metrics['null_precision']:>10.4f} "
          f"{exp_metrics['null_precision']:>10.4f}")
    print(f"  {'Null R':<25s} {haz_metrics['null_recall']:>10.4f} "
          f"{exp_metrics['null_recall']:>10.4f}")
    print(f"  {'Null F1':<25s} {haz_metrics['null_f1']:>10.4f} "
          f"{exp_metrics['null_f1']:>10.4f}")
    if training_time:
        print(f"  {'Training time':<25s} {training_time:>10.1f}s")
    print()

    return summary

"""
Training loop for dual-head safety-signal classifier.

Runs experiments A, B, C with different configurations.
Supports frozen and fine-tuned encoder, confidence-weighted loss.
"""

import json
import os
import sys
import time

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ai.ml.dataset import (
    load_all_rows, split_rows, SafetyDataset,
    HAZARD_LABELS, EXPOSURE_LABELS,
)
from ai.ml.model import SafetySignalClassifier, get_tokenizer
from ai.ml.evaluate import predict_transformer, evaluate_and_save


DATA_PATH = os.path.join(REPO_ROOT, "data", "labeled", "training_labels.csv")
MODEL_DIR = os.path.join(REPO_ROOT, "models", "safety_classifier")
RESULTS_DIR = os.path.join(MODEL_DIR, "results")


def get_device():
    """Get best available device, with MPS fallback to CPU."""
    if torch.backends.mps.is_available():
        try:
            # Quick MPS sanity check
            t = torch.zeros(1, device="mps")
            _ = t + 1
            print("Using device: MPS (Apple Silicon)")
            return torch.device("mps")
        except Exception:
            pass
    print("Using device: CPU")
    return torch.device("cpu")


def collate_fn(batch):
    """Custom collation for SafetyDataset."""
    return {
        "input_ids": torch.stack([b["input_ids"] for b in batch]),
        "attention_mask": torch.stack([b["attention_mask"] for b in batch]),
        "hazard_label": torch.tensor([b["hazard_label"] for b in batch],
                                     dtype=torch.long),
        "exposure_label": torch.tensor([b["exposure_label"] for b in batch],
                                       dtype=torch.long),
        "confidence_weight": torch.tensor([b["confidence_weight"] for b in batch],
                                          dtype=torch.float),
    }


def train_one_epoch(model, dataloader, optimizer, haz_criterion, exp_criterion,
                    device, use_confidence_weights=False):
    """Train for one epoch. Returns average loss."""
    model.train()
    total_loss = 0.0
    n_batches = 0

    for batch in dataloader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        haz_labels = batch["hazard_label"].to(device)
        exp_labels = batch["exposure_label"].to(device)
        conf_weights = batch["confidence_weight"].to(device)

        optimizer.zero_grad()

        haz_logits, exp_logits = model(input_ids, attention_mask)

        # Hazard loss
        haz_loss = haz_criterion(haz_logits, haz_labels)
        if use_confidence_weights:
            haz_loss = haz_loss * conf_weights
        haz_loss = haz_loss.mean()

        # Exposure loss
        exp_loss = exp_criterion(exp_logits, exp_labels)
        if use_confidence_weights:
            exp_loss = exp_loss * conf_weights
        exp_loss = exp_loss.mean()

        loss = haz_loss + exp_loss
        loss.backward()

        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

        optimizer.step()

        total_loss += loss.item()
        n_batches += 1

    return total_loss / max(n_batches, 1)


def evaluate_epoch(model, dataloader, haz_criterion, exp_criterion, device):
    """Evaluate on validation set. Returns (loss, macro_f1_hazard, macro_f1_exposure)."""
    from sklearn.metrics import f1_score

    model.eval()
    total_loss = 0.0
    n_batches = 0
    all_haz_pred, all_haz_true = [], []
    all_exp_pred, all_exp_true = [], []

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            haz_labels = batch["hazard_label"].to(device)
            exp_labels = batch["exposure_label"].to(device)

            haz_logits, exp_logits = model(input_ids, attention_mask)

            haz_loss = haz_criterion(haz_logits, haz_labels).mean()
            exp_loss = exp_criterion(exp_logits, exp_labels).mean()
            total_loss += (haz_loss + exp_loss).item()
            n_batches += 1

            all_haz_pred.extend(haz_logits.argmax(1).cpu().tolist())
            all_haz_true.extend(haz_labels.cpu().tolist())
            all_exp_pred.extend(exp_logits.argmax(1).cpu().tolist())
            all_exp_true.extend(exp_labels.cpu().tolist())

    avg_loss = total_loss / max(n_batches, 1)
    haz_f1 = f1_score(all_haz_true, all_haz_pred, average="macro",
                      zero_division=0)
    exp_f1 = f1_score(all_exp_true, all_exp_pred, average="macro",
                      zero_division=0)

    return avg_loss, haz_f1, exp_f1


def run_experiment(
    experiment_name: str,
    confidence_filter: set,
    use_confidence_weights: bool,
    freeze_encoder: bool,
    fine_tune_after: int = 0,
    frozen_epochs: int = 3,
    finetune_epochs: int = 5,
    batch_size: int = 64,
    max_length: int = 128,
    patience: int = 2,
):
    """
    Run a single transformer experiment.

    Args:
        experiment_name: e.g. "A", "B", "C"
        confidence_filter: set of confidence levels to include in train
        use_confidence_weights: whether to scale loss by confidence
        freeze_encoder: whether encoder starts frozen
        fine_tune_after: epoch after which to unfreeze encoder (0 = never)
        frozen_epochs: number of epochs with frozen encoder
        finetune_epochs: number of epochs after unfreezing
        batch_size: training batch size
        max_length: token sequence length
        patience: early stopping patience (epochs without improvement)
    """
    exp_dir = os.path.join(RESULTS_DIR, f"Exp_{experiment_name}")
    os.makedirs(exp_dir, exist_ok=True)

    print()
    print("=" * 60)
    print(f"  Experiment {experiment_name}")
    print("=" * 60)
    print(f"  Confidence filter: {confidence_filter}")
    print(f"  Confidence weighting: {use_confidence_weights}")
    print(f"  Encoder frozen: {freeze_encoder}")
    if fine_tune_after > 0:
        print(f"  Unfreeze after epoch: {fine_tune_after}")
    print()

    device = get_device()

    # Load data
    all_rows = load_all_rows(DATA_PATH)
    train_rows, val_rows, test_rows = split_rows(
        all_rows, confidence_filter=confidence_filter
    )

    print(f"Train rows: {len(train_rows):,}")
    print(f"Val rows:   {len(val_rows):,}")
    print(f"Test rows:  {len(test_rows):,}")

    # Tokenizer and datasets
    tokenizer = get_tokenizer()
    train_ds = SafetyDataset(train_rows, tokenizer=tokenizer, max_length=max_length)
    val_ds = SafetyDataset(val_rows, tokenizer=tokenizer, max_length=max_length)
    test_ds = SafetyDataset(test_rows, tokenizer=tokenizer, max_length=max_length)

    print(f"Train samples: {len(train_ds):,}")
    print(f"Val samples:   {len(val_ds):,}")
    print(f"Test samples:  {len(test_ds):,}")

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                              collate_fn=collate_fn, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False,
                            collate_fn=collate_fn, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False,
                             collate_fn=collate_fn, num_workers=0)

    # Model
    model = SafetySignalClassifier(
        freeze_encoder=freeze_encoder,
        n_hazard_classes=len(HAZARD_LABELS),
        n_exposure_classes=len(EXPOSURE_LABELS),
    ).to(device)

    # Class weights
    haz_weights, exp_weights = train_ds.get_class_weights(device=device)
    haz_criterion = nn.CrossEntropyLoss(weight=haz_weights, reduction="none")
    exp_criterion = nn.CrossEntropyLoss(weight=exp_weights, reduction="none")

    # Optimizer — heads only initially
    head_params = list(model.hazard_head.parameters()) + \
                  list(model.exposure_head.parameters())
    optimizer = torch.optim.AdamW(head_params, lr=2e-3, weight_decay=0.01)

    total_epochs = frozen_epochs + (finetune_epochs if fine_tune_after > 0 else 0)
    best_val_f1 = -1.0
    best_epoch = -1
    epochs_without_improvement = 0

    start_time = time.time()

    print(f"\nTraining for up to {total_epochs} epochs...")
    print(f"{'Epoch':>5s} {'Phase':>8s} {'TrLoss':>8s} {'VLoss':>8s} "
          f"{'VHazF1':>8s} {'VExpF1':>8s} {'VMeanF1':>8s} {'Best':>6s}")
    print("-" * 60)

    for epoch in range(1, total_epochs + 1):
        # Check if we should unfreeze
        phase = "frozen"
        if fine_tune_after > 0 and epoch > frozen_epochs:
            if epoch == frozen_epochs + 1:
                print(f"\n  >>> Unfreezing encoder at epoch {epoch} <<<\n")
                model.unfreeze_encoder()
                # Reset optimizer with discriminative LR
                optimizer = torch.optim.AdamW([
                    {"params": model.encoder.parameters(), "lr": 2e-5},
                    {"params": head_params, "lr": 2e-4},
                ], weight_decay=0.01)
                epochs_without_improvement = 0  # Reset patience
            phase = "finetune"

        # Train
        train_loss = train_one_epoch(
            model, train_loader, optimizer,
            haz_criterion, exp_criterion, device,
            use_confidence_weights=use_confidence_weights,
        )

        # Validate
        val_loss, val_haz_f1, val_exp_f1 = evaluate_epoch(
            model, val_loader, haz_criterion, exp_criterion, device,
        )
        val_mean_f1 = (val_haz_f1 + val_exp_f1) / 2

        is_best = val_mean_f1 > best_val_f1
        if is_best:
            best_val_f1 = val_mean_f1
            best_epoch = epoch
            epochs_without_improvement = 0
            # Save best checkpoint
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "val_mean_f1": val_mean_f1,
                "val_haz_f1": val_haz_f1,
                "val_exp_f1": val_exp_f1,
            }, os.path.join(exp_dir, "best_model.pt"))
        else:
            epochs_without_improvement += 1

        marker = " *" if is_best else ""
        print(f"{epoch:>5d} {phase:>8s} {train_loss:>8.4f} {val_loss:>8.4f} "
              f"{val_haz_f1:>8.4f} {val_exp_f1:>8.4f} {val_mean_f1:>8.4f}"
              f"{marker}")

        # Early stopping
        if epochs_without_improvement >= patience:
            print(f"\n  Early stopping at epoch {epoch} "
                  f"(no improvement for {patience} epochs)")
            break

    training_time = time.time() - start_time
    print(f"\nTraining complete. Best epoch: {best_epoch}, "
          f"Best val mean F1: {best_val_f1:.4f}, Time: {training_time:.1f}s")

    # Load best model and evaluate on test set
    checkpoint = torch.load(os.path.join(exp_dir, "best_model.pt"),
                            map_location=device, weights_only=True)
    model.load_state_dict(checkpoint["model_state_dict"])

    haz_true, haz_pred, exp_true, exp_pred = predict_transformer(
        model, test_loader, device,
    )

    summary = evaluate_and_save(
        f"Exp {experiment_name}",
        haz_true, haz_pred, exp_true, exp_pred,
        exp_dir,
        training_time=training_time,
    )

    # Save config
    config = {
        "experiment": experiment_name,
        "confidence_filter": list(confidence_filter),
        "use_confidence_weights": use_confidence_weights,
        "freeze_encoder": freeze_encoder,
        "fine_tune_after": fine_tune_after,
        "frozen_epochs": frozen_epochs,
        "finetune_epochs": finetune_epochs,
        "batch_size": batch_size,
        "max_length": max_length,
        "best_epoch": best_epoch,
        "best_val_f1": best_val_f1,
        "training_time": training_time,
        "hazard_labels": HAZARD_LABELS,
        "exposure_labels": EXPOSURE_LABELS,
    }
    with open(os.path.join(exp_dir, "config.json"), "w") as f:
        json.dump(config, f, indent=2)

    return summary


def run_all_experiments():
    """Run experiments A, B, C sequentially."""

    results = {}

    # Experiment A: Frozen encoder, high-confidence only
    results["A"] = run_experiment(
        experiment_name="A",
        confidence_filter={"high"},
        use_confidence_weights=False,
        freeze_encoder=True,
        fine_tune_after=0,
        frozen_epochs=5,
        patience=2,
    )

    # Experiment B: Frozen encoder, high + medium with confidence weighting
    results["B"] = run_experiment(
        experiment_name="B",
        confidence_filter={"high", "medium"},
        use_confidence_weights=True,
        freeze_encoder=True,
        fine_tune_after=0,
        frozen_epochs=5,
        patience=2,
    )

    # Experiment C: Fine-tuned encoder, high + medium with confidence weighting
    results["C"] = run_experiment(
        experiment_name="C",
        confidence_filter={"high", "medium"},
        use_confidence_weights=True,
        freeze_encoder=True,
        fine_tune_after=3,  # Unfreeze after epoch 3
        frozen_epochs=3,
        finetune_epochs=5,
        patience=2,
    )

    # Save comparison
    comparison_path = os.path.join(RESULTS_DIR, "experiment_comparison.json")
    with open(comparison_path, "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print("  ALL EXPERIMENTS COMPLETE")
    print("=" * 60)
    print(f"\n  {'Exp':<6s} {'Haz mF1':>9s} {'Exp mF1':>9s} "
          f"{'Haz wF1':>9s} {'Exp wF1':>9s} {'Time':>8s}")
    print(f"  {'─'*6} {'─'*9} {'─'*9} {'─'*9} {'─'*9} {'─'*8}")
    for name, r in results.items():
        h = r["hazard"]
        e = r["exposure"]
        t = r.get("training_time_seconds", 0) or 0
        print(f"  {name:<6s} {h['macro_f1']:>9.4f} {e['macro_f1']:>9.4f} "
              f"{h['weighted_f1']:>9.4f} {e['weighted_f1']:>9.4f} "
              f"{t:>7.1f}s")
    print()

    return results


if __name__ == "__main__":
    run_all_experiments()

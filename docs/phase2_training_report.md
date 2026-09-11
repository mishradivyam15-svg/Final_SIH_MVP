# Phase 2: ML Safety-Signal Classifier — Training Report

**Date**: 2026-09-11
**Branch**: `ai/relationship-precursor`
**Test set**: 2024–2025, 17,746 OSHA reports (untouched during training)

---

## 1. Experiment Summary

| Exp | Model | Train Data | Confidence | Hazard mF1 | Exp mF1 | Haz wF1 | Exp wF1 | Accuracy (H) | Accuracy (E) | Time |
|-----|-------|-----------|-----------|:----------:|:-------:|:-------:|:-------:|:------------:|:------------:|-----:|
| **BL** | TF-IDF + LR | high+medium (69K) | N/A | **0.7348** | **0.6893** | 0.7509 | 0.6737 | 0.7502 | 0.6630 | **13s** |
| **A** | Frozen MiniLM | high only (55K) | No | 0.5893 | 0.5537 | 0.6690 | 0.5620 | 0.6663 | 0.5500 | 19m |
| **B** | Frozen MiniLM | high+medium (69K) | Yes (0.5) | 0.6718 | 0.6178 | 0.6945 | 0.6019 | 0.6910 | 0.5896 | 28m |
| **C** | **Fine-tuned MiniLM** | high+medium (69K) | Yes (0.5) | **0.7525** | **0.6928** | 0.7545 | 0.6745 | 0.7590 | 0.6669 | ~81m |

> [!IMPORTANT]
> **Exp C (fine-tuned transformer) is the best model** on both hazard and exposure macro F1, but the margin over TF-IDF+LR (BL) is narrow: **+1.8pp hazard, +0.4pp exposure**.

---

## 2. Ablation Results

### Q1: Does adding medium-confidence data help?

**A (high-only) vs B (high+medium): YES, strongly.**

| Metric | A (high) | B (high+med) | Δ |
|--------|:--------:|:----------:|:-:|
| Hazard macro F1 | 0.5893 | 0.6718 | **+8.3pp** |
| Exposure macro F1 | 0.5537 | 0.6178 | **+6.4pp** |

Medium-confidence labels are critical — without them, `fire_or_hot_work` and `line_of_fire` have too few training samples.

### Q2: Does fine-tuning the encoder help?

**B (frozen) vs C (fine-tuned): YES, substantially.**

| Metric | B (frozen) | C (fine-tuned) | Δ |
|--------|:----------:|:----------:|:-:|
| Hazard macro F1 | 0.6718 | 0.7525 | **+8.1pp** |
| Exposure macro F1 | 0.6178 | 0.6928 | **+7.5pp** |

Fine-tuning the encoder allows the model to adapt its internal representations to safety-specific language.

### Q3: Does the transformer beat TF-IDF+LR?

**BL vs C: Yes, but the margin is narrow.**

| Metric | BL (TF-IDF) | C (Transformer) | Δ |
|--------|:-----------:|:----------:|:-:|
| Hazard macro F1 | 0.7348 | 0.7525 | **+1.8pp** |
| Exposure macro F1 | 0.6893 | 0.6928 | **+0.4pp** |
| Hazard accuracy | 0.7502 | 0.7590 | +0.9pp |
| Null F1 (hazard) | 0.4576 | 0.4398 | −1.8pp |
| Null F1 (exposure) | 0.7969 | 0.8015 | +0.5pp |
| Training time | 13s | ~81m | 370× slower |

> [!NOTE]
> TF-IDF+LR is remarkably competitive. The narratives are short (median 31 words) and the label signal is strong from keyword patterns, which is exactly where TF-IDF excels.

---

## 3. Per-Class Results (Exp C — Production Candidate)

### 3.1 Hazard Classification

| Class | Precision | Recall | F1 | Support |
|-------|:---------:|:------:|:--:|--------:|
| `null` | 0.55 | 0.37 | 0.44 | 2,821 |
| `working_at_height` | 0.91 | 0.90 | **0.91** | 3,117 |
| `moving_machinery` | 0.94 | 0.79 | **0.86** | 3,636 |
| `mobile_equipment` | 0.68 | 0.74 | 0.71 | 1,609 |
| `electrical_energy` | 0.87 | 1.00 | **0.93** | 397 |
| `excavation` | 0.43 | 1.00 | 0.61 | 20 |
| `falling_object` | 0.55 | 0.90 | 0.68 | 969 |
| `line_of_fire` | 0.40 | 0.48 | 0.44 | 1,164 |
| `chemical_exposure` | 0.71 | 0.97 | **0.82** | 273 |
| `stored_energy` | 0.84 | 0.87 | **0.85** | 117 |
| `slip_trip_fall` | 0.83 | 0.91 | **0.87** | 2,654 |
| `fire_or_hot_work` | 0.89 | 0.96 | **0.92** | 969 |

**Strong classes** (F1 > 0.8): `working_at_height`, `moving_machinery`, `electrical_energy`, `chemical_exposure`, `stored_energy`, `slip_trip_fall`, `fire_or_hot_work`.

**Weak classes** (F1 < 0.5): `null` (0.44), `line_of_fire` (0.44). The null class has low recall (0.37) meaning the model overpredicts specific hazards. `line_of_fire` is semantically ambiguous with `falling_object` and `struck_by`.

### 3.2 Exposure Classification

| Class | Precision | Recall | F1 | Support |
|-------|:---------:|:------:|:--:|--------:|
| `null` | 0.94 | 0.70 | **0.80** | 5,017 |
| `fall_from_height` | 0.90 | 0.91 | **0.91** | 3,238 |
| `caught_in` | 0.34 | 0.82 | 0.48 | 1,359 |
| `caught_between` | 0.26 | 0.71 | 0.38 | 700 |
| `struck_by` | 0.74 | 0.36 | 0.48 | 5,587 |
| `electrical_exposure` | 0.85 | 1.00 | **0.92** | 397 |
| `fire_exposure` | 0.64 | 0.99 | 0.78 | 207 |
| `chemical_exposure` | 0.70 | 0.97 | **0.81** | 272 |
| `falling_object_exposure` | 0.53 | 0.92 | 0.67 | 969 |

**Exposure confusion pattern**: `caught_in`, `caught_between`, and `struck_by` are heavily confused with each other. These three describe similar physical mechanisms (object-person contact), making narrative-only classification inherently difficult.

---

## 4. Diagnosis: Why Exp C Got Stuck

The training log shows:
1. Exp C loaded the model and tokenizer successfully
2. No epoch-level training output was printed
3. The `best_model.pt` was saved at **14:27** (~81 min after start at ~13:06)
4. The process then hung with no CPU progress for 2+ hours

**Root cause**: MPS (Apple Silicon GPU) memory management issue during the fine-tuning phase. When the encoder is unfrozen, backpropagation through 22.7M parameters creates large activation/gradient tensors on the MPS device. After several epochs, MPS memory fragmentation likely caused a deadlock during either:
- The validation pass after the final epoch (large `torch.no_grad()` inference)
- The test set prediction loop (17,746 × 128 tokens in sequence)

The checkpoint itself is complete and valid (epoch 5, val mean F1 = 0.7730). The evaluation was successfully completed on CPU.

---

## 5. Production Recommendation

> [!IMPORTANT]
> **Recommended production candidate: Exp C (fine-tuned MiniLM)**
>
> It achieves the highest macro F1 on both tasks. However, consider the tradeoffs:

| Factor | Exp C (Transformer) | BL (TF-IDF+LR) |
|--------|:-------------------:|:---------------:|
| Hazard macro F1 | **0.7525** | 0.7348 |
| Exposure macro F1 | **0.6928** | 0.6893 |
| Training time | ~81 min | 13 sec |
| Inference speed | ~7 ms/sample (CPU) | ~0.01 ms/sample |
| Model size | 86.7 MB | ~2 MB |
| Dependencies | PyTorch + transformers | scikit-learn only |
| Deployment complexity | Medium | Low |

**If deployment simplicity is paramount**, TF-IDF+LR (BL) achieves 97.6% of the transformer's hazard F1 and 99.5% of its exposure F1 with 370× faster training and trivial deployment.

**If maximum accuracy matters**, Exp C is the better choice, especially for classes like `stored_energy` (0.85 vs 0.71 F1) and `chemical_exposure` (0.82 vs 0.75 F1).

---

## 6. Files Created

### Training Code
| File | Purpose |
|------|---------|
| [`ai/ml/__init__.py`](file:///Users/divyammishra/Desktop/SIH-26-SIF-PRECURSORS-full/ai/ml/__init__.py) | Package init |
| [`ai/ml/dataset.py`](file:///Users/divyammishra/Desktop/SIH-26-SIF-PRECURSORS-full/ai/ml/dataset.py) | Dataset, temporal splits, label indexing |
| [`ai/ml/model.py`](file:///Users/divyammishra/Desktop/SIH-26-SIF-PRECURSORS-full/ai/ml/model.py) | Dual-head classifier architecture |
| [`ai/ml/train.py`](file:///Users/divyammishra/Desktop/SIH-26-SIF-PRECURSORS-full/ai/ml/train.py) | Training loop, experiments A/B/C |
| [`ai/ml/evaluate.py`](file:///Users/divyammishra/Desktop/SIH-26-SIF-PRECURSORS-full/ai/ml/evaluate.py) | Metrics, confusion matrices, reports |
| [`ai/ml/baseline.py`](file:///Users/divyammishra/Desktop/SIH-26-SIF-PRECURSORS-full/ai/ml/baseline.py) | TF-IDF + Logistic Regression baseline |

### Model Outputs
| File | Purpose |
|------|---------|
| `models/safety_classifier/best_model.pt` | Production checkpoint (Exp C, 86.7 MB) |
| `models/safety_classifier/config.json` | Model configuration and label maps |
| `models/safety_classifier/results/Exp_A/` | Exp A metrics, reports, confusion matrices |
| `models/safety_classifier/results/Exp_B/` | Exp B metrics, reports, confusion matrices |
| `models/safety_classifier/results/Exp_C/` | Exp C metrics, reports, confusion matrices |
| `models/safety_classifier/results/BL_tfidf_lr/` | Baseline metrics, reports, confusion matrices |
| `models/safety_classifier/results/experiment_comparison.json` | All experiments side-by-side |

### Documentation
| File | Purpose |
|------|---------|
| `docs/phase2_training_report.md` | This report |

### Files NOT Modified
- `ai/extraction.py` — untouched
- `ai/relationship.py` — untouched  
- `ai/embeddings.py` — untouched
- `data/January2015toNovember2025.csv` — untouched
- `data/labeled/training_labels.csv` — untouched

---

## 7. Known Limitations and Next Steps

1. **Null class recall is low** (0.37 hazard, 0.70 exposure) — the model over-predicts specific labels. Future work: calibration or threshold tuning.
2. **`caught_in` / `caught_between` / `struck_by` confusion** — these exposure types are semantically similar and hard to distinguish from narrative text alone.
3. **`line_of_fire` F1 = 0.44** — ambiguous hazard category. May benefit from sub-category splitting or narrative-specific features.
4. **3 zero-sample hazard classes** (`lifting_operation`, `confined_space`, `hydrocarbon_or_process_hazard`) — need narrative-based labeling to activate.
5. **MPS training instability** — use CPU fallback for production training or reduce batch size during fine-tuning.

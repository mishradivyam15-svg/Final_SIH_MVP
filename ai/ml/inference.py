"""
ML safety-signal inference for production use.

Loads the trained dual-head classifier and predicts hazard/exposure
from a single narrative. Designed for backend integration.
"""

import os
import sys

import torch
import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ai.ml.dataset import HAZARD_LABELS, EXPOSURE_LABELS
from ai.ml.model import SafetySignalClassifier, get_tokenizer


# Default checkpoint path
DEFAULT_CHECKPOINT = os.path.join(
    REPO_ROOT, "models", "safety_classifier", "best_model.pt"
)

# The checkpoint is gitignored (too large for a normal commit), so a
# deployed backend never has models/ populated. It's mirrored on the
# Hugging Face Hub and downloaded there on first use instead — local dev
# keeps using the file already on disk, so this changes nothing for anyone
# who has it.
HF_MODEL_REPO = os.environ.get(
    "SIF_MODEL_REPO", "Divyam1512/sif-precursor-safety-classifier"
)
HF_MODEL_FILENAME = "best_model.pt"


def _resolve_checkpoint_path(checkpoint_path: str) -> str | None:
    """Return a local path to the checkpoint, downloading it from the
    Hugging Face Hub if it isn't already on disk. Cached by huggingface_hub
    after the first download, so this only costs time on a cold start."""

    if os.path.exists(checkpoint_path):
        return checkpoint_path

    try:
        from huggingface_hub import hf_hub_download

        print(f"[SafetySignalPredictor] Downloading checkpoint from "
              f"{HF_MODEL_REPO}...")
        return hf_hub_download(repo_id=HF_MODEL_REPO, filename=HF_MODEL_FILENAME)
    except Exception as exc:
        print(f"[SafetySignalPredictor] Could not fetch checkpoint from "
              f"{HF_MODEL_REPO}: {exc}")
        return None


class SafetySignalPredictor:
    """
    Production inference wrapper for the trained safety-signal classifier.

    Usage:
        predictor = SafetySignalPredictor()
        result = predictor.predict("Worker fell from scaffolding...")
        # {"hazard": "working_at_height", "exposure": "fall_from_height",
        #  "hazard_confidence": 0.94, "exposure_confidence": 0.91}
    """

    def __init__(
        self,
        checkpoint_path: str = DEFAULT_CHECKPOINT,
        device: str = "cpu",
        max_length: int = 128,
    ):
        self.device = torch.device(device)
        self.max_length = max_length

        # Load tokenizer
        self.tokenizer = get_tokenizer()

        # Load model
        self.model = SafetySignalClassifier(
            freeze_encoder=False,
            n_hazard_classes=len(HAZARD_LABELS),
            n_exposure_classes=len(EXPOSURE_LABELS),
        )

        resolved_path = _resolve_checkpoint_path(checkpoint_path)
        if resolved_path:
            checkpoint = torch.load(
                resolved_path,
                map_location=self.device,
                weights_only=True,
            )
            self.model.load_state_dict(checkpoint["model_state_dict"])
            self._loaded = True
        else:
            self._loaded = False

        self.model.to(self.device)
        self.model.eval()

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def predict(self, narrative: str) -> dict:
        """
        Predict hazard and exposure from a narrative.

        Returns:
            {
                "hazard": str or None,
                "exposure": str or None,
                "hazard_confidence": float,
                "exposure_confidence": float,
                "method": "ml"
            }
        """
        if not narrative or not narrative.strip():
            return {
                "hazard": None,
                "exposure": None,
                "hazard_confidence": 0.0,
                "exposure_confidence": 0.0,
                "method": "ml",
            }

        # Tokenize
        encoded = self.tokenizer(
            narrative,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        input_ids = encoded["input_ids"].to(self.device)
        attention_mask = encoded["attention_mask"].to(self.device)

        # Predict
        with torch.no_grad():
            haz_logits, exp_logits = self.model(input_ids, attention_mask)

        # Softmax probabilities
        haz_probs = torch.softmax(haz_logits, dim=1).squeeze(0).cpu().numpy()
        exp_probs = torch.softmax(exp_logits, dim=1).squeeze(0).cpu().numpy()

        haz_idx = int(np.argmax(haz_probs))
        exp_idx = int(np.argmax(exp_probs))

        haz_conf = float(haz_probs[haz_idx])
        exp_conf = float(exp_probs[exp_idx])

        # Map indices to labels (index 0 = "null")
        hazard = HAZARD_LABELS[haz_idx] if haz_idx != 0 else None
        exposure = EXPOSURE_LABELS[exp_idx] if exp_idx != 0 else None

        return {
            "hazard": hazard,
            "exposure": exposure,
            "hazard_confidence": round(haz_conf, 4),
            "exposure_confidence": round(exp_conf, 4),
            "method": "ml",
        }

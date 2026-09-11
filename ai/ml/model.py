"""
Dual-head safety-signal classifier.

Architecture:
    Final Narrative → all-MiniLM-L6-v2 → shared 384-dim repr
                                          ├→ Hazard head (15 classes)
                                          └→ Exposure head (9 classes)
"""

import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer


class SafetySignalClassifier(nn.Module):
    """Dual-head multiclass classifier on a shared transformer encoder."""

    def __init__(
        self,
        encoder_name: str = "all-MiniLM-L6-v2",
        n_hazard_classes: int = 15,
        n_exposure_classes: int = 9,
        dropout: float = 0.1,
        freeze_encoder: bool = True,
    ):
        super().__init__()

        # Resolve sentence-transformers model name to HF hub path
        hf_name = (f"sentence-transformers/{encoder_name}"
                    if "/" not in encoder_name else encoder_name)

        self.encoder = AutoModel.from_pretrained(
            hf_name, attn_implementation="eager"
        )
        self.encoder_dim = self.encoder.config.hidden_size  # 384

        self.hazard_head = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(self.encoder_dim, n_hazard_classes),
        )
        self.exposure_head = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(self.encoder_dim, n_exposure_classes),
        )

        if freeze_encoder:
            self.freeze_encoder()

    def freeze_encoder(self):
        """Freeze all encoder parameters."""
        for param in self.encoder.parameters():
            param.requires_grad = False

    def unfreeze_encoder(self):
        """Unfreeze all encoder parameters for fine-tuning."""
        for param in self.encoder.parameters():
            param.requires_grad = True

    def _mean_pool(self, last_hidden_state, attention_mask):
        """Mean pooling over non-padding tokens."""
        mask_expanded = attention_mask.unsqueeze(-1).expand(
            last_hidden_state.size()
        ).float()
        sum_embeddings = torch.sum(last_hidden_state * mask_expanded, dim=1)
        sum_mask = torch.clamp(mask_expanded.sum(dim=1), min=1e-9)
        return sum_embeddings / sum_mask

    def forward(self, input_ids, attention_mask):
        """
        Args:
            input_ids: (batch, seq_len)
            attention_mask: (batch, seq_len)

        Returns:
            hazard_logits: (batch, n_hazard_classes)
            exposure_logits: (batch, n_exposure_classes)
        """
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
        )
        pooled = self._mean_pool(outputs.last_hidden_state, attention_mask)

        hazard_logits = self.hazard_head(pooled)
        exposure_logits = self.exposure_head(pooled)

        return hazard_logits, exposure_logits


def get_tokenizer(encoder_name: str = "all-MiniLM-L6-v2"):
    """Load the tokenizer for the encoder."""
    hf_name = (f"sentence-transformers/{encoder_name}"
                if "/" not in encoder_name else encoder_name)
    return AutoTokenizer.from_pretrained(hf_name)

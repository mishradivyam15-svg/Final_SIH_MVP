FROM python:3.11-slim

WORKDIR /app

# pymupdf needs a compiler toolchain to build on some slim-image versions.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/requirements.txt

# The CPU-only wheel is a fraction of the size of the default (CUDA-bundled)
# PyPI build and this Space has no GPU — installing it first means the
# later `-r requirements.txt` sees torch already satisfied and skips it.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY ai ./ai
COPY backend ./backend

# The base sentence-transformer encoder (all-MiniLM-L6-v2 — a small, public
# model, unlike our own fine-tuned checkpoint below) is pre-downloaded here
# so it's baked into the image. Without this, every cold start had to hit
# the Hugging Face Hub at runtime to fetch it, and Cloud Run's shared
# egress IPs get rate-limited (HTTP 429) doing that under real traffic —
# this used both by ai/ml/model.py's encoder and ai/embeddings.py's
# SentenceTransformer, so warming either call populates the shared cache
# both read from.
RUN python -c "from transformers import AutoModel, AutoTokenizer; \
    AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2'); \
    AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')"

# best_model.pt — our own fine-tuned checkpoint — is intentionally NOT
# copied here. It's gitignored (too large for a normal commit) and is
# downloaded from the Hugging Face Hub on first use instead, authenticated
# via the HF_TOKEN secret for a higher rate limit. See ai/ml/inference.py.

# Hugging Face Docker Spaces route traffic to port 7860 by default.
ENV PORT=7860
EXPOSE 7860

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "7860"]

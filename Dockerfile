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

# best_model.pt is intentionally not copied here — it's gitignored (too
# large for a normal commit) and is downloaded from the Hugging Face Hub
# on first use instead. See ai/ml/inference.py.

# Hugging Face Docker Spaces route traffic to port 7860 by default.
ENV PORT=7860
EXPOSE 7860

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "7860"]

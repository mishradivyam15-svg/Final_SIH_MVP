"""
Entry point for running the SIF Precursor backend.

Usage:
    python -m backend.main
    python backend/main.py
"""

import uvicorn


def main():
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()

"""
MongoDB connection for persistent storage.

Replaces the plain-dict in-memory store in backend/db.py — without this,
every server restart (including a host putting the process to sleep)
silently wiped all submitted reports and precursors.
"""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

# Loads the repo-root .env into the process environment. Safe to call
# even when the backend is started with real env vars already set
# (e.g. in a hosted deployment) — load_dotenv never overrides an
# existing value by default.
load_dotenv()

_DB_NAME = "sif_precursor"


@lru_cache(maxsize=1)
def get_db() -> Database:
    """Return the MongoDB database handle, creating the client on first use."""

    uri = os.environ.get("MONGODB_URI")
    if not uri:
        raise RuntimeError(
            "MONGODB_URI is not set. Add a MongoDB Atlas connection string "
            "to .env as MONGODB_URI=mongodb+srv://... (see .env.example)."
        )

    client = MongoClient(uri, serverSelectionTimeoutMS=8000)
    # Fail fast on a bad URI/credentials/network instead of surfacing a
    # confusing error on the first real request.
    client.admin.command("ping")
    return client[_DB_NAME]

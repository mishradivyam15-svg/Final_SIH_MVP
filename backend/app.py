"""
FastAPI application factory for the SIF Precursor backend.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.routes import router, api_router


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""

    app = FastAPI(
        title="SIF Precursor API",
        description=(
            "Backend integration layer for the SIF (Serious Injury "
            "and Fatality) Precursor detection pipeline.  Wraps the "
            "frozen Extraction v1 engine and provides placeholder "
            "contracts for the future AI-2 relationship / precursor "
            "analysis."
        ),
        version="0.1.0",
    )

    # ---------------------------------------------------------
    # CORS — allow the frontend dev server to connect.
    # ---------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---------------------------------------------------------
    # Register routes
    # ---------------------------------------------------------
    app.include_router(router)
    app.include_router(api_router)

    # ---------------------------------------------------------
    # Root redirect to interactive docs
    # ---------------------------------------------------------
    @app.get("/", include_in_schema=False)
    def root_redirect():
        return RedirectResponse(url="/docs")

    return app


app = create_app()

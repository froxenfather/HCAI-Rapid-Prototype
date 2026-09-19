"""FastAPI application entrypoint.

Run locally with:

    uvicorn app.main:app --reload

from inside the `ai/` directory.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import get_settings
from app.services.errors import AppHTTPError

logging.basicConfig(level=logging.INFO)

settings = get_settings()

app = FastAPI(
    title="CaringBridge AI Backend",
    description="Generates first-post drafts for CaringBridge from onboarding "
    "information, with unresolved details represented as canonical placeholders.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppHTTPError)
async def app_http_error_handler(request: Request, exc: AppHTTPError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error, "message": exc.message},
    )


app.include_router(router)

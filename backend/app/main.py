"""FastAPI main application entrypoint for VeriDocs AI."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.api.health import router as health_router
from backend.app.api.sessions import router as sessions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("VeriDocs AI backend starting up...")
    settings.TEMP_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    yield
    logger.info("VeriDocs AI backend shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Evidence-First Financial Document Intelligence and Fraud-Consistency Checker",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "error_type": "validation_error"},
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.error("Unhandled server exception", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "error_type": "internal_error"},
    )


# Include API routers
app.include_router(health_router, prefix=settings.API_PREFIX, tags=["System"])
app.include_router(sessions_router, prefix=settings.API_PREFIX, tags=["Sessions & Verification"])


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": f"{settings.API_PREFIX}/health",
    }

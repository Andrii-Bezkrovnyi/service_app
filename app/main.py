from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.github_routes import github_router
from app.api.storage_routes import storage_router
from app.core.exceptions import (
    ApplicationError,
    GitHubAPIError,
    GitHubRateLimitError,
    GitHubResourceNotFoundError,
    GitHubUnexpectedResponseError,
    StorageItemAlreadyExistsError,
    StorageItemNotFoundError,
)
from app.dependencies import close_cached_client

# Constants to avoid magic numbers (WPS432)
DEFAULT_PORT = 8000
LOCAL_HOST = "127.0.0.1"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifecycle events."""
    yield
    close_cached_client()


def _handle_application_error(request: Request, exc: ApplicationError) -> JSONResponse:
    """Handle custom application errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


def _handle_key_error(request: Request, exc: KeyError) -> JSONResponse:
    """Handle standard KeyError by mapping it to 404 Not Found."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc).strip("'")},
    )


def _register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers to reduce expression count in create_app.
    Fixes WPS213.
    """
    app.add_exception_handler(StorageItemAlreadyExistsError, _handle_application_error)
    app.add_exception_handler(StorageItemNotFoundError, _handle_application_error)
    app.add_exception_handler(GitHubAPIError, _handle_application_error)
    app.add_exception_handler(GitHubRateLimitError, _handle_application_error)
    app.add_exception_handler(GitHubResourceNotFoundError, _handle_application_error)
    app.add_exception_handler(GitHubUnexpectedResponseError, _handle_application_error)
    app.add_exception_handler(KeyError, _handle_key_error)


def healthcheck() -> dict[str, str]:
    """Simple health check endpoint. Fixed WPS430."""
    return {"status": "ok"}


def create_app() -> FastAPI:
    """Initialize and configure the FastAPI application."""
    app = FastAPI(
        title="GitHub SDK Sandbox",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Register routers
    app.include_router(github_router)
    app.include_router(storage_router)

    # Healthcheck route defined outside to fix WPS430
    app.get("/health")(healthcheck)

    # Batch register handlers to fix WPS213
    _register_exception_handlers(app)

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=LOCAL_HOST,
        port=DEFAULT_PORT,
        reload=True,
        log_level="info",
        access_log=True,
    )

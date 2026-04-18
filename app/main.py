from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import github_router, storage_router
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


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    close_cached_client()


def create_app() -> FastAPI:
    app = FastAPI(
        title="GitHub SDK Sandbox",
        version="1.0.0",
        lifespan=lifespan
    )

    # Подключаем роутеры
    app.include_router(github_router)
    app.include_router(storage_router)

    # Регистрация обработчиков исключений
    app.add_exception_handler(StorageItemAlreadyExistsError, _handle_application_error)
    app.add_exception_handler(StorageItemNotFoundError, _handle_application_error)
    app.add_exception_handler(GitHubAPIError, _handle_application_error)
    app.add_exception_handler(GitHubRateLimitError, _handle_application_error)
    app.add_exception_handler(GitHubResourceNotFoundError, _handle_application_error)
    app.add_exception_handler(GitHubUnexpectedResponseError, _handle_application_error)
    app.add_exception_handler(KeyError, _handle_key_error)

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


def _handle_application_error(request: Request, exc: ApplicationError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


def _handle_key_error(request: Request, exc: KeyError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc).strip("'")},
    )


app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

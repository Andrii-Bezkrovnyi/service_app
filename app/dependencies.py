from __future__ import annotations

from functools import lru_cache

from app.clients.github_client import GitHubClient
from app.core.config import Settings, get_settings
from app.services.github_service import GitHubService
from app.storage.in_memory import InMemoryStorage


@lru_cache(maxsize=1)
def get_cached_settings() -> Settings:
    return get_settings()


@lru_cache(maxsize=1)
def get_storage() -> InMemoryStorage:
    return InMemoryStorage()


@lru_cache(maxsize=1)
def get_github_client() -> GitHubClient:
    return GitHubClient(get_cached_settings())


@lru_cache(maxsize=1)
def get_github_service() -> GitHubService:
    return GitHubService(client=get_github_client(), storage=get_storage())


def close_cached_client() -> None:
    get_github_client().close()

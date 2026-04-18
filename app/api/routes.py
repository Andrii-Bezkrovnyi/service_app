from __future__ import annotations

from typing import Any, Dict, List, Union

from fastapi import APIRouter, Body, Depends, status

from app.dependencies import get_github_service, get_storage
from app.schemas.repo_schemas import RepoListResponse, RepoResponse
from app.services.github_service import GitHubService
from app.storage.in_memory import InMemoryStorage

# Typing alias for storage payloads, which can be any JSON-serializable structure
StoragePayload = Dict[str, Any]

github_router = APIRouter(prefix="/github", tags=["GitHub"])
storage_router = APIRouter(prefix="/storage", tags=["Storage"])


# --- GitHub Endpoints ---
@github_router.get(
    "/users/{username}",
    summary="Get GitHub user profile",
    response_description="User profile data"
)
def get_user(
    username: str,
    refresh: bool = False,
    service: GitHubService = Depends(get_github_service),
) -> Dict[str, Any]:
    """Endpoint to fetch GitHub user profile data. Supports optional cache refresh."""
    return service.get_user(username=username, refresh=refresh)


@github_router.get(
    "/users/{username}/repos",
    response_model=RepoListResponse,
    summary="List user repositories"
)
def list_user_repos(
    username: str,
    refresh: bool = False,
    per_page: int = 10,
    service: GitHubService = Depends(get_github_service),
) -> Any:
    """
    Endpoint to list repositories of a GitHub user.
    Supports optional cache refresh and pagination.
    """
    return service.list_user_repos(
        username=username,
        refresh=refresh,
        per_page=per_page,
    )


@github_router.get(
    "/repos/{owner}/{repo}",
    response_model=RepoResponse,
    summary="Get GitHub repository details"
)
def get_repo(
    owner: str,
    repo: str,
    refresh: bool = False,
    service: GitHubService = Depends(get_github_service),
) -> Any:
    return service.get_repo(owner=owner, repo=repo, refresh=refresh)


# --- Storage Endpoints ---
@storage_router.get(
    "/keys",
    summary="List all storage keys",
    response_description="List of available keys in storage"
)
def list_storage_keys(
    storage: InMemoryStorage = Depends(get_storage)
) -> Dict[str, List[str]]:
    """Endpoint to list all keys currently stored in the in-memory storage."""
    return {"keys": storage.list_keys()}


@storage_router.get(
    "/{key}",
    summary="Read item from storage",
    response_description="The stored storage_value associated with the key"
)
def read_storage_item(
    key: str,
    storage: InMemoryStorage = Depends(get_storage),
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Endpoint to read a storage_value from storage by its key.
    Raises 404 if key is not found.
    """
    value = storage.read(key)
    if value is None:
        raise KeyError(f"Storage item '{key}' was not found.")
    return value


@storage_router.post(
    "/{key}",
    status_code=status.HTTP_201_CREATED,
    summary="Create new storage item"
)
def create_storage_item(
    key: str,
    value: StoragePayload = Body(...),
    storage: InMemoryStorage = Depends(get_storage),
) -> Dict[str, Any]:
    """Endpoint to create a new storage item. Raises 400 if key already exists."""
    storage.create(key, value)
    return {
        "key": key,
        "storage_value": value,
    }


@storage_router.put(
    "/{key}",
    summary="Update existing storage item"
)
def update_storage_item(
    key: str,
    value: StoragePayload = Body(...),
    storage: InMemoryStorage = Depends(get_storage),
) -> Dict[str, Any]:
    """Endpoint to update an existing storage item. Raises 404 if key is not found."""
    storage.update(key, value)
    return {
        "key": key,
        "storage_value": value,
    }


@storage_router.delete(
    "/{key}",
    summary="Delete item from storage"
)
def delete_storage_item(
    key: str,
    storage: InMemoryStorage = Depends(get_storage),
) -> Dict[str, str]:
    """Endpoint to delete a storage item by its key. Raises 404 if key is not found."""
    storage.delete(key)
    return {"deleted": key}

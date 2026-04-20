from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends

from app.dependencies import get_github_service
from app.schemas.repo_schemas import RepoListResponse, RepoResponse
from app.services.github_service import GitHubService

# Typing alias for storage payloads, which can be any JSON-serializable structure
StoragePayload = Dict[str, Any]

github_router = APIRouter(prefix="/github", tags=["GitHub"])


# --- GitHub Endpoints ---
@github_router.get(
    "/users/{username}",
    summary="Get GitHub user profile",
    response_description="User profile data"
)
def get_user(
        username: str,
        refresh: bool = False,
        service: GitHubService = Depends(get_github_service),  # noqa: WPS404
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
        service: GitHubService = Depends(get_github_service),  # noqa: WPS404
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
        service: GitHubService = Depends(get_github_service),  # noqa: WPS404
) -> Any:
    return service.get_repo(owner=owner, repo=repo, refresh=refresh)

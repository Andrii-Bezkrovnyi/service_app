from __future__ import annotations

from collections.abc import Mapping
from http import HTTPStatus
from typing import TypeAlias, cast

import httpx

from app.core.config import Settings
from app.core.exceptions import (
    GitHubAPIError,
    GitHubRateLimitError,
    GitHubResourceNotFoundError,
    GitHubUnexpectedResponseError,
)

GitHubObject: TypeAlias = dict[str, object]
GitHubList: TypeAlias = list[GitHubObject]


class GitHubClient:
    def __init__(
        self,
        settings: Settings,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if settings.github_token is not None and settings.github_token != "":
            headers["Authorization"] = f"Bearer {settings.github_token}"

        self._client = httpx.Client(
            base_url=settings.github_base_url,
            headers=headers,
            timeout=settings.github_timeout_seconds,
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def get_user(self, username: str) -> GitHubObject:
        response = self._request("GET", f"/users/{username}")
        return self._ensure_object(response)

    def get_repo(self, owner: str, repo: str) -> GitHubObject:
        response = self._request("GET", f"/repos/{owner}/{repo}")
        return self._ensure_object(response)

    def list_user_repos(self, username: str, per_page: int = 10) -> GitHubList:
        params = {
            "per_page": per_page,
        }
        response = self._request("GET", f"/users/{username}/repos", params=params)
        return self._ensure_list(response)

    def _request(
        self,
        method: str,
        path: str,
        params: Mapping[str, object] | None = None,
    ) -> httpx.Response:
        response = self._client.request(method, path, params=params)

        if response.status_code == HTTPStatus.NOT_FOUND:
            raise GitHubResourceNotFoundError(f"GitHub resource '{path}' was not found.")

        if response.status_code == HTTPStatus.FORBIDDEN:
            if response.headers.get("X-RateLimit-Remaining") == "0":
                raise GitHubRateLimitError("GitHub API rate limit was exceeded.")
            raise GitHubAPIError(f"GitHub API returned 403 for '{path}'.")

        if response.status_code >= HTTPStatus.BAD_REQUEST:
            raise GitHubAPIError(
                f"GitHub API returned HTTP {response.status_code} for '{path}'.",
            )

        return response

    def _ensure_object(self, response: httpx.Response) -> GitHubObject:
        data = response.json()
        if not isinstance(data, dict):
            raise GitHubUnexpectedResponseError("Expected a JSON object from GitHub.")
        return cast(GitHubObject, data)

    def _ensure_list(self, response: httpx.Response) -> GitHubList:
        data = response.json()
        if not isinstance(data, list):
            raise GitHubUnexpectedResponseError("Expected a JSON list from GitHub.")

        result: GitHubList = []
        for item in data:
            if not isinstance(item, dict):
                raise GitHubUnexpectedResponseError("Expected a list of JSON objects from GitHub.")
            result.append(cast(GitHubObject, item))

        return result

from __future__ import annotations

from http import HTTPStatus
from typing import TypeAlias, Sequence

import httpx

from app.core.config import Settings
from app.core.exceptions import (
    GitHubAPIError,
    GitHubRateLimitError,
    GitHubResourceNotFoundError
)
from app.core.json_utils import parse_dict, parse_list
from app.core.types import GitHubList, GitHubObject

ScalarQueryValue: TypeAlias = str | int | float | bool | None
SequenceQueryValue: TypeAlias = Sequence[ScalarQueryValue]

QueryParamValue: TypeAlias = ScalarQueryValue | SequenceQueryValue
QueryParams: TypeAlias = dict[str, QueryParamValue]


class GitHubClient:
    def __init__(
            self,
            settings: Settings,
            transport: httpx.BaseTransport | None = None,
    ) -> None:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
        }

        if settings.github_token:
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
        return parse_dict(response)

    def get_repo(self, owner: str, repo: str) -> GitHubObject:
        response = self._request("GET", f"/repos/{owner}/{repo}")
        return parse_dict(response)

    def list_user_repos(self, username: str, per_page: int = 10) -> GitHubList:
        response = self._request(
            "GET",
            f"/users/{username}/repos",
            req_params={"per_page": per_page},
        )
        return parse_list(response)

    def _request(
            self,
            method: str,
            path: str,
            req_params: QueryParams | None = None,
    ) -> httpx.Response:
        response = self._client.request(method, path, params=req_params)
        status = response.status_code

        if status == HTTPStatus.NOT_FOUND:
            raise GitHubResourceNotFoundError(
                f"GitHub resource '{path}' was not found.",
            )

        if status >= HTTPStatus.FORBIDDEN:
            if status == HTTPStatus.FORBIDDEN:
                if response.headers.get("X-RateLimit-Remaining") == "0":
                    raise GitHubRateLimitError(
                        "GitHub API rate limit was exceeded.",
                    )
            raise GitHubAPIError(
                f"GitHub API error {status} for '{path}'.",
            )

        return response

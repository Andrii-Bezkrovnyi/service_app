from __future__ import annotations

from collections.abc import Callable
from typing import cast, Mapping

from app.clients.github_client import GitHubClient
from app.core.types import GitHubObject, GitHubList
# from app.clients.github_client import GitHubClient, GitHubList, GitHubObject
from app.storage.base import StorageProtocol, StorageValue


def build_storage_key(prefix: str, *parts: str) -> str:
    """Build a unique string key for storage."""
    suffix = ":".join(parts)
    return f"{prefix}:{suffix}"


def build_storage_record(
        kind: str,
        query: Mapping[str, object],
        response: StorageValue,
) -> dict[str, object]:
    """Structure the data for saving in the sandbox storage."""
    return {
        "kind": kind,
        "query": query,
        "response": response,
    }


class GitHubService:
    def __init__(self, client: GitHubClient, storage: StorageProtocol) -> None:
        """Initialize the service with a GitHub client and a storage mechanism."""
        self._client = client
        self._storage = storage

    def get_user(self, username: str, refresh: bool = False) -> GitHubObject:
        """Fetch user data, using cache if available unless refresh is True."""
        key = build_storage_key("user", username)
        query = {"username": username}
        user_data = self._get_or_fetch(
            key=key,
            kind="user",
            query=query,
            fetcher=lambda: self._client.get_user(username),
            refresh=refresh,
        )
        return cast(GitHubObject, user_data)

    def get_repo(self, owner: str, repo: str, refresh: bool = False) -> GitHubObject:
        """Fetch repository data, using cache if available unless refresh is True."""
        key = build_storage_key("repo", owner, repo)
        query = {
            "owner": owner,
            "repo": repo,
        }
        get_repo_result = self._get_or_fetch(
            key=key,
            kind="repo",
            query=query,
            fetcher=lambda: self._client.get_repo(owner, repo),
            refresh=refresh,
        )
        return cast(GitHubObject, get_repo_result)

    def list_user_repos(
            self,
            username: str,
            refresh: bool = False,
            per_page: int = 30,
    ) -> GitHubList:
        """
        Fetch a list of user repositories,
        using cache if available unless refresh is True.
        """
        key = build_storage_key("repos", username, str(per_page))
        query = {
            "username": username,
            "per_page": per_page,
        }
        user_repos = self._get_or_fetch(
            key=key,
            kind="repos",
            query=query,
            fetcher=lambda: self._client.list_user_repos(username=username,
                                                         per_page=per_page),
            refresh=refresh,
        )
        return cast(GitHubList, user_repos)

    def get_cached_value(self, key: str) -> StorageValue | None:
        """Directly access a cached value by its key."""
        return self._storage.read(key)

    def list_cached_keys(self) -> list[str]:
        """List all keys currently stored in the cache."""
        return self._storage.list_keys()

    def _get_or_fetch(
            self,
            key: str,
            kind: str,
            query: Mapping[str, object],
            fetcher: Callable[[], StorageValue],
            refresh: bool,
    ) -> StorageValue:
        """Core logic to either return cached data or fetch new data and cache it."""
        if not refresh:
            cached_value = self._storage.read(key)
            if cached_value is not None:
                return cached_value

        fetched_value = fetcher()
        record = build_storage_record(kind=kind, query=query, response=fetched_value)

        if self._storage.read(key) is None:
            self._storage.create(key, record)
        else:
            self._storage.update(key, record)

        return record

from __future__ import annotations

from collections.abc import Callable
from typing import cast

from app.clients.github import GitHubClient, GitHubList, GitHubObject
from app.storage.base import StorageProtocol, StorageValue


class GitHubService:
    def __init__(self, client: GitHubClient, storage: StorageProtocol) -> None:
        self._client = client
        self._storage = storage

    def get_user(self, username: str, refresh: bool = False) -> GitHubObject:
        key = self._build_key("user", username)
        query = {"username": username}
        result = self._get_or_fetch(
            key=key,
            kind="user",
            query=query,
            fetcher=lambda: self._client.get_user(username),
            refresh=refresh,
        )
        return cast(GitHubObject, result)

    def get_repo(self, owner: str, repo: str, refresh: bool = False) -> GitHubObject:
        key = self._build_key("repo", owner, repo)
        query = {
            "owner": owner,
            "repo": repo,
        }
        result = self._get_or_fetch(
            key=key,
            kind="repo",
            query=query,
            fetcher=lambda: self._client.get_repo(owner, repo),
            refresh=refresh,
        )
        return cast(GitHubObject, result)

    def list_user_repos(
        self,
        username: str,
        refresh: bool = False,
        per_page: int = 30,
    ) -> GitHubList:
        key = self._build_key("repos", username, str(per_page))
        query = {
            "username": username,
            "per_page": per_page,
        }
        result = self._get_or_fetch(
            key=key,
            kind="repos",
            query=query,
            fetcher=lambda: self._client.list_user_repos(username=username, per_page=per_page),
            refresh=refresh,
        )
        return cast(GitHubList, result)

    def get_cached_value(self, key: str) -> StorageValue | None:
        return self._storage.read(key)

    def list_cached_keys(self) -> list[str]:
        return self._storage.list_keys()

    def _get_or_fetch(
        self,
        key: str,
        kind: str,
        query: dict[str, object],
        fetcher: Callable[[], StorageValue],
        refresh: bool,
    ) -> StorageValue:
        if not refresh:
            cached_value = self._storage.read(key)
            if cached_value is not None:
                return cached_value

        fetched_value = fetcher()
        record = self._build_record(kind=kind, query=query, response=fetched_value)

        if self._storage.read(key) is None:
            self._storage.create(key, record)
        else:
            self._storage.update(key, record)

        return record

    def _build_record(
        self,
        kind: str,
        query: dict[str, object],
        response: StorageValue,
    ) -> dict[str, object]:
        return {
            "kind": kind,
            "query": query,
            "response": response,
        }

    def _build_key(self, prefix: str, *parts: str) -> str:
        suffix = ":".join(parts)
        return f"{prefix}:{suffix}"

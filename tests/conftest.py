from __future__ import annotations

import pytest

from app.clients.github_client import GitHubClient
from app.core.config import Settings
from app.core.types import GitHubList, GitHubObject
from app.services.github_service import GitHubService
from app.storage.in_memory import InMemoryStorage

TIMEOUT_PERIOD = 10.0


class FakeGitHubClient(GitHubClient):
    def __init__(self) -> None:
        self.user_calls = 0
        self.repo_calls = 0
        self.repos_calls = 0

        settings = Settings(
            github_token="fake_token",
            github_base_url="https://api.github.com",
            github_timeout_seconds=TIMEOUT_PERIOD,
        )
        super().__init__(settings=settings)

    def get_user(self, username: str) -> GitHubObject:
        self.user_calls += 1
        return {"login": username, "id": 1}

    def get_repo(self, owner: str, repo: str) -> GitHubObject:
        self.repo_calls += 1
        return {"full_name": f"{owner}/{repo}", "private": False}

    def list_user_repos(
            self,
            username: str,
            per_page: int = 10,
    ) -> GitHubList:
        self.repos_calls += 1
        return [
            {
                "full_name": f"{username}/repo-1",
                "private": False,
            },
        ]


@pytest.fixture
def service() -> tuple[GitHubService, FakeGitHubClient, InMemoryStorage]:
    client = FakeGitHubClient()
    storage = InMemoryStorage()
    service = GitHubService(client=client, storage=storage)
    return service, client, storage

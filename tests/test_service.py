from __future__ import annotations

from app.clients.github_client import GitHubClient, GitHubList, GitHubObject
from app.core.config import Settings
from app.services.github_service import GitHubService
from app.storage.in_memory import InMemoryStorage


class FakeGitHubClient(GitHubClient):
    """Fake GitHub client for testing purposes."""

    def __init__(self) -> None:
        """Initialize call counters and parent with test settings."""
        self.user_calls = 0
        self.repo_calls = 0
        self.repos_calls = 0

        test_settings = Settings(
            github_token="fake_token",
            github_base_url="https://api.github.com",
            github_timeout_seconds=10.0,
        )
        super().__init__(settings=test_settings)

    def get_user(self, username: str) -> GitHubObject:
        """Simulate fetching a user."""
        self.user_calls += 1
        return {"login": username, "id": 1}

    def get_repo(self, owner: str, repo: str) -> GitHubObject:
        """Simulate fetching a repository."""
        self.repo_calls += 1
        return {"full_name": f"{owner}/{repo}", "private": False}

    def list_user_repos(
        self,
        username: str,
        per_page: int = 10,
    ) -> GitHubList:
        """Simulate listing repositories."""
        self.repos_calls += 1
        return [
            {
                "full_name": f"{username}/repo-1",
                "private": False,
            },
        ]


def test_service_fetches_and_caches_user() -> None:
    """Test that user data is fetched once and then served from cache."""
    client = FakeGitHubClient()
    storage = InMemoryStorage()
    service = GitHubService(client=client, storage=storage)

    user_record = service.get_user("octocat")
    cached_user_record = service.get_user("octocat")

    assert user_record == cached_user_record
    assert client.user_calls == 1

    stored_entry = storage.read("user:octocat")

    assert stored_entry is not None
    assert stored_entry == user_record
    assert stored_entry["response"]["login"] == "octocat"


def test_service_can_refresh_repo() -> None:
    """Test that the refresh flag forces a new API call."""
    client = FakeGitHubClient()
    storage = InMemoryStorage()
    service = GitHubService(client=client, storage=storage)

    service.get_repo("octo", "hello")
    service.get_repo("octo", "hello", refresh=True)

    assert client.repo_calls == 2


def test_service_lists_repos() -> None:
    """Test listing repositories through the service layer."""
    client = FakeGitHubClient()
    storage = InMemoryStorage()
    service = GitHubService(client=client, storage=storage)

    repos_record = service.list_user_repos("octocat")

    assert isinstance(repos_record, dict)
    assert "response" in repos_record

    repositories = repos_record["response"]
    assert isinstance(repositories, list)
    assert repositories[0]["full_name"] == "octocat/repo-1"
    assert client.repos_calls == 1
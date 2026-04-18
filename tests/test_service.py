from __future__ import annotations

from app.services.github_service import GitHubService
from app.storage.in_memory import InMemoryStorage


class FakeGitHubClient:
    def __init__(self) -> None:
        self.user_calls = 0
        self.repo_calls = 0
        self.repos_calls = 0

    def get_user(self, username: str) -> dict[str, object]:
        self.user_calls += 1
        return {
            "login": username,
            "id": 1,
        }

    def get_repo(self, owner: str, repo: str) -> dict[str, object]:
        self.repo_calls += 1
        return {
            "full_name": f"{owner}/{repo}",
            "private": False,
        }

    def list_user_repos(self, username: str, per_page: int = 10) -> list[
        dict[str, object]]:
        self.repos_calls += 1
        return [
            {
                "full_name": f"{username}/repo-1",
                "private": False,
            },
        ]


def test_service_fetches_and_caches_user() -> None:
    client = FakeGitHubClient()
    storage = InMemoryStorage()
    service = GitHubService(client=client, storage=storage)

    first_result = service.get_user("octocat")
    second_result = service.get_user("octocat")

    assert first_result == second_result
    assert client.user_calls == 1
    assert storage.read("user:octocat") == first_result


def test_service_can_refresh_repo() -> None:
    client = FakeGitHubClient()
    storage = InMemoryStorage()
    service = GitHubService(client=client, storage=storage)

    first_result = service.get_repo("octo", "hello")
    second_result = service.get_repo("octo", "hello", refresh=True)

    assert first_result == second_result
    assert client.repo_calls == 2
    assert storage.read("repo:octo:hello") == second_result


def test_service_lists_repos() -> None:
    client = FakeGitHubClient()
    storage = InMemoryStorage()
    service = GitHubService(client=client, storage=storage)

    result = service.list_user_repos("octocat")

    assert isinstance(result, dict)
    assert "response" in result

    repos = result["response"]
    assert isinstance(repos, list)
    assert repos[0]["full_name"] == "octocat/repo-1"
    assert client.repos_calls == 1

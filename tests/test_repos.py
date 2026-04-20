def test_service_can_refresh_repo(service) -> None:
    svc, client, _ = service

    svc.get_repo("octo", "hello")
    svc.get_repo("octo", "hello", refresh=True)

    assert client.repo_calls == 2


def test_service_caches_repo(service) -> None:
    svc, client, _ = service

    svc.get_repo("octo", "hello")
    svc.get_repo("octo", "hello")

    assert client.repo_calls == 1


def test_service_lists_repos(service) -> None:
    svc, client, _ = service

    repos_record = svc.list_user_repos("octocat")

    repositories = repos_record["response"]
    assert repositories[0]["full_name"] == "octocat/repo-1"

    assert client.repos_calls == 1


def test_service_caches_repos(service) -> None:
    svc, client, _ = service

    svc.list_user_repos("octocat")
    svc.list_user_repos("octocat")

    assert client.repos_calls == 1

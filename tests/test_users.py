from typing import Any


def test_service_fetches_user(service: Any) -> None:
    svc, client, _ = service

    user_record = svc.get_user("octocat")

    assert user_record["response"]["login"] == "octocat"
    assert client.user_calls == 1


def test_service_caches_user(service: Any) -> None:
    svc, client, _ = service

    svc.get_user("octocat")
    svc.get_user("octocat")

    assert client.user_calls == 1


def test_service_stores_user_in_cache(service: Any) -> None:
    svc, _, storage = service

    user_record = svc.get_user("octocat")
    stored = storage.read("user:octocat")

    assert stored is not None
    assert stored == user_record

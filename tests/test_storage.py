from __future__ import annotations

from app.core.exceptions import StorageItemAlreadyExistsError, StorageItemNotFoundError
from app.storage.in_memory import InMemoryStorage


def test_storage_crud_cycle() -> None:
    storage = InMemoryStorage()
    storage.create("alpha", {"value": 1})

    assert storage.read("alpha") == {"value": 1}

    storage.update("alpha", {"value": 2})
    assert storage.read("alpha") == {"value": 2}

    storage.delete("alpha")
    assert storage.read("alpha") is None


def test_storage_create_duplicate_raises() -> None:
    storage = InMemoryStorage()
    storage.create("alpha", {"value": 1})

    try:
        storage.create("alpha", {"value": 2})
    except StorageItemAlreadyExistsError as exc:
        assert "already exists" in str(exc)
    else:
        raise AssertionError("Expected StorageItemAlreadyExistsError")


def test_storage_update_missing_raises() -> None:
    storage = InMemoryStorage()

    try:
        storage.update("missing", {"value": 2})
    except StorageItemNotFoundError as exc:
        assert "not found" in str(exc)
    else:
        raise AssertionError("Expected StorageItemNotFoundError")

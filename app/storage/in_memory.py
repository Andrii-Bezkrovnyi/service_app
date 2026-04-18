from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.exceptions import StorageItemAlreadyExistsError, StorageItemNotFoundError
from app.storage.base import StorageProtocol, StorageValue


@dataclass(slots=True)
class StorageEntry:
    value: StorageValue
    created_at: datetime
    updated_at: datetime


class InMemoryStorage(StorageProtocol):
    def __init__(self) -> None:
        self._items: dict[str, StorageEntry] = {}

    def create(self, key: str, value: StorageValue) -> None:
        if key in self._items:
            raise StorageItemAlreadyExistsError(f"Storage item '{key}' already exists.")

        now = datetime.now(tz=timezone.utc)
        self._items[key] = StorageEntry(
            value=value,
            created_at=now,
            updated_at=now,
        )

    def read(self, key: str) -> StorageValue | None:
        entry = self._items.get(key)
        if entry is None:
            return None

        return entry.value

    def update(self, key: str, value: StorageValue) -> None:
        entry = self._items.get(key)
        if entry is None:
            raise StorageItemNotFoundError(f"Storage item '{key}' was not found.")

        self._items[key] = StorageEntry(
            value=value,
            created_at=entry.created_at,
            updated_at=datetime.now(tz=timezone.utc),
        )

    def delete(self, key: str) -> None:
        if key not in self._items:
            raise StorageItemNotFoundError(f"Storage item '{key}' was not found.")

        del self._items[key]

    def list_keys(self) -> list[str]:
        return list(self._items.keys())

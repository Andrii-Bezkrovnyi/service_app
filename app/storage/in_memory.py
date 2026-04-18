from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.exceptions import StorageItemAlreadyExistsError, StorageItemNotFoundError
from app.storage.base import StorageProtocol, StorageValue


@dataclass(slots=True)
class StorageEntry:
    """Represents an entry in the internal storage with timestamps."""

    storage_value: StorageValue
    created_at: datetime
    updated_at: datetime


class InMemoryStorage(StorageProtocol):
    """
    In-memory implementation of a sandbox data storage.
    Uses a dictionary to store data with CRUD methods.
    """

    def __init__(self) -> None:
        """Initialize the storage with an empty dictionary."""
        self._storage_entries: dict[str, StorageEntry] = {}

    def create(self, key: str, storage_value: StorageValue) -> None:
        """
        Create a new storage item with the given key and storage_value.

        Raises:
            StorageItemAlreadyExistsError: If the key is already present.
        """
        if key in self._storage_entries:
            raise StorageItemAlreadyExistsError(f"Storage item '{key}' already exists.")

        now = datetime.now(tz=timezone.utc)
        self._storage_entries[key] = StorageEntry(
            storage_value=storage_value,
            created_at=now,
            updated_at=now,
        )

    def read(self, key: str) -> StorageValue | None:
        """
        Read the storage_value of a storage item by its key.

        Returns:
            The stored storage_value or None if the key is not found.
        """
        entry = self._storage_entries.get(key)
        if entry is None:
            return None

        return entry.storage_value

    def update(self, key: str, storage_value: StorageValue) -> None:
        """
        Update the storage_value of an existing storage item by its key.

        Raises:
            StorageItemNotFoundError: If the key does not exist.
        """
        existing_entry = self._storage_entries.get(key)
        if existing_entry is None:
            raise StorageItemNotFoundError(f"Storage item '{key}' was not found.")

        self._storage_entries[key] = StorageEntry(
            storage_value=storage_value,
            created_at=existing_entry.created_at,
            updated_at=datetime.now(tz=timezone.utc),
        )

    def delete(self, key: str) -> None:
        """
        Delete a storage item by its key.

        Raises:
            StorageItemNotFoundError: If the key was not found.
        """
        if key not in self._storage_entries:
            raise StorageItemNotFoundError(f"Storage item '{key}' was not found.")

        self._storage_entries.pop(key)

    def list_keys(self) -> list[str]:
        """
        List all keys currently stored.

        Returns:
            A list of string keys.
        """
        return list(self._storage_entries.keys())

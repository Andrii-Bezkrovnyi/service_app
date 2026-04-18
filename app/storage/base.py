from __future__ import annotations

from typing import Protocol, TypeAlias

StorageItem: TypeAlias = dict[str, object]

StorageValue: TypeAlias = StorageItem | list[StorageItem]


class StorageProtocol(Protocol):
    def create(self, key: str, storage_value: StorageValue) -> None:
        ...

    def read(self, key: str) -> StorageValue | None:
        ...

    def update(self, key: str, storage_value: StorageValue) -> None:
        ...

    def delete(self, key: str) -> None:
        ...

    def list_keys(self) -> list[str]:
        ...

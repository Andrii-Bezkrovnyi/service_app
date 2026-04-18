from __future__ import annotations

from typing import Protocol, TypeAlias

StorageValue: TypeAlias = dict[str, object] | list[dict[str, object]]


class StorageProtocol(Protocol):
    def create(self, key: str, value: StorageValue) -> None:
        ...

    def read(self, key: str) -> StorageValue | None:
        ...

    def update(self, key: str, value: StorageValue) -> None:
        ...

    def delete(self, key: str) -> None:
        ...

    def list_keys(self) -> list[str]:
        ...

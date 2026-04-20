from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Body, Depends, status

from app.dependencies import get_storage
from app.storage.in_memory import InMemoryStorage

# Typing alias for storage payloads, which can be any JSON-serializable structure
StoragePayload = Dict[str, Any]

storage_router = APIRouter(prefix="/storage", tags=["Storage"])


# --- Storage Endpoints ---
@storage_router.get(
    "/keys",
    summary="List all storage keys",
    response_description="List of available keys in storage"
)
def list_storage_keys(
        storage: InMemoryStorage = Depends(get_storage)  # noqa: WPS404
) -> Dict[str, List[str]]:
    """Endpoint to list all keys currently stored in the in-memory storage."""
    return {"keys": storage.list_keys()}


@storage_router.get(
    "/{key}",
    summary="Read item from storage",
    response_description="The stored storage_value associated with the key"
)
def read_storage(
        key: str,
        storage_item: InMemoryStorage = Depends(get_storage),  # noqa: WPS404
) -> dict[str, Any] | list[dict[str, Any]]:
    stored_item = storage_item.read(key)

    if stored_item:
        return stored_item

    raise KeyError(f"Storage item '{key}' was not found.")


@storage_router.post(
    "/{key}",
    status_code=status.HTTP_201_CREATED,
    summary="Create new storage item"
)
def create_storage(
        key: str,
        storage_item: StoragePayload = Body(...),  # noqa: WPS404
        storage: InMemoryStorage = Depends(get_storage),  # noqa: WPS404
) -> Dict[str, Any]:
    """Endpoint to create a new storage item. Raises 400 if key already exists."""
    storage.create(key, storage_item)
    return {
        "key": key,
        "storage_value": storage_item,
    }


@storage_router.put(
    "/{key}",
    summary="Update existing storage item"
)
def update_storage(
        key: str,
        storage_item: StoragePayload = Body(...),  # noqa: WPS404
        storage: InMemoryStorage = Depends(get_storage),  # noqa: WPS404
) -> Dict[str, Any]:
    """Endpoint to update an existing storage item. Raises 404 if key is not found."""
    storage.update(key, storage_item)
    return {
        "key": key,
        "storage_value": storage_item,
    }


@storage_router.delete(
    "/{key}",
    summary="Delete item from storage"
)
def delete_storage(
        key: str,
        storage_item: InMemoryStorage = Depends(get_storage),  # noqa: WPS404
) -> Dict[str, str]:
    """Endpoint to delete a storage item by its key. Raises 404 if key is not found."""
    storage_item.delete(key)
    return {"deleted": key}

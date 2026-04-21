from typing import Any

import httpx

from app.core.exceptions import GitHubUnexpectedResponseError
from app.core.types import GitHubList, GitHubObject


def parse_dict(response: httpx.Response) -> GitHubObject:
    response_data: Any = response.json()

    if not isinstance(response_data, dict):
        raise GitHubUnexpectedResponseError("Expected dict")

    return response_data


def parse_list(response: httpx.Response) -> GitHubList:
    response_data: Any = response.json()

    if not isinstance(response_data, list) or not all(
            isinstance(elem, dict) for elem in response_data
    ):
        raise GitHubUnexpectedResponseError("Expected list[dict]")

    return response_data

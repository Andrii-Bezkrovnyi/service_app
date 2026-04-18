from __future__ import annotations


class ApplicationError(Exception):
    status_code = 500
    default_message = "Unexpected application error."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class StorageItemAlreadyExistsError(ApplicationError):
    status_code = 409
    default_message = "Storage item already exists."


class StorageItemNotFoundError(ApplicationError):
    status_code = 404
    default_message = "Storage item was not found."


class GitHubAPIError(ApplicationError):
    status_code = 502
    default_message = "GitHub API request failed."


class GitHubResourceNotFoundError(GitHubAPIError):
    status_code = 404
    default_message = "GitHub resource was not found."


class GitHubRateLimitError(GitHubAPIError):
    status_code = 429
    default_message = "GitHub API rate limit was exceeded."


class GitHubUnexpectedResponseError(GitHubAPIError):
    status_code = 502
    default_message = "GitHub API returned an unexpected response."

from __future__ import annotations

from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True, slots=True)
class Settings:
    github_token: str | None
    github_base_url: str
    github_timeout_seconds: float


def get_settings() -> Settings:
    token = getenv("GITHUB_TOKEN")
    base_url = getenv("GITHUB_BASE_URL", "https://api.github.com")
    timeout = float(getenv("GITHUB_TIMEOUT_SECONDS", "10.0"))

    return Settings(
        github_token=token,
        github_base_url=base_url,
        github_timeout_seconds=timeout,
    )

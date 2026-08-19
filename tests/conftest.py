"""Shared pytest fixtures."""

from __future__ import annotations

import os

import pytest

# SDK-standard env vars that we want isolated per test.
_SDK_ENV_VARS = (
    "DATABRICKS_HOST",
    "DATABRICKS_CLIENT_ID",
    "DATABRICKS_CLIENT_SECRET",
    "DATABRICKS_AUTH_TYPE",
)


@pytest.fixture(autouse=True)
def _isolated_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Strip Magic Ratio and Databricks env vars so tests start clean."""
    for key in list(os.environ):
        if key.startswith("MAGIC_RATIO_"):
            monkeypatch.delenv(key, raising=False)
    for key in _SDK_ENV_VARS:
        monkeypatch.delenv(key, raising=False)

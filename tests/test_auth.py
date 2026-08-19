"""Tests for the Databricks OAuth client factory."""

from __future__ import annotations

import pytest

from magic_ratio.auth import build_config, get_client
from magic_ratio.config import ConfigError


def test_build_config_external_browser(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAGIC_RATIO_DEV_HOST", "https://dev.example.com")
    assert build_config("dev", auth_type="external-browser") == {
        "host": "https://dev.example.com",
        "auth_type": "external-browser",
    }


def test_build_config_defaults_to_external_browser(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MAGIC_RATIO_DEV_HOST", "https://dev.example.com")
    assert build_config("dev")["auth_type"] == "external-browser"


def test_build_config_oauth_m2m_with_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MAGIC_RATIO_PROD_HOST", "https://prod.example.com")
    monkeypatch.setenv("MAGIC_RATIO_PROD_CLIENT_ID", "client-id")
    monkeypatch.setenv("MAGIC_RATIO_PROD_CLIENT_SECRET", "client-secret")
    assert build_config("prod", auth_type="oauth-m2m") == {
        "host": "https://prod.example.com",
        "auth_type": "oauth-m2m",
        "client_id": "client-id",
        "client_secret": "client-secret",
    }


def test_build_config_falls_back_to_sdk_env_vars(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABRICKS_HOST", "https://fallback.example.com")
    monkeypatch.setenv("DATABRICKS_CLIENT_ID", "fallback-id")
    cfg = build_config("dev", auth_type="oauth-m2m")
    assert cfg["host"] == "https://fallback.example.com"
    assert cfg["client_id"] == "fallback-id"
    assert "client_secret" not in cfg


def test_build_config_rejects_unsupported_auth_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MAGIC_RATIO_DEV_HOST", "https://dev.example.com")
    with pytest.raises(ConfigError, match="pat"):
        build_config("dev", auth_type="pat")


def test_build_config_rejects_invalid_env() -> None:
    with pytest.raises(ConfigError, match="staging"):
        build_config("staging")


def test_get_client_passes_config_to_workspace_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WorkspaceClient is constructed with the resolved per-env config."""
    monkeypatch.setenv("MAGIC_RATIO_DEV_HOST", "https://dev.example.com")

    captured: dict[str, str] = {}

    class StubClient:
        def __init__(self, **kwargs: str) -> None:
            captured.update(kwargs)

    monkeypatch.setattr("magic_ratio.auth.WorkspaceClient", StubClient)
    get_client("dev")
    assert captured == {
        "host": "https://dev.example.com",
        "auth_type": "external-browser",
    }

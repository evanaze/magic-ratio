"""Tests for environment and configuration resolution."""

from __future__ import annotations

import pytest

from magic_ratio.config import (
    DEFAULT_ENV,
    SUPPORTED_ENVS,
    ConfigError,
    default_auth_type,
    env_var_name,
    resolve_host,
)


def test_default_env_is_dev() -> None:
    assert DEFAULT_ENV == "dev"


def test_supported_envs_includes_prod_and_dev() -> None:
    assert set(SUPPORTED_ENVS) == {"prod", "dev"}


def test_env_var_name() -> None:
    assert env_var_name("prod", "HOST") == "MAGIC_RATIO_PROD_HOST"
    assert env_var_name("dev", "client_id") == "MAGIC_RATIO_DEV_CLIENT_ID"


def test_default_auth_type_is_external_browser(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MAGIC_RATIO_AUTH_TYPE", raising=False)
    assert default_auth_type() == "external-browser"


def test_default_auth_type_reads_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAGIC_RATIO_AUTH_TYPE", "oauth-m2m")
    assert default_auth_type() == "oauth-m2m"


def test_resolve_host_prefers_per_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAGIC_RATIO_DEV_HOST", "https://dev.example.com")
    monkeypatch.setenv("DATABRICKS_HOST", "https://fallback.example.com")
    assert resolve_host("dev") == "https://dev.example.com"


def test_resolve_host_falls_back_to_databricks_host(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABRICKS_HOST", "https://fallback.example.com/")
    assert resolve_host("prod") == "https://fallback.example.com"


def test_resolve_host_missing_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MAGIC_RATIO_DEV_HOST", raising=False)
    monkeypatch.delenv("DATABRICKS_HOST", raising=False)
    with pytest.raises(ConfigError, match="MAGIC_RATIO_DEV_HOST"):
        resolve_host("dev")


def test_resolve_host_requires_scheme(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAGIC_RATIO_PROD_HOST", "adb-123.4.azuredatabricks.net")
    with pytest.raises(ConfigError, match="scheme"):
        resolve_host("prod")


def test_resolve_host_rejects_unknown_env() -> None:
    with pytest.raises(ConfigError, match="staging"):
        resolve_host("staging")

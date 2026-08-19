"""Tests for the Click CLI entrypoint."""

from __future__ import annotations

from click.testing import CliRunner

from magic_ratio.cli import main


def invoke(*args: str) -> CliRunner.Result:
    runner = CliRunner()
    return runner.invoke(main, list(args))


def test_help_lists_auth_command() -> None:
    result = invoke("--help")
    assert result.exit_code == 0
    assert "auth" in result.output


def test_help_lists_env_options() -> None:
    result = invoke("--help")
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "dev" in result.output


def test_version() -> None:
    result = invoke("--version")
    assert result.exit_code == 0
    assert "magic-ratio" in result.output


def test_auth_without_host_fails_clearly() -> None:
    result = invoke("auth")
    assert result.exit_code != 0
    assert "MAGIC_RATIO_DEV_HOST" in result.output


def test_auth_prod_mentions_prod_host_var() -> None:
    result = invoke("--env", "prod", "auth")
    assert result.exit_code != 0
    assert "MAGIC_RATIO_PROD_HOST" in result.output


def test_env_reads_env_var(monkeypatch) -> None:
    monkeypatch.setenv("MAGIC_RATIO_ENV", "prod")
    result = invoke("auth")
    assert result.exit_code != 0
    assert "MAGIC_RATIO_PROD_HOST" in result.output


def test_env_reads_auth_type_env_var(monkeypatch) -> None:
    """A successful auth run prints connection details (client calls mocked)."""
    monkeypatch.setenv("MAGIC_RATIO_DEV_HOST", "https://dev.example.com")
    monkeypatch.setenv("MAGIC_RATIO_AUTH_TYPE", "oauth-m2m")
    monkeypatch.setattr("magic_ratio.cli.get_client", lambda *a, **k: object())
    monkeypatch.setattr("magic_ratio.cli.get_identity", lambda *a, **k: "service-principal")
    result = invoke("--env", "dev", "auth")
    assert result.exit_code == 0
    assert "Authenticated with dev" in result.output
    assert "https://dev.example.com" in result.output
    assert "service-principal" in result.output


def test_invalid_env_rejected() -> None:
    result = invoke("--env", "staging", "auth")
    assert result.exit_code != 0
    assert "staging" in result.output

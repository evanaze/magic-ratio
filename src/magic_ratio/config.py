"""Environment and configuration resolution for the magic-ratio CLI."""

from __future__ import annotations

import os

#: Environments the CLI knows about, in order of the ``--env`` choice.
SUPPORTED_ENVS = ("prod", "dev")

#: OAuth flows supported by Databricks and wrapped here.
SUPPORTED_AUTH_TYPES = ("external-browser", "oauth-m2m")

#: Environment used when ``--env`` / ``MAGIC_RATIO_ENV`` are not provided.
DEFAULT_ENV = "dev"

#: OAuth flow used when ``--auth-type`` / ``MAGIC_RATIO_AUTH_TYPE`` are not provided.
DEFAULT_AUTH_TYPE = "external-browser"

_ENV_VAR_PREFIX = "MAGIC_RATIO"


class ConfigError(RuntimeError):
    """Raised when CLI configuration is missing or invalid."""


def env_var_name(env: str, suffix: str) -> str:
    """Return the per-environment variable name, e.g. ``MAGIC_RATIO_PROD_HOST``."""
    return f"{_ENV_VAR_PREFIX}_{env.upper()}_{suffix.upper()}"


def default_auth_type() -> str:
    """Resolve the OAuth flow, preferring the ``MAGIC_RATIO_AUTH_TYPE`` env var."""
    return os.environ.get(f"{_ENV_VAR_PREFIX}_AUTH_TYPE", DEFAULT_AUTH_TYPE)


def resolve_host(env: str) -> str:
    """Resolve the Databricks workspace host URL for an environment.

    Per-environment vars (``MAGIC_RATIO_PROD_HOST`` / ``MAGIC_RATIO_DEV_HOST``)
    take precedence over the SDK-standard ``DATABRICKS_HOST`` fallback.
    """
    if env not in SUPPORTED_ENVS:
        raise ConfigError(
            f"Unknown environment {env!r}; expected one of {', '.join(SUPPORTED_ENVS)}"
        )
    host = os.environ.get(env_var_name(env, "HOST")) or os.environ.get("DATABRICKS_HOST")
    if not host:
        raise ConfigError(
            f"No Databricks host configured for environment {env!r}.\n"
            f"Set {env_var_name(env, 'HOST')} (or DATABRICKS_HOST) to the workspace URL, e.g. https://adb-123.4.azuredatabricks.net"
        )
    host = host.rstrip("/")
    if not host.startswith(("https://", "http://")):
        raise ConfigError(
            f"Host for environment {env!r} must include a scheme (got {host!r}). "
            "Use the workspace URL, e.g. https://adb-123.4.azuredatabricks.net"
        )
    return host

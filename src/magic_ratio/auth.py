"""Databricks OAuth authentication for the prod and dev environments."""

from __future__ import annotations

import os

from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import DatabricksError

from magic_ratio.config import (
    SUPPORTED_AUTH_TYPES,
    ConfigError,
    env_var_name,
    resolve_host,
)


class AuthError(RuntimeError):
    """Raised when Databricks authentication or identity resolution fails."""


def build_config(env: str, auth_type: str | None = None) -> dict[str, str]:
    """Build the ``databricks-sdk`` config kwargs for an environment.

    ``external-browser`` uses the user OAuth consent flow (opens a browser),
    while ``oauth-m2m`` uses a service principal via client ID/secret.

    Per-environment ``MAGIC_RATIO_*`` vars take precedence over the
    SDK-standard ``DATABRICKS_*`` vars.
    """
    if auth_type is None:
        from magic_ratio.config import default_auth_type

        auth_type = default_auth_type()
    if auth_type not in SUPPORTED_AUTH_TYPES:
        raise ConfigError(
            f"Unsupported auth type {auth_type!r}; expected one of "
            f"{', '.join(SUPPORTED_AUTH_TYPES)}"
        )

    config: dict[str, str] = {
        "host": resolve_host(env),
        "auth_type": auth_type,
    }
    client_id = os.environ.get(env_var_name(env, "CLIENT_ID")) or os.environ.get(
        "DATABRICKS_CLIENT_ID"
    )
    client_secret = os.environ.get(env_var_name(env, "CLIENT_SECRET")) or os.environ.get(
        "DATABRICKS_CLIENT_SECRET"
    )
    if client_id:
        config["client_id"] = client_id
    if client_secret:
        config["client_secret"] = client_secret
    return config


def get_client(env: str, auth_type: str | None = None) -> WorkspaceClient:
    """Build a Databricks workspace client for an environment.

    The client is constructed lazily: OAuth (consent or M2M) is only
    triggered on the first API call, e.g. via :func:`get_identity`.
    """
    try:
        return WorkspaceClient(**build_config(env, auth_type))
    except DatabricksError as exc:
        raise AuthError(f"Failed to authenticate with {env!r}: {exc}") from exc


def get_identity(client: WorkspaceClient) -> str:
    """Return a human-readable identity for the authenticated principal.

    This is the call that forces the OAuth round trip for
    ``external-browser`` (user) and ``oauth-m2m`` (service principal).
    """
    try:
        me = client.current_user.me()
    except DatabricksError as exc:
        raise AuthError(f"Failed to resolve identity: {exc}") from exc
    user_name = me.user_name or me.display_name or "<unknown>"
    if me.display_name and me.display_name != user_name:
        return f"{user_name} ({me.display_name})"
    return user_name

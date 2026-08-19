"""Command-line entrypoint for magic-ratio."""

from __future__ import annotations

import click

from magic_ratio import __version__
from magic_ratio.auth import AuthError, get_client, get_identity
from magic_ratio.config import (DEFAULT_ENV, SUPPORTED_AUTH_TYPES,
                                SUPPORTED_ENVS, ConfigError, default_auth_type,
                                resolve_host)


@click.group()
@click.version_option(__version__, prog_name="magic-ratio")
@click.option(
    "--env",
    type=click.Choice(SUPPORTED_ENVS),
    default=DEFAULT_ENV,
    envvar="MAGIC_RATIO_ENV",
    show_default=True,
    help="Databricks environment to target.",
)
@click.option(
    "--auth-type",
    type=click.Choice(SUPPORTED_AUTH_TYPES),
    envvar="MAGIC_RATIO_AUTH_TYPE",
    help=(
        "OAuth flow: external-browser (user consent) or "
        "oauth-m2m (service principal)."
    ),
)
@click.pass_context
def main(ctx: click.Context, env: str, auth_type: str | None) -> None:
    """Size dbt pipelines in Databricks so dev runs match production."""
    ctx.ensure_object(dict)
    ctx.obj["env"] = env
    ctx.obj["auth_type"] = auth_type or default_auth_type()


@main.command()
@click.pass_context
def auth(ctx: click.Context) -> None:
    """Authenticate the CLI with the prod/dev Databricks environment."""
    env: str = ctx.obj["env"]
    auth_type: str = ctx.obj["auth_type"]
    try:
        client = get_client(env, auth_type)
        identity = get_identity(client)
        host = resolve_host(env)
    except (ConfigError, AuthError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Authenticated with {env} ({host}) as {identity}.")


if __name__ == "__main__":
    main()

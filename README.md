# Magic Ratio

Size your dbt pipelines in Databricks so they run in **dev** the same way they
run in **production**.

## How it works

dbt pipelines behave differently in dev than in prod for one simple reason: the
underlying compute is different. A model that takes five minutes against a
large production cluster can take hours — or time out entirely — against a
small shared dev cluster, and a data volume that fits comfortably in prod
memory can spill or OOM in dev.

Magic Ratio closes that gap by calculating the right dev settings from what
already works in production:

1. **Profile the production run.** Magic Ratio inspects the clusters and/or
   pipeline configurations your production dbt jobs actually use — instance
   type, number of workers, autoscaling, Spark configurations, and the size of
   the data being processed.
2. **Compute the scaling ratio.** It derives the ratio between the production
   footprint and the dev footprint limits (budget, instance availability, or
   your own guardrails), producing a concrete sizing recommendation for the
   dev run: instance type, cluster size, parallelism, and dbt
   thread/session settings.
3. **Apply the same behavior in dev.** The recommended settings are emitted as
   configuration for the dev environment, so dbt runs in dev against compute
   that behaves like prod — just smaller, on purpose.

The target environments are referred to throughout the CLI as **prod** and
**dev**. Both are authenticated with the same tooling, so switching between
"size from prod" and "apply to dev" is a single flag.

## How to use

### Installation

Requires Python 3.10+.

```bash
git clone <your-repo-url> magic-ratio
cd magic-ratio
python -m pip install -e .[dev]
```

This installs the `magic-ratio` command and the `databricks-sdk` dependency.

### Authentication

Magic Ratio authenticates with both Databricks environments using
**Databricks OAuth**, via the `databricks-sdk`:

- **`external-browser`** (default) — user OAuth consent flow. Opens a browser,
  you approve access, and the SDK caches the refresh token. Best for
  interactive day-to-day usage.
- **`oauth-m2m`** — service-principal flow using a client ID and secret. Best
  for automation and CI.

The environment host and (for M2M) credentials are resolved from environment
variables. Per-environment vars take precedence, and the SDK-standard
`DATABRICKS_*` vars act as a fallback:

| Variable                    | Used for                                        |
| --------------------------- | ----------------------------------------------- |
| `MAGIC_RATIO_ENV`           | Default environment (`prod` or `dev`)           |
| `MAGIC_RATIO_AUTH_TYPE`     | Default OAuth flow (`external-browser` / `oauth-m2m`) |
| `MAGIC_RATIO_PROD_HOST`     | Production workspace URL                        |
| `MAGIC_RATIO_DEV_HOST`      | Dev workspace URL                               |
| `MAGIC_RATIO_PROD_CLIENT_ID` / `MAGIC_RATIO_PROD_CLIENT_SECRET` | M2M credentials for prod |
| `MAGIC_RATIO_DEV_CLIENT_ID` / `MAGIC_RATIO_DEV_CLIENT_SECRET`  | M2M credentials for dev  |
| `DATABRICKS_HOST`           | Fallback host for either environment            |
| `DATABRICKS_CLIENT_ID` / `DATABRICKS_CLIENT_SECRET` | Fallback M2M credentials |

### CLI usage

```bash
# Authenticate with dev (default), opening the user consent flow
magic-ratio auth

# Authenticate with prod
magic-ratio --env prod auth

# Authenticate with a service principal against dev
magic-ratio --env dev --auth-type oauth-m2m auth
```

You can also set the defaults once in your shell instead of passing flags:

```bash
export MAGIC_RATIO_ENV=prod
export MAGIC_RATIO_AUTH_TYPE=oauth-m2m
export MAGIC_RATIO_PROD_HOST=https://adb-123456789.4.azuredatabricks.net
export MAGIC_RATIO_PROD_CLIENT_ID=your-client-id
export MAGIC_RATIO_PROD_CLIENT_SECRET=your-client-secret

magic-ratio auth
```

Sizing commands (profile, ratio, apply) will be added on top of this
authentication layer as the tool evolves.

### Development

```bash
python -m pip install -e .[dev]
pytest          # run the test suite
ruff check src tests   # lint
```

## Project layout

```
src/magic_ratio/
  __init__.py   # package metadata
  cli.py        # Click entrypoint (--env / --auth-type, `auth` command)
  config.py     # environment registry and configuration resolution
  auth.py       # Databricks OAuth client factory (external-browser / oauth-m2m)
tests/          # pytest suite
pyproject.toml  # build + dependency configuration
```

## License

GPL-3.0-or-later, see [LICENSE](LICENSE).

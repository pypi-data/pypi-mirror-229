# Flipt Migrator

This is a tool to migrate feature flags from one source (e.g. competitor) to [Flipt](https://github.com/flipt-io/flipt).

It works by exporting the feature flags from the source into a set of `*.features.yml` files that can then be imported into Flipt or run as the source data with Flipt in ['local' mode](https://www.flipt.io/docs/configuration/storage#local).

## Disclaimer

:warning: This tool is best effort and may not work for all use cases. Because of the differences in how feature flags are implemented across different sources and APIs, it is likely that some manual work will be required to get the feature flags into a state that works with Flipt after they have been exported.

The main goal of this tool is to make it easier to get started with Flipt by reducing the amount of manual work required to migrate from another source.

No guarantees are made about the correctness of the exported feature flags. It is recommended that you review the exported feature flags before importing them into Flipt.

## Legal

:balance_scale: This tool is not affiliated with or endorsed by any of the sources it supports. All trademarks are the property of their respective owners.

## Usage

```shell
usage: flipt-migrate [-h] [--source {LaunchDarkly}] [--out OUT]

Migrate from a feature flag source to Flipt.

options:
  -h, --help            show this help message and exit
  --source {LaunchDarkly}
                        The source to migrate from.
  --out OUT             The location to export Flipt data. Defaults to current directory.
```

## Sources

### LaunchDarkly

To export feature flags from LaunchDarkly, you will need to set the following environment variables or you will be prompted for them:

- `LAUNCHDARKLY_API_KEY` - Your LaunchDarkly API key
- `LAUNCHDARKLY_PROJECT_KEY` - The LaunchDarkly project key to export (optional)

## Contributing

### Conventional Commits

We use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for commit messages. This allows us to automatically generate a changelog and releases with [Release Please](https://github.com/googleapis/release-please).

### Adding a New Source

To add a new source, you will need to create a new class that inherits from [`Transformer`](./flipt_migrate/transformer.py) and implements the `transform` method. The `transform` method should return a `Collection` which maps to the Flipt [state model](https://www.flipt.io/docs/configuration/storage#defining-flag-state).

Once you have created the new source, you will need to add it to the `SOURCES` dictionary to load the necessary `Transformer` in [`main.py`](./flipt_migrate/main.py).

The `SOURCES` dictionary maps the source name to function which returns the implemented `Transformer` class. The function is used to delay the import of the `Transformer` class until it is needed as well as to allow each source to prompt for any necessary credentials or arguments.

## Development

We use [Poetry](https://python-poetry.org/) to manage dependencies and packaging.

### Setup

```shell
poetry install
```

### Run

```shell
poetry run python flipt_migrate/main.py
```

### Format/Lint

We use [black](https://black.readthedocs.io/en/stable/) for linting and formatting.

```shell
poetry run black .
```

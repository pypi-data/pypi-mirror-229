import os
import questionary
import argparse
from flipt_migrate.source import launchdarkly
from flipt_migrate.exporter import export_to_yaml

# TODO: Add support for other sources
SOURCES = {"LaunchDarkly": launchdarkly.transformer}


def run():
    parser = argparse.ArgumentParser(
        description="Migrate from a feature flag source to Flipt."
    )
    parser.add_argument(
        "--source",
        type=str,
        choices=SOURCES.keys(),
        help="The source to migrate from.",
    )
    parser.add_argument(
        "--out",
        type=str,
        help="The location to export Flipt data.",
    )
    args = parser.parse_args()

    if args.out is not None:
        path = args.out
    else:
        path = questionary.path(
            "Location to export Flipt data:", ".", only_directories=True
        ).ask()

    transformer = None

    if args.source is not None:
        competitor = args.source
    else:
        competitor = questionary.select(
            "Source:",
            choices=SOURCES.keys(),
        ).ask()

    if competitor in SOURCES:
        transformer = SOURCES[competitor]()
    else:
        print("Unsupported source.")
        return

    data = transformer.transform()
    if not data:
        print("No data to export.")
        return

    wrote = export_to_yaml(data, path)
    print("\n✅ Migration completed successfully.")

    print("\n📂 Exported files:")
    for f in wrote:
        print(f"- {f}")


def main():
    run()

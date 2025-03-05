"""Command-line interface."""

import click


@click.command()
@click.version_option()
def main() -> None:
    """File Stream."""


if __name__ == "__main__":
    main(prog_name="file-stream")  # pragma: no cover

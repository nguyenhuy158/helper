"""Table formatting utilities for the helper CLI."""

import json

import click
import yaml
from tabulate import tabulate

data = [{"name": "Huy", "age": 23}, {"name": "An", "age": 25}]


@click.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "yaml", "table", "text"]),
    default="table",
)
def show(output_format):
    """Display data in various formats."""
    if output_format == "json":
        click.echo(json.dumps(data, indent=2))
    elif output_format == "yaml":
        click.echo(yaml.dump(data))
    elif output_format == "table":
        click.echo(tabulate(data, headers="keys"))
    else:
        for item in data:
            click.echo(f"{item['name']} - {item['age']}")


if __name__ == "__main__":
    show()

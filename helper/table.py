import click
import json
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
def show(format):
    if format == "json":
        click.echo(json.dumps(data, indent=2))
    elif format == "yaml":
        click.echo(yaml.dump(data))
    elif format == "table":
        click.echo(tabulate(data, headers="keys"))
    else:
        for item in data:
            click.echo(f"{item['name']} - {item['age']}")


if __name__ == "__main__":
    show()

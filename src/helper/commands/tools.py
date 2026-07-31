"""Tools command for helper CLI - showcase other tools by the same author."""

import click
from rich.console import Console
from rich.table import Table

console = Console()

TOOLS = [
    {
        "name": "helper-cli",
        "description": "Quick system info CLI (this tool)",
        "install": "uv tool install helper-cli",
        "repo": "https://github.com/nguyenhuy158/helper",
    },
    {
        "name": "pgslim",
        "description": "Reduce PostgreSQL dump size by nullifying large bytea/text columns",
        "install": "pip install pgslim",
        "repo": "https://github.com/nguyenhuy158/pgslim",
    },
    {
        "name": "superclean",
        "description": "Clean development caches and reclaim disk space (sclean)",
        "install": "pip install superclean",
        "repo": "https://github.com/nguyenhuy158/superclean",
    },
    {
        "name": "chillguy",
        "description": "Terminal-based YouTube music player (requires mpv)",
        "install": "pip install chillguy",
        "repo": "https://github.com/nguyenhuy158/chillguy",
    },
    {
        "name": "docxlint",
        "description": "Validate Jinja2 template syntax inside .docx files (docxtpl)",
        "install": "pip install docxlint",
        "repo": "https://github.com/nguyenhuy158/docxlint",
    },
    {
        "name": "graphql-compare",
        "description": "Compare GraphQL responses between environments (Docker app)",
        "install": "git clone + docker compose up",
        "repo": "https://github.com/nguyenhuy158/graphql-compare",
    },
]


def get_tools():
    """Return the list of tools to showcase."""
    return TOOLS


@click.command()
def tools():
    """List other tools by the same author.

    Shows name, description, install command, and repository link
    for each tool.

    Example:
        $ h tools
    """
    table = Table(title="🧰 More tools by nguyenhuy158", border_style="magenta")
    table.add_column("Name", style="bold cyan", no_wrap=True)
    table.add_column("Description")
    table.add_column("Install", style="green", no_wrap=True)
    table.add_column("Repo", style="blue", overflow="fold")

    for tool in get_tools():
        table.add_row(tool["name"], tool["description"], tool["install"], tool["repo"])

    console.print(table)

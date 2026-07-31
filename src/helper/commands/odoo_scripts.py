"""Odoo scripts command - browse and download click-odoo scripts."""

import json
import os
import urllib.error
import urllib.request

import click
from rich.console import Console
from rich.table import Table

console = Console()

REPO = "nguyenhuy158/odoo-scripts"
API_URL = f"https://api.github.com/repos/{REPO}/contents/scripts"


def _request(url, raw=False):
    """Fetch a GitHub API URL, using GITHUB_TOKEN/GH_TOKEN when available."""
    accept = "application/vnd.github.raw" if raw else "application/vnd.github+json"
    headers = {"Accept": accept, "User-Agent": "helper-cli"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read()


def list_scripts():
    """Return the .py files under scripts/ in the odoo-scripts repo."""
    entries = json.loads(_request(API_URL))
    return [e for e in entries if e["type"] == "file" and e["name"].endswith(".py")]


def download_script(script, dest_dir="."):
    """Download one script entry to dest_dir, return the written path."""
    content = _request(script["url"], raw=True)
    dest = os.path.join(dest_dir, script["name"])
    with open(dest, "wb") as fh:
        fh.write(content)
    return dest


def _first_doc_line(script):
    """Best-effort short description: repo API has no docstring, keep size instead."""
    size = script.get("size", 0)
    return f"{size} B" if size < 1024 else f"{size / 1024:.1f} KB"


@click.command()
@click.argument("name", required=False)
@click.option(
    "--dir",
    "-d",
    "dest_dir",
    default=None,
    type=click.Path(file_okay=False),
    help="Directory to save the script into (prompted if omitted, default: current dir).",
)
def odoo(name, dest_dir):
    """Browse and download click-odoo scripts.

    Lists the scripts available in the odoo-scripts repository,
    downloads the selected one, then you run it yourself with
    click-odoo. After selecting, you are asked where to save the
    file (default: current directory).

    NAME optionally skips the menu and downloads that script directly.

    Example:
        $ h odoo
        $ h odoo list_users
        $ h odoo list_users --dir ~/scripts
    """
    try:
        scripts = list_scripts()
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 404):
            console.print(
                f"[red]Cannot access {REPO} (HTTP {e.code}).[/red] "
                "Repo is private - set GITHUB_TOKEN or GH_TOKEN with read access."
            )
        else:
            console.print(f"[red]GitHub API error: HTTP {e.code}[/red]")
        raise SystemExit(1)
    except urllib.error.URLError as e:
        console.print(f"[red]Network error: {e.reason}[/red]")
        raise SystemExit(1)

    if not scripts:
        console.print("No scripts found in the repository.")
        return

    if name:
        wanted = name if name.endswith(".py") else f"{name}.py"
        selected = next((s for s in scripts if s["name"] == wanted), None)
        if selected is None:
            console.print(f"[red]No script named '{wanted}'.[/red] Available:")
            for s in scripts:
                console.print(f"  - {s['name']}")
            raise SystemExit(1)
    else:
        table = Table(title=f"📜 Scripts in {REPO}", border_style="magenta")
        table.add_column("#", justify="right", style="bold")
        table.add_column("Name", style="cyan")
        table.add_column("Size", justify="right")
        for i, s in enumerate(scripts, start=1):
            table.add_row(str(i), s["name"], _first_doc_line(s))
        console.print(table)

        choice = click.prompt(
            "Select script number (0 to cancel)",
            type=click.IntRange(0, len(scripts)),
        )
        if choice == 0:
            return
        selected = scripts[choice - 1]

    if dest_dir is None:
        dest_dir = click.prompt(
            "Save to directory",
            default=".",
            type=click.Path(file_okay=False),
        )
    dest_dir = os.path.expanduser(dest_dir)
    os.makedirs(dest_dir, exist_ok=True)

    target = os.path.join(dest_dir, selected["name"])
    if os.path.exists(target) and not click.confirm(
        f"{target} already exists. Overwrite?"
    ):
        return

    dest = download_script(selected, dest_dir=dest_dir)
    console.print(f"[green]Saved[/green] {dest}")
    console.print("Run it with:")
    console.print(f"  [bold]click-odoo -c odoo.conf -d <db> {dest}[/bold]")

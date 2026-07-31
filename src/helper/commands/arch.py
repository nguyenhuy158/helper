"""Arch command for helper CLI."""

import subprocess

import click
from rich.console import Console
from rich.panel import Panel

from ..rich_help import RichHelpCommand

console = Console()


def get_arch():
    """Get system architecture information."""
    cmd = "uname -m"
    try:
        result = subprocess.check_output(cmd, shell=True, text=True).strip()
        return result
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"


@click.command(cls=RichHelpCommand)
def arch():
    """Display system architecture information.

    Shows the machine hardware name, which is useful for determining
    if you're running on x86_64, arm64, or other architectures.

    Equivalent to running 'uname -m' in the terminal.

    Example:
        $ h arch
        arm64
    """
    result = get_arch()
    console.print(Panel(result, title="$ uname -m", border_style="magenta"))

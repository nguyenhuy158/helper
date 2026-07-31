"""Public IP address commands."""

import subprocess

import click
from rich.console import Console
from rich.panel import Panel

console = Console()


def get_public_ip():
    """Get the public IP address."""
    cmd = "curl -s ifconfig.me"
    try:
        result = subprocess.check_output(cmd, shell=True, text=True).strip()
        return result
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"


@click.command()
def public_ip():
    """Display the public (external) IP address.

    This command retrieves and displays your public IP address as seen from the internet.
    It's useful for checking your current external network identity.

    Examples:
        $ h pubip
        203.0.113.45

    Note: Requires an active internet connection. Uses ifconfig.me service by default.
    """
    result = get_public_ip()
    console.print(Panel(result, title="$ curl -s ifconfig.me", border_style="green"))

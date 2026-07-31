"""Command to display all system information."""

import click
from rich.console import Console
from rich.panel import Panel

from ..rich_help import RichHelpCommand
from . import arch, internal_ip, public_ip, system_info

console = Console()


def get_info():
    """Get all system information as a dictionary."""
    return {
        "internal_ip": internal_ip.get_internal_ip(),
        "public_ip": public_ip.get_public_ip(),
        "arch": arch.get_arch(),
        "system_info": system_info.get_info(),
    }


@click.command(name="all", cls=RichHelpCommand)
def all_command():
    """Show all info"""
    info = get_info()

    console.print(Panel(info["internal_ip"], title="Internal IP", border_style="blue"))
    console.print(Panel(info["public_ip"], title="Public IP", border_style="green"))
    console.print(Panel(info["arch"], title="Architecture", border_style="magenta"))

    # NixOS command doesn't accept arguments, so we'll just run it directly
    console.print(
        Panel(
            "Note: NixOS version check skipped as it requires direct execution\nTo check NixOS version, run: [bold]h nix[/bold]",
            title="NixOS (Skipped)",
            border_style="yellow",
        )
    )

    # Format system_info
    si = info["system_info"]
    if si:
        # Reusing the logic from system_info but with specific formatting for 'all'
        from rich.table import Table

        # System Information
        table = Table(show_header=False, box=None)
        table.add_row("System", f"{si['system']['system']} {si['system']['release']}")
        table.add_row("Node Name", si["system"]["node"])
        table.add_row("Machine", si["system"]["machine"])
        table.add_row("Processor", si["system"]["processor"])
        console.print(Panel(table, title="System Information", border_style="blue"))

        # OS Version & Uptime
        table = Table(show_header=False, box=None)
        table.add_row("OS Version", si["os_version"])
        table.add_row("Uptime", si["uptime"])
        console.print(Panel(table, title="OS & Uptime", border_style="green"))

        # CPU Info
        table = Table(show_header=False, box=None)
        table.add_row("Cores", si["cpu"]["cores"])
        if "cpu" in si["cpu"]:
            table.add_row("Model", si["cpu"]["cpu"])
        if "load_avg" in si["cpu"]:
            table.add_row("Load Average", si["cpu"]["load_avg"])
        console.print(Panel(table, title="CPU Info", border_style="magenta"))

        # Memory Information
        if isinstance(si["memory"], dict):
            table = Table(box=None)
            table.add_column("Type", style="cyan")
            table.add_column("Value", style="bold")
            table.add_row("Total", si["memory"]["total"])
            table.add_row("Used", si["memory"]["used"])
            table.add_row("Free", si["memory"]["free"])
            table.add_row("Usage", si["memory"]["usage"])
            console.print(Panel(table, title="Memory Information", border_style="yellow"))
        else:
            console.print(Panel(si["memory"], title="Memory Information", border_style="yellow"))

        # Disk Information
        console.print(Panel(si["disks"], title="Disk Information", border_style="cyan"))


def register_all_command(cli):
    """Register the 'all' command with the CLI (kept for back-compat)."""
    cli.add_command(all_command)
    return all_command

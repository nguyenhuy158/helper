"""Main entry point for the helper CLI application."""

import logging

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .commands import (
    all_info,
    arch,
    disk,
    docker,
    env_cmd,
    file,
    internal_ip,
    journalctl,
    kill,
    nixos,
    odoo_scripts,
    public_ip,
    rsync,
    run_cmd,
    speed,
    system_info,
    tools,
    venv,
    verbosity,
)
from .env_manager import load_env

# Import verbosity classes from the verbosity module
VerbosityCommand = verbosity.VerbosityCommand
VerbosityGroup = verbosity.VerbosityGroup

COMMAND_CATEGORIES = {
    "System": ["si", "arch", "env", "v", "nix", "all"],
    "Network": ["ip", "pubip", "sp"],
    "Docker": ["d"],
    "Files & Disk": ["f", "disk", "rsync"],
    "Process & Logs": ["kill", "journalctl"],
    "Odoo": ["odoo"],
    "Snippets & Tools": ["run", "tools"],
}


class HelperGroup(VerbosityGroup):
    """Group with a rich, categorized help screen."""

    def format_help(self, ctx, formatter):
        console = Console()
        with console.capture() as capture:
            console.print(
                Panel.fit(
                    f"[bold cyan]Helper CLI[/bold cyan] [dim]v{__version__}[/dim]"
                    " — quick system info\n"
                    "[dim]Shortcut:[/dim] [bold]h[/bold] = helper"
                    "   [dim]e.g.[/dim] h ip, h odoo",
                    border_style="magenta",
                )
            )
            console.print(
                "[bold]Usage:[/bold] helper [dim]\\[OPTIONS][/dim] COMMAND [dim]\\[ARGS]...[/dim]"
            )

            table = Table(border_style="magenta", show_header=False, pad_edge=False, box=None)
            table.add_column("Category", style="yellow", no_wrap=True)
            table.add_column("Command", style="bold cyan", no_wrap=True)
            table.add_column("Description", style="")

            categorized = set()
            for category, names in COMMAND_CATEGORIES.items():
                for j, cmd_name in enumerate(names):
                    cmd = self.get_command(ctx, cmd_name)
                    if cmd is None:
                        continue
                    categorized.add(cmd_name)
                    table.add_row(
                        f"─ {category}" if j == 0 else "",
                        cmd_name,
                        cmd.get_short_help_str(70),
                    )
                table.add_section()
            leftovers = [n for n in self.list_commands(ctx) if n not in categorized]
            for j, cmd_name in enumerate(leftovers):
                cmd = self.get_command(ctx, cmd_name)
                table.add_row("─ Other" if j == 0 else "", cmd_name, cmd.get_short_help_str(70))

            console.print(table)
            console.print(
                "[dim]Options:[/dim] [bold]-V[/bold] version"
                "  [bold]-h[/bold] help"
                "  [bold]-v[/bold] verbose"
                "   [dim]|   helper <command> --help for details[/dim]"
            )
        formatter.write(capture.get())


@click.group(
    name="helper",
    cls=HelperGroup,
    context_settings={
        "help_option_names": ["-h", "--help"],
        "token_normalize_func": lambda x: "helper" if x == "h" else x,
    },
)
@click.version_option(__version__, "-V", "--version", message="%(prog)s version %(version)s")
def cli():
    """Helper CLI - quick system info.

    You can use 'h' as a shortcut for 'helper' command.
    Example: h docker ps

    For detailed help on a specific command, use: helper <command> --help
    """
    # Initialize environment variables
    load_env()

    # Set up basic logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.ERROR,
    )


# Register all commands
# Keep only short versions of commands where duplicates exist
cli.add_command(internal_ip.internal_ip, name="ip")
cli.add_command(public_ip.public_ip, name="pubip")
cli.add_command(arch.arch, name="arch")
cli.add_command(nixos.nixos, name="nix")
cli.add_command(docker.docker, name="d")
cli.add_command(speed.speed, name="sp")
cli.add_command(system_info.system_info, name="si")
cli.add_command(venv.venv, name="v")
cli.add_command(file.file(), name="f")
cli.add_command(env_cmd, name="env")
cli.add_command(run_cmd, name="run")
cli.add_command(kill.kill, name="kill")
cli.add_command(disk.disk(), name="disk")
cli.add_command(journalctl.journalctl(), name="journalctl")
cli.add_command(rsync.rsync, name="rsync")
cli.add_command(tools.tools, name="tools")
cli.add_command(odoo_scripts.odoo, name="odoo")


# Register the all command
all_info.register_all_command(cli)


if __name__ == "__main__":
    cli()

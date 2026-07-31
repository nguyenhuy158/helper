"""Main entry point for the helper CLI application."""

import importlib
import logging

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .commands import verbosity
from .env_manager import load_env

# Import verbosity classes from the verbosity module
VerbosityCommand = verbosity.VerbosityCommand
VerbosityGroup = verbosity.VerbosityGroup

# Commands are loaded lazily so startup doesn't import heavy modules
# (psutil, speedtest, ...) until the command actually runs.
# name -> (module, attribute); the attribute is a click command or a
# zero-arg factory returning one.
LAZY_COMMANDS = {
    "ip": ("helper.commands.internal_ip", "internal_ip"),
    "pubip": ("helper.commands.public_ip", "public_ip"),
    "arch": ("helper.commands.arch", "arch"),
    "nix": ("helper.commands.nixos", "nixos"),
    "d": ("helper.commands.docker", "docker"),
    "sp": ("helper.commands.speed", "speed"),
    "si": ("helper.commands.system_info", "system_info"),
    "v": ("helper.commands.venv", "venv"),
    "f": ("helper.commands.file", "file"),
    "env": ("helper.commands.env", "env"),
    "run": ("helper.commands.run", "run"),
    "kill": ("helper.commands.kill", "kill"),
    "disk": ("helper.commands.disk", "disk"),
    "journalctl": ("helper.commands.journalctl", "journalctl"),
    "rsync": ("helper.commands.rsync", "rsync"),
    "tools": ("helper.commands.tools", "tools"),
    "odoo": ("helper.commands.odoo_scripts", "odoo"),
    "all": ("helper.commands.all_info", "all_command"),
}

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
    """Group with lazy command loading and a rich, categorized help screen."""

    def list_commands(self, ctx):
        return sorted(set(super().list_commands(ctx)) | set(LAZY_COMMANDS))

    def get_command(self, ctx, name):
        cmd = super().get_command(ctx, name)
        if cmd is not None:
            return cmd
        spec = LAZY_COMMANDS.get(name)
        if spec is None:
            return None
        module_path, attr = spec
        obj = getattr(importlib.import_module(module_path), attr)
        if not isinstance(obj, click.BaseCommand):
            obj = obj()
        self.add_command(obj, name=name)
        return obj

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


if __name__ == "__main__":
    cli()

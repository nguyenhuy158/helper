"""Main entry point for the helper CLI application."""

import importlib

import click
from rich.panel import Panel

from . import __version__
from .commands import verbosity
from .env_manager import load_env
from .rich_help import render_group_help

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
        intro = Panel.fit(
            f"[bold cyan]Helper CLI[/bold cyan] [dim]v{__version__}[/dim]"
            " — quick system info\n"
            "[dim]Shortcut:[/dim] [bold]h[/bold] = helper"
            "   [dim]e.g.[/dim] h ip, h odoo",
            border_style="magenta",
        )
        render_group_help(
            ctx,
            formatter,
            categories=COMMAND_CATEGORIES,
            intro=intro,
            show_description=False,
            extra_options=("[bold]-v[/bold] verbose",),
        )


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


if __name__ == "__main__":
    cli()

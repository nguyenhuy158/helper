import click
import logging
import sys
import subprocess
from . import __version__
from .commands import (
    internal_ip,
    public_ip,
    arch,
    nixos,
    docker,
    speed,
    system_info,
    venv,
    file,
    verbosity,
    all_info,
)


# Import verbosity classes from the verbosity module
VerbosityCommand = verbosity.VerbosityCommand
VerbosityGroup = verbosity.VerbosityGroup


@click.group(
    cls=VerbosityGroup,
    context_settings={
        "help_option_names": ["-h", "--help"],
        "token_normalize_func": lambda x: "helper" if x == "h" else x,
    },
)
@click.version_option(__version__, "-V", "--version", message="%(prog)s version %(version)s")
def cli():
    """Helper CLI - quick system info (v{})
    
    You can use 'h' as a shortcut for 'helper' command.
    Example: h docker ps
    
    For detailed help on a specific command, use: helper <command> --help
    """.format(__version__)
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


# Register the all command
all_info.register_all_command(cli)


if __name__ == "__main__":
    cli()

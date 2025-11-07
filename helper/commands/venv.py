"""
Virtual environment management commands for the helper CLI.

This module provides commands to manage Python virtual environments,
including activating and deactivating them from the command line.
"""

import os
import sys

import click


def find_virtualenv(path=None):
    """Find virtual environment in the given path or current directory.

    Args:
        path (str, optional): Path to search for virtual environment.
            Defaults to current directory.

    Returns:
        str: Path to the activate script if found, None otherwise.
    """
    if path is None:
        path = os.getcwd()

    # Check common virtual environment directories
    venv_dirs = ["venv", ".venv"]
    for venv_dir in venv_dirs:
        activate_script = os.path.join(path, venv_dir, "bin", "activate")
        if os.path.exists(activate_script):
            return activate_script

    # If not found in current directory, try parent directories
    parent = os.path.dirname(path)
    if parent != path:  # Prevent infinite recursion
        return find_virtualenv(parent)

    return None


def source_virtualenv(venv_path=None):
    """Source a virtual environment.

    Args:
        venv_path (str, optional): Path to the virtual environment.
            If None, search in current and parent directories.
    """
    if venv_path is None:
        activate_script = find_virtualenv()
        if not activate_script:
            click.echo(
                "Error: No virtual environment found in current or parent directories.",
                err=True,
            )
            click.echo(
                "Please specify the path to the virtual environment or "
                "create one with 'python -m venv venv'"
            )
            sys.exit(1)
    else:
        # If path is provided, check if it's a directory or activate script
        if os.path.isdir(venv_path):
            # If it's a directory, look for bin/activate
            activate_script = os.path.join(venv_path, "bin", "activate")
            if not os.path.exists(activate_script):
                click.echo(f"Error: No activate script found in {venv_path}", err=True)
                sys.exit(1)
        elif os.path.isfile(venv_path):
            # If it's a file, use it directly
            activate_script = venv_path
        else:
            click.echo(f"Error: {venv_path} is not a valid file or directory", err=True)
            sys.exit(1)

    # Get the absolute path to the activate script
    activate_script = os.path.abspath(activate_script)

    # Print the command to source the virtual environment
    # The user needs to run this with 'eval $(h venv source [path])' or
    # 'source <(h venv source [path])'
    click.echo(f'source "{activate_script}"')
    venv_dir = os.path.dirname(os.path.dirname(activate_script))
    click.echo(f"# Virtual environment activated: {venv_dir}", err=True)


def deactivate_virtualenv():
    """Print the command to deactivate the current virtual environment."""
    click.echo("deactivate")
    click.echo("# Virtual environment deactivated", err=True)


@click.group()
def venv():
    """Manage Python virtual environments."""


@venv.command()
@click.argument("path", required=False)
def source(path):
    """Source a Python virtual environment.

    If no path is provided, searches for a virtual environment in the current or parent directories.
    Looks for 'venv' first, then '.venv'.

    Usage:
        h venv source [PATH]  # Source the specified virtual environment or auto-detect
        eval $(h venv source)  # In bash/zsh to activate the virtual environment
        source <(h venv source)  # Alternative syntax for bash/zsh
    """
    source_virtualenv(path)


@venv.command()
def deactivate():
    """Deactivate the current virtual environment.

    Usage:
        h venv deactivate  # Show the deactivate command
        eval $(h venv deactivate)  # In bash/zsh to deactivate the virtual environment
    """
    deactivate_virtualenv()


# Add short aliases
s = source
d = deactivate

# Add the commands to the module
__all__ = ["venv", "source", "deactivate", "s", "d"]

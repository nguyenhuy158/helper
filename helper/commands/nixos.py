"""NixOS related commands for the helper CLI.

This module provides commands to manage NixOS packages and system operations.
"""

import subprocess
import sys

import click


def check_nixos():
    """Check if running on NixOS."""
    try:
        with open("/etc/os-release") as f:
            return "NixOS" in f.read()
    except FileNotFoundError:
        return False
    except (IOError, PermissionError) as e:
        click.echo(f"Warning: Could not check if running on NixOS: {e}", err=True)
        return False


def get_nixos_version():
    """Get NixOS version information.

    Returns:
        str: NixOS version information or error message
    """
    if not check_nixos():
        return "Not running NixOS"

    try:
        result = subprocess.run(
            ["nixos-version"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error getting NixOS version: {e.stderr}"
    except FileNotFoundError:
        return "nixos-version command not found"


@click.group()
def nixos():
    """NixOS related commands (v0.1.19)."""
    if not check_nixos():
        click.echo(
            "Warning: Not running on NixOS. Some commands may not work as expected.",
            err=True,
        )


@nixos.command()
def version():
    """Show NixOS version."""
    click.echo(get_nixos_version())


@nixos.command()
@click.argument("package", required=False)
def search(package):
    """Search for Nix packages."""
    if not package:
        click.echo("Please specify a package to search for")
        return

    try:
        result = subprocess.run(
            ["nix-env", "-qa", package], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            click.echo(result.stdout)
        else:
            click.echo(f"Error searching for package: {result.stderr}", err=True)
    except subprocess.SubprocessError as e:
        click.echo(f"Error: {str(e)}", err=True)


@nixos.command()
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force garbage collection and remove all old generations",
)
def clean(force):
    """Clean Nix store and perform garbage collection."""
    if not check_nixos():
        click.echo("Error: This command can only be run on NixOS", err=True)
        return

    try:
        click.echo("Running Nix garbage collection...")
        if force:
            click.echo("Forcing garbage collection and removing all old generations...")
            # Remove all old generations of all profiles
            subprocess.run(["nix-collect-garbage", "-d"], check=True)
            click.echo("✓ Removed all old generations and ran garbage collection")
        else:
            # Regular garbage collection (safe, only removes unreachable paths)
            subprocess.run(["nix-collect-garbage"], check=True)
            click.echo("✓ Garbage collection completed")

        # Show disk space usage after cleanup
        click.echo("\nDisk space usage after cleanup:")
        subprocess.run(
            ["nix-store", "--query", "--disk-usage", "/nix/store"], check=False
        )

    except subprocess.CalledProcessError as e:
        click.echo(f"Error during cleanup: {e}", err=True)
    except subprocess.SubprocessError as e:
        click.echo(f"Subprocess error: {str(e)}", err=True)

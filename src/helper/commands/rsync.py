"""Rsync file synchronization commands for the helper CLI."""

import subprocess
import sys

import click

from ..rich_help import RichHelpCommand


@click.command(cls=RichHelpCommand)
@click.argument("source")
@click.argument("dest")
def rsync(source, dest):
    """Synchronize files using rsync with common options.

    This command provides a convenient shorthand for rsync with archive (-a),
    verbose (-v), human-readable (-h), compress (-z), progress (--progress),
    inplace (--inplace), and partial (--partial) options.

    Equivalent to: rsync -havz --progress --inplace --partial SOURCE DEST

    Examples:
        helper rsync /source/dir /dest/dir
        helper rsync user@host:/remote/path /local/path
    """
    cmd = ["rsync", "-havz", "--progress", "--inplace", "--partial", source, dest]

    try:
        # Show the command being executed
        click.echo(f"Executing: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"rsync failed with return code {e.returncode}", err=True)
        sys.exit(e.returncode)
    except FileNotFoundError:
        click.echo("Error: rsync command not found. Please install rsync.", err=True)
        sys.exit(1)

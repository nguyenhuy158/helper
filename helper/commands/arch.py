from ..utils import run_cmd
import click

@click.command()
def arch():
    """Show CPU architecture"""
    cmd = "uname -m"
    run_cmd(cmd)

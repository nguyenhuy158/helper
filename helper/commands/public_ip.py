from ..utils import run_cmd
import click

@click.command()
def public_ip():
    """Show public IP"""
    cmd = "curl -s ifconfig.me"
    run_cmd(cmd)

import click
from helper import __version__
from helper.utils import run_cmd


@click.command()
def public_ip():
    """Show public IP address.
    
    Version: {}
    
    Retrieves and displays the public IP address of the current machine.
    Uses https://ifconfig.me as the primary service and falls back to curl
    if the primary method fails.
    """.format(__version__)
    cmd = "curl -s ifconfig.me"
    run_cmd(cmd)

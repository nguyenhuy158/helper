from ..utils import run_cmd
import click


@click.command()
def public_ip():
    """Show public IP address.
    
    Version: 0.1.19
    
    Retrieves and displays the public IP address of the current machine.
    Uses https://ifconfig.me as the primary service and falls back to curl
    if the primary method fails.
    """
    cmd = "curl -s ifconfig.me"
    run_cmd(cmd)

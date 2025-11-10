import click
from helper import __version__
from helper.utils import run_cmd


@click.command()
def public_ip():
    """Display the public (external) IP address.
    
    This command retrieves and displays your public IP address as seen from the internet.
    It's useful for checking your current external network identity.
    
    Examples:
        $ h pubip
        203.0.113.45
        
    Note: Requires an active internet connection. Uses ifconfig.me service by default.
    """
    cmd = "curl -s ifconfig.me"
    run_cmd(cmd)

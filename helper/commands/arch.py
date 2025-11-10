import click
from helper import __version__
from helper.utils import run_cmd


@click.command()
def arch():
    """Display system architecture information.
    
    Shows the machine hardware name, which is useful for determining
    if you're running on x86_64, arm64, or other architectures.
    
    Equivalent to running 'uname -m' in the terminal.
    
    Example:
        $ h arch
        arm64
    """
    cmd = "uname -m"
    run_cmd(cmd)

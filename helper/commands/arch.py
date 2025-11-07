from ..utils import run_cmd
import click


@click.command()
def arch():
    """Show CPU architecture information.
    
    Version: 0.1.19
    Displays the machine hardware name (equivalent to 'uname -m').
    """
    cmd = "uname -m"
    run_cmd(cmd)

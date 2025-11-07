import click
from helper import __version__
from helper.utils import run_cmd


@click.command()
def arch():
    """Show CPU architecture information.
    
    Version: {}
    Displays the machine hardware name (equivalent to 'uname -m').
    """.format(__version__)
    cmd = "uname -m"
    run_cmd(cmd)

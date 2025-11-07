import click
import subprocess
from ..utils import run_cmd


def check_speedtest_installed():
    """Check if speedtest-cli is installed."""
    try:
        subprocess.run(
            ["which", "speedtest-cli"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


@click.command()
@click.option("--simple", "-s", is_flag=True, help="Only show basic speed information")
def speed(simple):
    """Test internet speed using speedtest-cli"""
    if not check_speedtest_installed():
        click.echo("Error: speedtest-cli is not installed. Please install it first.")
        click.echo("You can install it with: pip install speedtest-cli")
        return

    cmd = "speedtest-cli"
    if simple:
        cmd += " --simple"

    run_cmd(cmd)


# Add aliases for the command
speed_test = speed
sp = speed

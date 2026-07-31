"""Journalctl log commands."""

import platform

import click


@click.command(name="journalctl")
def journalctl_cmd():
    """Display useful journalctl options and examples for Linux systemd logs."""
    system = platform.system().lower()

    if system != "linux":
        click.echo("journalctl is specific to Linux systems with systemd.")
        return

    click.echo("Useful journalctl options and examples:")
    click.echo()
    click.echo("Viewing logs:")
    click.echo("  journalctl                           # View all logs")
    click.echo("  journalctl -n 50                     # View last 50 lines")
    click.echo("  journalctl -f                         # Follow logs in real-time")
    click.echo("  journalctl -u nginx                   # View logs for specific unit")
    click.echo("  journalctl -p err                     # View error priority logs")
    click.echo()
    click.echo("Filtering by time:")
    click.echo("  journalctl --since yesterday          # Logs since yesterday")
    click.echo("  journalctl --since '2023-01-01'       # Logs since specific date")
    click.echo("  journalctl --until '2023-12-31'       # Logs until specific date")
    click.echo("  journalctl --since '1 hour ago'       # Logs from last hour")
    click.echo()
    click.echo("Managing journal size:")
    click.echo("  journalctl --vacuum-size=100M         # Keep only 100MB of logs")
    click.echo("  journalctl --vacuum-time=2weeks       # Keep only logs from last 2 weeks")
    click.echo()
    click.echo("Other useful options:")
    click.echo("  journalctl --no-pager                 # Output without pager")
    click.echo("  journalctl -o json                    # Output in JSON format")
    click.echo("  journalctl --list-boots               # List boot sessions")
    click.echo("  journalctl -b -1                      # Logs from previous boot")


def journalctl():
    """Journalctl command group."""
    return journalctl_cmd

"""Command to display all system information."""
import click
from . import internal_ip, public_ip, arch, system_info


def get_info():
    """Get all system information as a dictionary."""
    return {
        'internal_ip': internal_ip.get_internal_ip(),
        'public_ip': public_ip.get_public_ip(),
        'arch': arch.get_arch(),
        'system_info': system_info.get_info()
    }


def register_all_command(cli):
    """Register the 'all' command with the CLI.

    Args:
        cli: The main CLI group
    """
    @cli.command()
    @click.pass_context
    def all(ctx):
        """Show all info"""
        info = get_info()

        click.echo("=== Internal IP ===")
        click.echo(info['internal_ip'])

        click.echo("\n=== Public IP ===")
        click.echo(info['public_ip'])

        click.echo("\n=== Architecture ===")
        click.echo(info['arch'])

        # NixOS command doesn't accept arguments, so we'll just run it directly
        click.echo("\n=== NixOS (Skipped) ==="
                 "\nNote: NixOS version check skipped as it requires direct execution"
                 "\nTo check NixOS version, run: h nix")

        click.echo("\n=== System Info ===")
        # Format system_info
        si = info['system_info']
        if si:
            click.echo("=" * 40 + " System Information " + "=" * 40)
            click.echo(f"System: {si['system']['system']} {si['system']['release']}")
            click.echo(f"Node Name: {si['system']['node']}")
            click.echo(f"Machine: {si['system']['machine']}")
            click.echo(f"Processor: {si['system']['processor']}")

            click.echo("\n" + "=" * 40 + " OS Version " + "=" * 40)
            click.echo(si['os_version'])

            click.echo("\n" + "=" * 40 + " Uptime " + "=" * 40)
            click.echo(si['uptime'])

            click.echo("\n" + "=" * 40 + " CPU Info " + "=" * 40)
            click.echo(f"CPU Cores: {si['cpu']['cores']}")
            if 'cpu' in si['cpu']:
                click.echo(f"CPU: {si['cpu']['cpu']}")
            if 'load_avg' in si['cpu']:
                click.echo(f"Load Average: {si['cpu']['load_avg']}")

            click.echo("\n" + "=" * 40 + " Memory Information " + "=" * 40)
            if isinstance(si['memory'], dict):
                click.echo(
                    f"Total: {si['memory']['total']}\n"
                    f"Used:  {si['memory']['used']}\n"
                    f"Free:  {si['memory']['free']}\n"
                    f"Usage: {si['memory']['usage']}"
                )
            else:
                click.echo(si['memory'])

            click.echo("\n" + "=" * 40 + " Disk Information " + "=" * 40)
            click.echo(si['disks'])

    return all

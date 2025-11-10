"""Command to display all system information."""
import click
from .. import commands


def register_all_command(cli):
    """Register the 'all' command with the CLI.
    
    Args:
        cli: The main CLI group
    """
    @cli.command()
    @click.pass_context
    def all(ctx):
        """Show all info"""
        # Get the parent command (the main CLI group)
        parent = ctx.parent.command
        
        click.echo("=== Internal IP ===")
        ctx.invoke(parent.get_command(ctx, "ip"))
        
        click.echo("\n=== Public IP ===")
        ctx.invoke(parent.get_command(ctx, "pubip"))
        
        click.echo("\n=== Architecture ===")
        ctx.invoke(parent.get_command(ctx, "arch"))
        
        # NixOS command doesn't accept arguments, so we'll just run it directly
        click.echo("\n=== NixOS (Skipped) ==="
                 "\nNote: NixOS version check skipped as it requires direct execution"
                 "\nTo check NixOS version, run: h nix")
        
        click.echo("\n=== System Info ===")
        ctx.invoke(parent.get_command(ctx, "si"))

    return all

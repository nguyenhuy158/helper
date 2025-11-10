"""Command to display all system information."""
import click


def register_all_command(cli):
    """Register the 'all' command with the CLI.
    
    Args:
        cli: The main CLI group
    """
    @cli.command()
    @click.pass_context
    def all(ctx):
        """Show all info"""
        click.echo("=== Internal IP ===")
        ctx.invoke(ctx.command.parent.get_command(ctx, "internal-ip"))
        click.echo("\n=== Public IP ===")
        ctx.invoke(ctx.command.parent.get_command(ctx, "public-ip"))
        click.echo("\n=== Architecture ===")
        ctx.invoke(ctx.command.parent.get_command(ctx, "arch"))
        click.echo("\n=== NixOS ===")
        ctx.invoke(ctx.command.parent.get_command(ctx, "nixos"), "version")
        click.echo("\n=== System Info ===")
        ctx.invoke(ctx.command.parent.get_command(ctx, "system-info"))

    return all

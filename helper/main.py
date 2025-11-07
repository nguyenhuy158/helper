import click
from .commands import internal_ip, public_ip, arch, nixos, docker

@click.group()
def cli():
    """Helper CLI - quick system info"""
    pass

# Register all commands
cli.add_command(internal_ip.internal_ip)
cli.add_command(public_ip.public_ip)
cli.add_command(arch.arch)
cli.add_command(nixos.nixos, name="nixos")
cli.add_command(docker.docker, name="docker")

@cli.command()
@click.pass_context
def all(ctx):
    """Show all info"""
    click.echo("=== Internal IP ===")
    ctx.invoke(internal_ip.internal_ip)
    click.echo("\n=== Public IP ===")
    ctx.invoke(public_ip.public_ip)
    click.echo("\n=== Architecture ===")
    ctx.invoke(arch.arch)
    click.echo("\n=== NixOS ===")
    ctx.invoke(nixos.nixos, 'version')

if __name__ == "__main__":
    cli()

import click
import logging
import sys
from .commands import internal_ip, public_ip, arch, nixos, docker

class VerbosityCommand(click.Command):
    def parse_args(self, ctx, args):
        # Initialize verbosity from context if it exists
        ctx.ensure_object(dict)
        verbose = ctx.obj.get('verbosity', 0)
        
        # Process args for verbosity flags
        new_args = []
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '--verbose':
                verbose += 1
            elif arg.startswith('-v'):
                verbose += arg.count('v')
            else:
                new_args.append(arg)
            i += 1
        
        # Update verbosity in context
        ctx.obj['verbosity'] = verbose
        
        # Set up logging
        self._setup_logging(verbose)
        
        # Continue with normal argument parsing
        return super().parse_args(ctx, new_args)
    
    def _setup_logging(self, verbose):
        logger = logging.getLogger('docker-helper')
        if verbose >= 3:
            logger.setLevel(logging.DEBUG)
        elif verbose == 2:
            logger.setLevel(logging.INFO)
        elif verbose == 1:
            logger.setLevel(logging.WARNING)
        else:
            logger.setLevel(logging.ERROR)

class VerbosityGroup(click.Group):
    def make_context(self, info_name, args, parent=None, **extra):
        # Pre-process args to find verbosity flags
        verbose = 0
        processed_args = []
        
        for arg in args:
            if arg == '--verbose':
                verbose += 1
            elif arg.startswith('-v'):
                verbose += arg.count('v')
            else:
                processed_args.append(arg)
        
        # Create context with processed args
        ctx = super().make_context(info_name, processed_args, parent=parent, **extra)
        
        # Set verbosity in context
        ctx.ensure_object(dict)
        ctx.obj['verbosity'] = verbose
        
        # Set up logging
        logger = logging.getLogger('docker-helper')
        if verbose >= 3:
            logger.setLevel(logging.DEBUG)
        elif verbose == 2:
            logger.setLevel(logging.INFO)
        elif verbose == 1:
            logger.setLevel(logging.WARNING)
        else:
            logger.setLevel(logging.ERROR)
        
        return ctx

@click.group(cls=VerbosityGroup)
def cli():
    """Helper CLI - quick system info"""
    # Set up basic logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.ERROR
    )

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

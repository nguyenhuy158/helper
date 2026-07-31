"""The docker command group."""

import click

from ...rich_help import RichHelpGroup
from .core import Verbosity, check_docker, logger


def _launch_dashboard(ctx):
    """Launch the full-screen Textual dashboard (optional dependency)."""
    try:
        from .dashboard import DockerDashboard
    except ImportError:
        click.echo(
            "Error: the interactive dashboard requires the 'textual' package.\n"
            "Install it with: uv tool install 'helper-cli[tui]'"
            "  (or: pip install 'helper-cli[tui]')",
            err=True,
        )
        ctx.exit(1)
    DockerDashboard().run()


@click.group(cls=RichHelpGroup, invoke_without_command=True)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity (can be used multiple times)",
)
@click.pass_context
def docker(ctx, verbose):
    """Docker container and image management.

    Without a subcommand, opens a full-screen interactive dashboard
    (lazydocker-style) for containers and images.

    Subcommands:
      ui        Open the interactive dashboard (same as no subcommand)
      ps        List containers
      run       Run a command in a new container
      rm        Remove one or more containers
      rmi       Remove one or more images
      url       Show containers with their HTTP/HTTPS URLs
      clean     Clean up disk space by removing unused resources
      disk-used Show Docker disk usage information

    Examples:
      h d               # Open the interactive dashboard
      h d ps            # List running containers
      h d run nginx     # Run an nginx container
      h d rm container  # Remove a container
      h d clean         # Clean up unused Docker resources
      h d disk-used     # Show disk usage
    """
    ctx.ensure_object(dict)

    # Get verbosity from parent context if it exists, otherwise use the flag value
    parent_verbosity = ctx.obj.get("verbosity", 0) if hasattr(ctx, "obj") else 0
    verbosity_level = max(verbose, parent_verbosity)

    # Initialize verbosity (also sets the log level)
    verbosity = Verbosity(verbosity=verbosity_level)
    ctx.obj["verbosity"] = verbosity

    logger.debug(f"Docker command group initialized with verbosity level: {verbosity_level}")

    verbosity.debug("Initializing Docker command group")
    if not check_docker(verbosity):
        click.echo(
            "Error: Docker is not installed or not running. Please start Docker and try again.",
            err=True,
        )
        ctx.exit(1)

    if ctx.invoked_subcommand is None:
        _launch_dashboard(ctx)


@docker.command()
@click.pass_context
def ui(ctx):
    """Open the full-screen interactive dashboard (lazydocker-style)."""
    _launch_dashboard(ctx)

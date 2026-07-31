"""The docker command group."""

import logging

import click

from .core import Verbosity, check_docker, logger


@click.group()
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity (can be used multiple times)",
)
@click.pass_context
def docker(ctx, verbose):
    """Docker container and image management.

    Manage Docker containers and images with subcommands for common operations.

    Subcommands:
      ps        List containers
      run       Run a command in a new container
      rm        Remove one or more containers
      rmi       Remove one or more images
      url       Show containers with their HTTP/HTTPS URLs
      clean     Clean up disk space by removing unused resources
      disk-used Show Docker disk usage information

    Examples:
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

    # Initialize verbosity
    verbosity = Verbosity(verbosity=verbosity_level)
    ctx.obj["verbosity"] = verbosity

    # Configure logger with verbosity level
    logger.setLevel(
        logging.DEBUG
        if verbosity_level >= 3
        else (
            logging.INFO
            if verbosity_level == 2
            else logging.WARNING
            if verbosity_level == 1
            else logging.ERROR
        )
    )

    logger.debug("Docker command group initialized with verbosity level: %s", verbosity_level)

    verbosity.debug("Initializing Docker command group")
    if not check_docker(verbosity):
        click.echo(
            "Error: Docker is not installed or not running. Please start Docker and try again.",
            err=True,
        )
        ctx.exit(1)

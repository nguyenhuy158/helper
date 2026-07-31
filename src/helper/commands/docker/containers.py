"""Container subcommands: ps, run, rm."""

import json
import subprocess

import click

from .cli import docker


@docker.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.option("--all", "-a", is_flag=True, help="Show all containers (default shows just running)")
@click.option(
    "--all-containers",
    is_flag=True,
    help="Show all containers (default shows just running)",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json"], case_sensitive=False),
    default="table",
    help="Output format",
)
@click.help_option(
    "-h",
    "--help",
)
@click.pass_context
def ps(ctx, all_containers, output_format):
    """List containers."""
    verbosity = ctx.obj["verbosity"]
    cmd = ["docker", "ps"]
    if all_containers:
        cmd.append("-a")

    try:
        verbosity.debug(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            if output_format == "json":
                # Try to parse and pretty-print JSON output
                try:
                    data = json.loads(result.stdout)
                    click.echo(json.dumps(data, indent=2))
                except json.JSONDecodeError:
                    # Fall back to raw output if not valid JSON
                    click.echo(result.stdout)
            else:
                # For table format, try to align columns
                lines = result.stdout.strip().split("\n")
                if len(lines) > 1:
                    # Parse as JSON to handle special characters in values
                    try:
                        data = [json.loads(line) for line in lines[1:]]
                        headers = data[0].keys()
                        rows = [[item.get(header, "") for header in headers] for item in data]

                        # Calculate column widths
                        col_widths = [
                            max(
                                len(str(header)),
                                max((len(str(row[i])) for row in rows), default=0),
                            )
                            for i, header in enumerate(headers)
                        ]

                        # Print header
                        header_row = "  ".join(
                            header.ljust(width) for header, width in zip(headers, col_widths)
                        )
                        click.echo(header_row)
                        click.echo("-" * len(header_row))

                        # Print rows
                        for row in rows:
                            click.echo(
                                "  ".join(
                                    str(cell).ljust(width) for cell, width in zip(row, col_widths)
                                )
                            )
                    except Exception as e:
                        verbosity.debug(f"Error formatting table: {e!s}")
                        # Fall back to raw output if processing fails
                        click.echo(result.stdout)
                else:
                    click.echo(result.stdout)
        else:
            error_msg = f"Error: {result.stderr}"
            verbosity.error(error_msg)
            click.echo(error_msg, err=True)
    except subprocess.CalledProcessError as e:
        error_msg = f"Command failed: {e!s}"
        verbosity.error(error_msg)
        click.echo(error_msg, err=True)
    except Exception as e:
        error_msg = f"Unexpected error: {e!s}"
        verbosity.error(error_msg)
        click.echo(error_msg, err=True)


@docker.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.argument("image", required=False)
@click.option("--name", help="Assign a name to the container")
@click.option("--port", "-p", multiple=True, help="Publish a container's port(s) to the host")
@click.option(
    "--detach",
    "-d",
    is_flag=True,
    help="Run container in background and print container ID",
)
@click.option("--env", "-e", multiple=True, help="Set environment variables")
@click.option("--volume", "-v", multiple=True, help="Bind mount a volume")
@click.pass_context
def run(ctx, image, name, port, detach, env, volume):
    """Run a command in a new container."""
    verbosity = ctx.obj["verbosity"]
    cmd = ["docker", "run"]

    if name:
        cmd.extend(["--name", name])
        verbosity.debug(f"Setting container name: {name}")

    for p in port:
        cmd.extend(["-p", p])
        verbosity.debug(f"Adding port mapping: {p}")

    if detach:
        cmd.append("-d")
        verbosity.debug("Running container in detached mode")

    for e in env:
        cmd.extend(["-e", e])
        verbosity.debug(f"Setting environment variable: {e}")

    for v in volume:
        cmd.extend(["-v", v])
        verbosity.debug(f"Mounting volume: {v}")

    if image:
        cmd.append(image)
        verbosity.debug(f"Using image: {image}")

    # Add any remaining arguments
    if hasattr(ctx, "args") and ctx.args:
        cmd.extend(ctx.args)
        verbosity.debug(f"Additional arguments: {' '.join(ctx.args)}")

    try:
        verbosity.debug(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            if result.stdout:
                click.echo(result.stdout.strip())
            verbosity.info("Container started successfully")
        else:
            error_msg = f"Error: {result.stderr.strip() or 'Unknown error'}"
            verbosity.error(error_msg)
            click.echo(error_msg, err=True)
            ctx.exit(1)

    except Exception as e:
        error_msg = f"Failed to run container: {e!s}"
        verbosity.error(error_msg, exc_info=verbosity.verbosity >= 3)
        click.echo(error_msg, err=True)
        ctx.exit(1)


@docker.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.argument("containers", nargs=-1, required=False)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force the removal of a running container (uses SIGKILL)",
)
@click.option(
    "--volumes",
    "-v",
    is_flag=True,
    help="Remove anonymous volumes associated with the container",
)
@click.pass_context
def rm(ctx, containers, force, volumes):
    """Remove one or more containers."""
    verbosity = ctx.obj["verbosity"]
    cmd = ["docker", "rm"]

    if force:
        cmd.append("-f")
        verbosity.debug("Force removal enabled")
    if volumes:
        cmd.append("-v")
        verbosity.debug("Volume removal enabled")

    # Get containers from both the containers argument and any remaining args
    all_containers = list(containers)
    if hasattr(ctx, "args") and ctx.args:
        all_containers.extend(ctx.args)

    if not all_containers:
        error_msg = "Error: You must specify at least one container"
        verbosity.error(error_msg)
        click.echo(error_msg, err=True)
        ctx.exit(1)

    cmd.extend(all_containers)
    verbosity.debug(f"Removing containers: {', '.join(all_containers)}")

    try:
        verbosity.debug(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            if result.stdout.strip():
                click.echo(result.stdout.strip())
            verbosity.info(f"Successfully removed {len(all_containers)} container(s)")
        else:
            error_msg = f"Error: {result.stderr.strip() or 'Unknown error'}"
            verbosity.error(error_msg)
            click.echo(error_msg, err=True)
            ctx.exit(1)

    except Exception as e:
        error_msg = f"Failed to remove containers: {e!s}"
        verbosity.error(error_msg, exc_info=verbosity.verbosity >= 3)
        click.echo(error_msg, err=True)
        ctx.exit(1)

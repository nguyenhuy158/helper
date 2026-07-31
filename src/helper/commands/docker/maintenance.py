"""Maintenance subcommands: clean, disk-used."""

import subprocess

import click

from .cli import docker


@docker.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be cleaned without actually cleaning",
)
@click.pass_context
def clean(ctx, dry_run):
    """Clean up Docker disk space by removing dangling images and unused resources."""
    verbosity = ctx.obj["verbosity"]

    verbosity.info("Starting Docker cleanup process")

    # Step 1: Remove dangling images
    verbosity.info("Removing dangling images...")
    try:
        # Get list of dangling images
        result = subprocess.run(
            ["docker", "images", "-f", "dangling=true", "-q"],
            capture_output=True,
            text=True,
            check=True,
        )
        dangling_images = result.stdout.strip().split("\n") if result.stdout.strip() else []

        if dangling_images:
            verbosity.info(f"Found {len(dangling_images)} dangling image(s) to remove")
            if not dry_run:
                rmi_cmd = ["docker", "rmi"] + dangling_images
                verbosity.debug(f"Running: {' '.join(rmi_cmd)}")
                rmi_result = subprocess.run(rmi_cmd, capture_output=True, text=True, check=False)
                if rmi_result.returncode == 0:
                    verbosity.info("Successfully removed dangling images")
                    if rmi_result.stdout.strip():
                        click.echo("Removed dangling images:")
                        click.echo(rmi_result.stdout.strip())
                else:
                    verbosity.warning(f"Failed to remove some dangling images: {rmi_result.stderr}")
            else:
                click.echo(f"Would remove {len(dangling_images)} dangling image(s)")
        else:
            verbosity.info("No dangling images found")

    except subprocess.CalledProcessError as e:
        verbosity.error(f"Failed to list or remove dangling images: {e.stderr}")
        click.echo("Error: Failed to remove dangling images", err=True)
    except Exception as e:
        verbosity.error(f"Unexpected error removing dangling images: {e!s}")
        click.echo("Error: Unexpected error during cleanup", err=True)

    # Step 2: Run system prune
    verbosity.info("Running system prune...")
    try:
        prune_cmd = ["docker", "system", "prune", "-f"]
        if dry_run:
            # For dry run, we can't really dry run system prune, so just show what it would do
            click.echo("Would run: docker system prune -f")
            click.echo("This would remove:")
            click.echo("- All stopped containers")
            click.echo("- All networks not used by at least one container")
            click.echo("- All dangling images")
            click.echo("- All dangling build cache")
        else:
            verbosity.debug(f"Running: {' '.join(prune_cmd)}")
            prune_result = subprocess.run(prune_cmd, capture_output=True, text=True, check=False)
            if prune_result.returncode == 0:
                verbosity.info("System prune completed successfully")
                if prune_result.stdout.strip():
                    click.echo("System prune results:")
                    click.echo(prune_result.stdout.strip())
                else:
                    click.echo("System prune completed (no output)")
            else:
                verbosity.error(f"System prune failed: {prune_result.stderr}")
                click.echo("Error: System prune failed", err=True)
    except Exception as e:
        verbosity.error(f"Unexpected error during system prune: {e!s}")
        click.echo("Error: Unexpected error during system prune", err=True)

    if dry_run:
        click.echo("\nThis was a dry run. No actual cleanup was performed.")
    else:
        verbosity.info("Docker cleanup completed")
        click.echo("Docker cleanup completed successfully.")


@docker.command("disk-used")
@click.pass_context
def disk_used(ctx):
    """Show Docker disk usage information."""
    verbosity = ctx.obj["verbosity"]

    verbosity.info("Retrieving Docker disk usage information")

    try:
        cmd = ["docker", "system", "df", "-v"]
        verbosity.debug(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        if result.returncode == 0:
            verbosity.info("Successfully retrieved disk usage information")
            click.echo(result.stdout.strip())
        else:
            error_msg = f"Error: {result.stderr.strip() or 'Unknown error'}"
            verbosity.error(error_msg)
            click.echo(error_msg, err=True)
            ctx.exit(1)

    except subprocess.CalledProcessError as e:
        error_msg = f"Command failed: {e!s}"
        verbosity.error(error_msg)
        click.echo(error_msg, err=True)
        ctx.exit(1)
    except Exception as e:
        error_msg = f"Unexpected error: {e!s}"
        verbosity.error(error_msg, exc_info=verbosity.verbosity >= 3)
        click.echo(error_msg, err=True)
        ctx.exit(1)

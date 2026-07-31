"""Image subcommands: rmi."""

import subprocess

import click

from .cli import docker


@docker.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.argument("image", required=False)
@click.option(
    "--all-tags",
    "-a",
    is_flag=True,
    help="Remove all versions of the image with the given name",
)
@click.option("--force", "-f", is_flag=True, help="Force removal of the image")
@click.option("--no-prune", is_flag=True, help="Do not delete untagged parents")
@click.pass_context
def rmi(ctx, image, all_tags, force, no_prune):
    """Remove one or more images."""
    verbosity = ctx.obj["verbosity"]
    cmd = ["docker", "rmi"]

    if force:
        cmd.append("-f")
        verbosity.debug("Force removal enabled")
    if no_prune:
        cmd.append("--no-prune")
        verbosity.debug("Pruning of untagged parents disabled")

    # Get images from both the image argument and any remaining args
    images = []
    if image:
        images.append(image)
    if hasattr(ctx, "args") and ctx.args:
        images.extend(ctx.args)

    if not images and not all_tags:
        error_msg = "Error: You must specify at least one image"
        verbosity.error(error_msg)
        click.echo(error_msg, err=True)
        ctx.exit(1)

    if all_tags:
        if not images:
            error_msg = "Error: You must specify an image name when using --all-tags"
            verbosity.error(error_msg)
            click.echo(error_msg, err=True)
            ctx.exit(1)

        # Get all tags for the specified images
        all_tags_to_remove = []
        for img in images:
            verbosity.debug(f"Finding all tags for image: {img}")
            try:
                result = subprocess.run(
                    ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}", img],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result.returncode == 0 and result.stdout.strip():
                    tags = [line for line in result.stdout.split("\n") if line]
                    verbosity.debug(f"Found {len(tags)} tags for {img}")
                    all_tags_to_remove.extend(tags)
                else:
                    verbosity.warning(f"No images found matching '{img}'")

            except Exception as e:
                verbosity.error(
                    f"Error finding tags for {img}: {e!s}",
                    exc_info=verbosity.verbosity >= 3,
                )
                continue

        if not all_tags_to_remove:
            error_msg = "No matching images found to remove"
            verbosity.error(error_msg)
            click.echo(error_msg, err=True)
            ctx.exit(1)

        cmd.extend(all_tags_to_remove)
        verbosity.info(f"Removing {len(all_tags_to_remove)} image(s) with all tags")

    else:
        cmd.extend(images)
        verbosity.info(f"Removing {len(images)} image(s)")

    try:
        verbosity.debug(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            if result.stdout.strip():
                click.echo(result.stdout.strip())
            removed_count = len(cmd) - 2  # Subtract 'docker rmi' from the command
            verbosity.info(f"Successfully removed {removed_count} image(s)")
        else:
            error_msg = f"Error: {result.stderr.strip() or 'Unknown error'}"
            verbosity.error(error_msg)
            click.echo(error_msg, err=True)
            ctx.exit(1)

    except Exception as e:
        error_msg = f"Failed to remove images: {e!s}"
        verbosity.error(error_msg, exc_info=verbosity.verbosity >= 3)
        click.echo(error_msg, err=True)
        ctx.exit(1)

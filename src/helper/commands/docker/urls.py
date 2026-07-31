"""The url subcommand: show containers with their HTTP/HTTPS URLs."""

import subprocess

import click

from .cli import docker
from .core import get_container_ports


def _parse_port_string(port_str):
    """Parse port string and return port number and protocol."""
    port_num = None
    protocol = "tcp"  # default protocol

    # Handle format like '0.0.0.0:8080->80/tcp' (check before the plain
    # '/' case: the host part may contain '/' after splitting on it)
    if "->" in port_str:
        _, port_mapping = port_str.split("->", 1)
        if "/" in port_mapping:
            port_num, protocol = port_mapping.split("/", 1)
        else:
            port_num = port_mapping
    # Handle format like '8069/tcp' or '80/http'
    elif "/" in port_str:
        port_num, protocol = port_str.split("/", 1)
    else:
        port_num = port_str

    # Clean up port number (remove any non-numeric characters)
    port_num = "".join(c for c in port_num if c.isdigit())
    return port_num, protocol


def _process_container_urls(container_id, name, verbosity):
    """Process port mappings for a container and return list of URLs."""
    urls = []
    port_mappings = get_container_ports(container_id, verbosity)
    verbosity.debug(f"Found {len(port_mappings)} port mappings for {name}")

    for port in port_mappings:
        if not port.get("host_port") or not port.get("container_port"):
            verbosity.debug(f"Skipping incomplete port mapping: {port}")
            continue

        verbosity.debug(f"Checking port mapping: {port}")
        verbosity.debug(f"Container name: {name}, Port: {port['container_port']}")

        port_num, protocol = _parse_port_string(port["container_port"])

        if port_num:
            scheme = "http"
            host = port["host_ip"]
            if ":" in host and not host.startswith("["):
                host = f"[{host}]"

            url = f"{scheme}://{host}:{port['host_port']}"
            urls.append({"url": url, "port": port_num, "protocol": protocol})
            verbosity.info(f"Added URL for {name}: {url} (port {port_num}/{protocol})")

    return urls


def _parse_container_line(line, verbosity):
    """Parse a container line and return container info dict."""
    verbosity.debug(f"Processing container line: {line}")
    container_id, name, status, ports = line.split("|", 3)
    is_running = "Up" in status
    verbosity.info(
        f"Container: ID={container_id[:12]}, Name={name}, Status={status}, Running={is_running}"
    )

    container_info = {
        "id": container_id[:12],  # Short ID
        "name": name,
        "status": status,
        "urls": _process_container_urls(container_id, name, verbosity),
    }

    return container_info, is_running


def _display_containers(containers, title, color, dim=False, verbosity=None):
    """Display a list of containers with their URLs."""
    if not containers:
        return

    click.secho(f"\n{title}", fg=color, bold=True)
    for container in containers:
        if verbosity:
            verbosity.debug(f"Displaying container: {container['name']}")
        name_style = click.style(container["name"], dim=dim)
        if not dim:
            name_style = click.style(name_style, bold=True)
        click.echo(f"\n{click.style('●', fg=color)} {name_style} ({container['id']})")

        if container["urls"]:
            if verbosity:
                verbosity.info(f"Found {len(container['urls'])} URLs for {container['name']}")
            for url_info in container["urls"]:
                if verbosity:
                    verbosity.debug(f"Displaying URL: {url_info['url']}")
                url_style = click.style(url_info["url"], fg="blue", underline=True, dim=dim)
                click.echo(f"   {click.style('→', fg='blue')} {url_style}")
        else:
            if verbosity:
                verbosity.debug(f"No URLs found for {container['name']}")


@docker.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.option(
    "--show-all",
    "-a",
    is_flag=True,
    help="Show all containers (default shows just running)",
)
@click.option("--http-only", "-h", is_flag=True, help="Show only containers with HTTP/HTTPS ports")
@click.pass_context
def url(ctx, show_all, http_only):
    """Show containers with their HTTP/HTTPS URLs."""
    verbosity = ctx.obj["verbosity"]
    verbosity.info(f"Starting url command with show_all={show_all}, http_only={http_only}")

    try:
        # Get all containers
        cmd = ["docker", "ps", "--format", "{{.ID}}|{{.Names}}|{{.Status}}|{{.Ports}}"]
        if show_all:
            cmd.append("-a")

        verbosity.debug(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            error_msg = f"Error listing containers: {result.stderr}"
            verbosity.error(error_msg)
            click.echo(error_msg, err=True)
            return

        verbosity.debug(f"Command output: {result.stdout}")

        running_containers = []
        stopped_containers = []

        container_lines = result.stdout.strip().split("\n")
        verbosity.info(f"Found {len(container_lines)} container(s)")

        for line in container_lines:
            if not line.strip():
                verbosity.debug("Skipping empty line")
                continue

            try:
                container_info, is_running = _parse_container_line(line, verbosity)

                # If http_only is True and no HTTP URLs, skip this container
                if http_only and not container_info["urls"]:
                    continue

                if is_running:
                    running_containers.append(container_info)
                else:
                    stopped_containers.append(container_info)

            except Exception as e:
                click.echo(f"Error processing container info: {e}", err=True)
                continue

        # Display containers
        _display_containers(
            running_containers, "🚀 Running Containers:", "green", verbosity=verbosity
        )
        if show_all or not http_only:
            _display_containers(
                stopped_containers,
                "⏸️  Stopped Containers:",
                "yellow",
                dim=True,
                verbosity=verbosity,
            )

        if not running_containers and not stopped_containers:
            msg = "No containers found."
            verbosity.info(msg)
            click.echo(msg)
        else:
            verbosity.info(
                f"Displayed {len(running_containers)} running and "
                f"{len(stopped_containers)} stopped containers"
            )

    except Exception as e:
        error_msg = f"Error in url command: {e!s}"
        verbosity.error(error_msg, exc_info=verbosity.verbosity >= 3)
        click.echo(error_msg, err=True)

"""Shared docker helpers: verbosity, docker availability, port inspection."""

import json
import logging
import subprocess
import sys
from typing import Dict, List

import click

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("docker-helper")


class Verbosity:
    """Handle verbosity levels for logging."""

    def __init__(self, verbosity: int = 0):
        self.verbosity = verbosity
        self.set_level()

    def set_level(self):
        """Set logging level based on verbosity."""
        if self.verbosity >= 3:
            logger.setLevel(logging.DEBUG)
        elif self.verbosity == 2:
            logger.setLevel(logging.INFO)
        elif self.verbosity == 1:
            logger.setLevel(logging.WARNING)
        else:
            logger.setLevel(logging.ERROR)

    def debug(self, msg: str, *args, **kwargs):
        """Log debug message if verbosity >= 3."""
        if self.verbosity >= 3:
            logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        """Log info message if verbosity >= 2."""
        if self.verbosity >= 2:
            logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        """Log warning message if verbosity >= 1."""
        if self.verbosity >= 1:
            logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        """Log error message regardless of verbosity."""
        logger.error(msg, *args, **kwargs)


def get_container_ports(container_id: str, verbosity: Verbosity) -> List[Dict]:
    """Get exposed ports and IPs for a container.

    Args:
        container_id: The ID of the container to inspect
        verbosity: Verbosity level for logging

    Returns:
        List of dictionaries containing port mappings
    """
    verbosity.debug("Getting ports for container %s", container_id)
    try:
        result = subprocess.run(
            [
                "docker",
                "inspect",
                "--format",
                "{{range $p, $conf := .NetworkSettings.Ports}}"
                "{{range $h, $hosts := $conf}}"
                "{{$p}}|{{$hosts.HostIp}}|{{$hosts.HostPort}};"
                "{{end}}{{end}}",
                container_id,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        ports = []
        raw_output = result.stdout.strip()
        verbosity.debug("Raw port mappings: %s", raw_output)

        if not raw_output:
            return ports

        for mapping in raw_output.split(";"):
            if not mapping:
                continue
            try:
                container_port, host_ip, host_port = mapping.split("|")
                verbosity.debug(
                    "Processing mapping: container=%s, host_ip=%s, host_port=%s",
                    container_port,
                    host_ip,
                    host_port,
                )

                if container_port and host_port:
                    port_info = {
                        "container_port": container_port.split("/")[0],  # Remove /tcp or /udp
                        "host_ip": (host_ip if host_ip not in ("0.0.0.0", "") else "localhost"),
                        "host_port": host_port,
                    }
                    verbosity.info("Added port mapping: %s", port_info)
                    ports.append(port_info)
                else:
                    verbosity.debug("Skipping incomplete mapping: %s", mapping)
            except ValueError as e:
                verbosity.warning("Failed to parse mapping '%s': %s", mapping, e)

        verbosity.debug("Final port mappings: %s", ports)
        return ports

    except subprocess.CalledProcessError as e:
        verbosity.error("Failed to get container info: %s", e.stderr)
    except Exception as e:
        verbosity.error(
            "Unexpected error in get_container_ports: %s",
            str(e),
            exc_info=verbosity.verbosity >= 3,
        )
    return []


def check_docker(verbosity: Verbosity) -> bool:
    """Check if Docker is installed and running."""
    verbosity.info("Checking if Docker is installed and running...")
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, text=True, check=False)

        verbosity.debug(f"Docker info command output:\n{result.stdout}")

        if result.returncode != 0:
            verbosity.error(f"Docker is not running or not accessible. Error: {result.stderr}")
            return False

        verbosity.info("Docker is running and accessible")
        return True

    except FileNotFoundError:
        verbosity.error("Docker command not found. Is Docker installed?")
        return False
    except Exception as e:
        verbosity.error(
            f"Unexpected error checking Docker: {e!s}",
            exc_info=verbosity.verbosity >= 3,
        )
        return False


def format_output(output, output_format="table"):
    """Format command output based on the specified format."""
    if output_format == "json":
        try:
            return json.dumps(json.loads(output), indent=2)
        except json.JSONDecodeError:
            return output
    return output


def get_verbosity(ctx: click.Context) -> Verbosity:
    """Get verbosity level from context."""
    # Count the number of 'v's in the --verbose flag
    verbose = ctx.params.get("verbose", 0)
    verbosity = Verbosity(verbosity=verbose)
    verbosity.info(f"Verbosity level set to {verbose}")
    return verbosity

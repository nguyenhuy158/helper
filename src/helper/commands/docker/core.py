"""Shared docker helpers: verbosity, docker availability, port inspection."""

import json
import subprocess
from typing import Dict, List

import click

from ...log import logger, set_level


class Verbosity:
    """Handle verbosity levels for logging."""

    def __init__(self, verbosity: int = 0):
        self.verbosity = verbosity
        self.set_level()

    def set_level(self):
        """Set logging level based on verbosity."""
        set_level(self.verbosity)

    def _log(self, level: str, msg: str, exc_info: bool = False):
        logger.opt(exception=bool(exc_info), depth=2).log(level, msg)

    def debug(self, msg: str, exc_info: bool = False):
        """Log debug message (shown when verbosity >= 3)."""
        self._log("DEBUG", msg, exc_info)

    def info(self, msg: str, exc_info: bool = False):
        """Log info message (shown when verbosity >= 2)."""
        self._log("INFO", msg, exc_info)

    def warning(self, msg: str, exc_info: bool = False):
        """Log warning message (shown when verbosity >= 1)."""
        self._log("WARNING", msg, exc_info)

    def error(self, msg: str, exc_info: bool = False):
        """Log error message regardless of verbosity."""
        self._log("ERROR", msg, exc_info)


def get_container_ports(container_id: str, verbosity: Verbosity) -> List[Dict]:
    """Get exposed ports and IPs for a container.

    Args:
        container_id: The ID of the container to inspect
        verbosity: Verbosity level for logging

    Returns:
        List of dictionaries containing port mappings
    """
    verbosity.debug(f"Getting ports for container {container_id}")
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
        verbosity.debug(f"Raw port mappings: {raw_output}")

        if not raw_output:
            return ports

        for mapping in raw_output.split(";"):
            if not mapping:
                continue
            try:
                container_port, host_ip, host_port = mapping.split("|")
                verbosity.debug(
                    f"Processing mapping: container={container_port}, "
                    f"host_ip={host_ip}, host_port={host_port}"
                )

                if container_port and host_port:
                    port_info = {
                        "container_port": container_port.split("/")[0],  # Remove /tcp or /udp
                        "host_ip": (host_ip if host_ip not in ("0.0.0.0", "") else "localhost"),
                        "host_port": host_port,
                    }
                    verbosity.info(f"Added port mapping: {port_info}")
                    ports.append(port_info)
                else:
                    verbosity.debug(f"Skipping incomplete mapping: {mapping}")
            except ValueError as e:
                verbosity.warning(f"Failed to parse mapping '{mapping}': {e}")

        verbosity.debug(f"Final port mappings: {ports}")
        return ports

    except subprocess.CalledProcessError as e:
        verbosity.error(f"Failed to get container info: {e.stderr}")
    except Exception as e:
        verbosity.error(
            f"Unexpected error in get_container_ports: {e!s}",
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

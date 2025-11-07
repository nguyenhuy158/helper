import click
import subprocess
import json
import re
import logging
import sys
from typing import Dict, List, Tuple, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger('docker-helper')

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
    """Get exposed ports and IPs for a container."""
    verbosity.debug(f"Getting ports for container {container_id}")
    try:
        result = subprocess.run(
            ['docker', 'inspect', '--format',
             '{{range $p, $conf := .NetworkSettings.Ports}}'  # noqa: E501
             '{{range $h, $hosts := $conf}}'
             '{{$p}}|{{$hosts.HostIp}}|{{$hosts.HostPort}};'
             '{{end}}{{end}}',
             container_id],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            verbosity.error(f"Failed to get container info: {result.stderr}")
            return []

        ports = []
        raw_output = result.stdout.strip()
        verbosity.debug(f"Raw port mappings: {raw_output}")

        if raw_output:
            for mapping in raw_output.split(';'):
                if not mapping:
                    continue
                try:
                    container_port, host_ip, host_port = mapping.split('|')
                    verbosity.debug(f"Processing mapping: container={container_port}, host_ip={host_ip}, host_port={host_port}")

                    if container_port and host_port:
                        port_info = {
                            'container_port': container_port.split('/')[0],  # Remove /tcp or /udp
                            'host_ip': host_ip if host_ip not in ('0.0.0.0', '') else 'localhost',
                            'host_port': host_port
                        }
                        verbosity.info(f"Added port mapping: {port_info}")
                        ports.append(port_info)
                    else:
                        verbosity.debug(f"Skipping incomplete mapping: {mapping}")
                except ValueError as e:
                    verbosity.warning(f"Failed to parse mapping '{mapping}': {e}")
                    continue
        verbosity.debug(f"Final port mappings: {ports}")
        return ports
    except Exception as e:
        verbosity.error(f"Unexpected error in get_container_ports: {str(e)}", exc_info=verbosity.verbosity >= 3)
        return []

def check_docker(verbosity: Verbosity) -> bool:
    """Check if Docker is installed and running."""
    verbosity.info("Checking if Docker is installed and running...")
    try:
        result = subprocess.run(['docker', 'info'],
                              capture_output=True,
                              text=True)

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
        verbosity.error(f"Unexpected error checking Docker: {str(e)}", exc_info=verbosity.verbosity >= 3)
        return False

def format_output(output, output_format='table'):
    """Format command output based on the specified format."""
    if output_format == 'json':
        try:
            return json.dumps(json.loads(output), indent=2)
        except json.JSONDecodeError:
            return output
    return output

def get_verbosity(ctx: click.Context) -> Verbosity:
    """Get verbosity level from context."""
    # Count the number of 'v's in the --verbose flag
    verbose = ctx.params.get('verbose', 0)
    verbosity = Verbosity(verbosity=verbose)
    verbosity.info(f"Verbosity level set to {verbose}")
    return verbosity

@click.group(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.pass_context
def docker(ctx):
    """Docker management commands."""
    # Parse verbosity from args
    verbose = 0
    remaining_args = []
    i = 0
    while i < len(ctx.args):
        arg = ctx.args[i]
        if arg in ('-v', '--verbose'):
            if arg == '--verbose':
                verbose += 1
            else:
                # Count number of 'v's in -v, -vv, -vvv, etc.
                verbose += arg.count('v')
            # Remove the processed flag
            ctx.args.pop(i)
        else:
            i += 1
    
    # Initialize verbosity
    verbosity = Verbosity(verbosity=verbose)
    ctx.obj = {'verbosity': verbosity, 'args': ctx.args}

    verbosity.debug("Initializing Docker command group")
    if not check_docker(verbosity):
        click.echo("Error: Docker is not installed or not running. Please start Docker and try again.", err=True)
        ctx.exit(1)

@docker.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.option('--all', '-a', is_flag=True, help='Show all containers (default shows just running)')
@click.option('--format', type=click.Choice(['table', 'json'], case_sensitive=False),
              default='table', help='Output format')
@click.pass_context
def ps(ctx, all, format):
    """List containers."""
    verbosity = ctx.obj['verbosity']
    cmd = ['docker', 'ps']
    if all:
        cmd.append('-a')

    try:
        verbosity.debug(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            if format == 'json':
                # Try to parse and pretty-print JSON output
                try:
                    data = json.loads(result.stdout)
                    click.echo(json.dumps(data, indent=2))
                except json.JSONDecodeError:
                    # Fall back to raw output if not valid JSON
                    click.echo(result.stdout)
            else:
                # For table format, try to align columns
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    # Parse as JSON to handle special characters in values
                    try:
                        data = [json.loads(line) for line in lines[1:]]
                        headers = data[0].keys()
                        rows = [[item.get(header, '') for header in headers] for item in data]

                        # Calculate column widths
                        col_widths = [max(len(str(header)),
                                        max((len(str(row[i])) for row in rows), default=0))
                                    for i, header in enumerate(headers)]

                        # Print header
                        header_row = "  ".join(header.ljust(width) for header, width in zip(headers, col_widths))
                        click.echo(header_row)
                        click.echo("-" * len(header_row))

                        # Print rows
                        for row in rows:
                            click.echo("  ".join(str(cell).ljust(width) for cell, width in zip(row, col_widths)))
                    except Exception as e:
                        verbosity.debug(f"Error formatting table: {str(e)}")
                        # Fall back to raw output if processing fails
                        click.echo(result.stdout)
                else:
                    click.echo(result.stdout)
        else:
            error_msg = f"Error: {result.stderr}"
            verbosity.error(error_msg)
            click.echo(error_msg, err=True)
    except subprocess.CalledProcessError as e:
        error_msg = f"Command failed: {str(e)}"
        verbosity.error(error_msg)
        click.echo(error_msg, err=True)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        verbosity.error(error_msg)
        click.echo(error_msg, err=True)

@docker.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.argument('image', required=False)
@click.option('--name', help='Assign a name to the container')
@click.option('--port', '-p', multiple=True, help='Publish a container\'s port(s) to the host')
@click.option('--detach', '-d', is_flag=True, help='Run container in background and print container ID')
@click.option('--env', '-e', multiple=True, help='Set environment variables')
@click.option('--volume', '-v', multiple=True, help='Bind mount a volume')
@click.pass_context
def run(ctx, image, name, port, detach, env, volume):
    """Run a command in a new container."""
    verbosity = ctx.obj['verbosity']
    cmd = ['docker', 'run']

    if name:
        cmd.extend(['--name', name])
        verbosity.debug(f"Setting container name: {name}")

    for p in port:
        cmd.extend(['-p', p])
        verbosity.debug(f"Adding port mapping: {p}")

    if detach:
        cmd.append('-d')
        verbosity.debug("Running container in detached mode")

    for e in env:
        cmd.extend(['-e', e])
        verbosity.debug(f"Setting environment variable: {e}")

    for v in volume:
        cmd.extend(['-v', v])
        verbosity.debug(f"Mounting volume: {v}")

    if image:
        cmd.append(image)
        verbosity.debug(f"Using image: {image}")
    
    # Add any remaining arguments
    if hasattr(ctx, 'args') and ctx.args:
        cmd.extend(ctx.args)
        verbosity.debug(f"Additional arguments: {' '.join(ctx.args)}")

    try:
        verbosity.debug(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
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
        error_msg = f"Failed to run container: {str(e)}"
        verbosity.error(error_msg, exc_info=verbosity.verbosity >= 3)
        click.echo(error_msg, err=True)
        ctx.exit(1) 

@docker.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.argument('containers', nargs=-1, required=False)
@click.option('--force', '-f', is_flag=True, help='Force the removal of a running container (uses SIGKILL)')
@click.option('--volumes', '-v', is_flag=True, help='Remove anonymous volumes associated with the container')
@click.pass_context
def rm(ctx, containers, force, volumes):
    """Remove one or more containers."""
    verbosity = ctx.obj['verbosity']
    cmd = ['docker', 'rm']

    if force:
        cmd.append('-f')
        verbosity.debug("Force removal enabled")
    if volumes:
        cmd.append('-v')
        verbosity.debug("Volume removal enabled")

    # Get containers from both the containers argument and any remaining args
    all_containers = list(containers)
    if hasattr(ctx, 'args') and ctx.args:
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
        result = subprocess.run(cmd, capture_output=True, text=True)
        
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
        error_msg = f"Failed to remove containers: {str(e)}"
        verbosity.error(error_msg, exc_info=verbosity.verbosity >= 3)
        click.echo(error_msg, err=True)
        ctx.exit(1) 

@docker.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.option('--show-all', '-a', is_flag=True, help='Show all containers (default shows just running)')
@click.option('--http-only', is_flag=True, help='Show only containers with HTTP/HTTPS ports')
@click.pass_context
def url(ctx, show_all, http_only):
    """Show containers with their HTTP/HTTPS URLs."""
    verbosity = ctx.obj['verbosity']
    verbosity.info(f"Starting url command with show_all={show_all}, http_only={http_only}")

    try:
        # Get all containers
        cmd = ['docker', 'ps', '--format', '{{.ID}}|{{.Names}}|{{.Status}}|{{.Ports}}']
        if show_all:
            cmd.append('-a')

        verbosity.debug(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            error_msg = f"Error listing containers: {result.stderr}"
            verbosity.error(error_msg)
            click.echo(error_msg, err=True)
            return

        verbosity.debug(f"Command output: {result.stdout}")

        running_containers = []
        stopped_containers = []

        container_lines = result.stdout.strip().split('\n')
        verbosity.info(f"Found {len(container_lines)} container(s)")

        for line in container_lines:
            if not line.strip():
                verbosity.debug("Skipping empty line")
                continue

            try:
                verbosity.debug(f"Processing container line: {line}")
                container_id, name, status, ports = line.split('|', 3)
                is_running = 'Up' in status
                verbosity.info(f"Container: ID={container_id[:12]}, Name={name}, Status={status}, Running={is_running}")

                # Get container details
                container_info = {
                    'id': container_id[:12],  # Short ID
                    'name': name,
                    'status': status,
                    'urls': []
                }

                # Get exposed ports and their mappings
                port_mappings = get_container_ports(container_id, verbosity)
                verbosity.debug(f"Found {len(port_mappings)} port mappings for {name}")

                for port in port_mappings:
                    if port['host_port'] and port['container_port']:
                        verbosity.debug(f"Checking port mapping: {port}")

                        # Check if it's HTTP/HTTPS port (common ports)
                        http_ports = ['80', '443', '8080', '8443', '3000', '5000', '8000', '8888']
                        is_http_port = (
                            port['container_port'] in http_ports or
                            any(p in port['container_port'] for p in ['80/', '443/', '8080/', '8443/'])
                        )

                        if is_http_port:
                            scheme = 'https' if port['container_port'].startswith('443') else 'http'
                            url = f"{scheme}://{port['host_ip']}:{port['host_port']}"
                            port_num = port['container_port'].split('/')[0]

                            container_info['urls'].append({
                                'url': url,
                                'port': port_num
                            })
                            verbosity.info(f"Added URL for {name}: {url} (port {port_num})")
                        else:
                            verbosity.debug(f"Skipping non-HTTP port: {port['container_port']}")

                # If http_only is True and no HTTP URLs, skip this container
                if http_only and not container_info['urls']:
                    continue

                if is_running:
                    running_containers.append(container_info)
                else:
                    stopped_containers.append(container_info)

            except Exception as e:
                click.echo(f"Error processing container info: {e}", err=True)
                continue

        # Display running containers
        if running_containers:
            click.secho("\n🚀 Running Containers:", fg='green', bold=True)
            for container in running_containers:
                verbosity.debug(f"Displaying running container: {container['name']}")
                click.echo(f"\n{click.style('●', fg='green')} {click.style(container['name'], bold=True)} ({container['id']})")

                if container['urls']:
                    verbosity.info(f"Found {len(container['urls'])} URLs for {container['name']}")
                    for url_info in container['urls']:
                        verbosity.debug(f"Displaying URL: {url_info['url']}")
                        click.echo(f"   {click.style('→', fg='blue')} {click.style(url_info['url'], fg='blue', underline=True)}")
                else:
                    verbosity.debug(f"No URLs found for {container['name']}")

        # Display stopped containers
        if stopped_containers and (show_all or not http_only):
            click.secho("\n⏸️  Stopped Containers:", fg='yellow', bold=True)
            for container in stopped_containers:
                verbosity.debug(f"Displaying stopped container: {container['name']}")
                click.echo(f"\n{click.style('●', fg='yellow')} {click.style(container['name'], dim=True)} ({container['id']})")

                if container['urls']:
                    verbosity.info(f"Found {len(container['urls'])} URLs for stopped container {container['name']}")
                    for url_info in container['urls']:
                        verbosity.debug(f"Displaying URL for stopped container: {url_info['url']}")
                        click.echo(f"   {click.style('→', fg='blue')} {click.style(url_info['url'], fg='blue', underline=True, dim=True)}")
                else:
                    verbosity.debug(f"No URLs found for stopped container {container['name']}")

        if not running_containers and not stopped_containers:
            msg = "No containers found."
            verbosity.info(msg)
            click.echo(msg)
        else:
            verbosity.info(f"Displayed {len(running_containers)} running and {len(stopped_containers)} stopped containers")

    except Exception as e:
        error_msg = f"Error in url command: {str(e)}"
        verbosity.error(error_msg, exc_info=verbosity.verbosity >= 3)
        click.echo(error_msg, err=True)

@docker.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.argument('image', required=False)
@click.option('--all-tags', '-a', is_flag=True, help='Remove all versions of the image with the given name')
@click.option('--force', '-f', is_flag=True, help='Force removal of the image')
@click.option('--no-prune', is_flag=True, help='Do not delete untagged parents')
@click.pass_context
def rmi(ctx, image, all_tags, force, no_prune):
    """Remove one or more images."""
    verbosity = ctx.obj['verbosity']
    cmd = ['docker', 'rmi']

    if force:
        cmd.append('-f')
        verbosity.debug("Force removal enabled")
    if no_prune:
        cmd.append('--no-prune')
        verbosity.debug("Pruning of untagged parents disabled")

    # Get images from both the image argument and any remaining args
    images = []
    if image:
        images.append(image)
    if hasattr(ctx, 'args') and ctx.args:
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
                    ['docker', 'images', '--format', '{{.Repository}}:{{.Tag}}', img],
                    capture_output=True, 
                    text=True
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    tags = [line for line in result.stdout.split('\n') if line]
                    verbosity.debug(f"Found {len(tags)} tags for {img}")
                    all_tags_to_remove.extend(tags)
                else:
                    verbosity.warning(f"No images found matching '{img}'")
                    
            except Exception as e:
                verbosity.error(f"Error finding tags for {img}: {str(e)}", exc_info=verbosity.verbosity >= 3)
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
        result = subprocess.run(cmd, capture_output=True, text=True)
        
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
        error_msg = f"Failed to remove images: {str(e)}"
        verbosity.error(error_msg, exc_info=verbosity.verbosity >= 3)
        click.echo(error_msg, err=True)
        ctx.exit(1) 

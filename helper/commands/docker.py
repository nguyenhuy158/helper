import click
import subprocess
import json
import re
from typing import Dict, List, Tuple

def get_container_ports(container_id: str) -> List[Dict]:
    """Get exposed ports and IPs for a container."""
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
            return []
            
        ports = []
        if result.stdout.strip():
            for mapping in result.stdout.strip().split(';'):
                if not mapping:
                    continue
                try:
                    container_port, host_ip, host_port = mapping.split('|')
                    if container_port and host_port:
                        ports.append({
                            'container_port': container_port.split('/')[0],  # Remove /tcp or /udp
                            'host_ip': host_ip if host_ip not in ('0.0.0.0', '') else 'localhost',
                            'host_port': host_port
                        })
                except ValueError:
                    continue
        return ports
    except Exception:
        return []

def check_docker():
    """Check if Docker is installed and running."""
    try:
        result = subprocess.run(['docker', 'info'], 
                              capture_output=True, 
                              text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except Exception as e:
        click.echo(f"Error checking Docker: {e}", err=True)
        return False

def format_output(output, output_format='table'):
    """Format command output based on the specified format."""
    if output_format == 'json':
        try:
            return json.dumps(json.loads(output), indent=2)
        except json.JSONDecodeError:
            return output
    return output

@click.group()
@click.pass_context
def docker(ctx):
    """Docker management commands."""
    if not check_docker():
        click.echo("Error: Docker is not installed or not running. Please start Docker and try again.", err=True)
        ctx.exit(1)

@docker.command()
@click.option('--all', '-a', is_flag=True, help='Show all containers (default shows just running)')
@click.option('--format', type=click.Choice(['table', 'json'], case_sensitive=False), 
              default='table', help='Output format')
def ps(all, format):
    """List containers."""
    cmd = ['docker', 'ps', '--format', '{{json .}}']
    if all:
        cmd.append('-a')
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            # Process each line as a separate JSON object
            lines = [line for line in result.stdout.splitlines() if line.strip()]
            if format == 'json':
                click.echo(json.dumps([json.loads(line) for line in lines], indent=2))
            else:
                # Simple table output
                if lines:
                    data = [json.loads(line) for line in lines]
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
        else:
            click.echo(f"Error: {result.stderr}", err=True)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

@docker.command()
@click.argument('image')
@click.option('--name', help='Assign a name to the container')
@click.option('--port', '-p', multiple=True, help='Publish a container\'s port(s) to the host')
@click.option('--detach', '-d', is_flag=True, help='Run container in background and print container ID')
@click.option('--env', '-e', multiple=True, help='Set environment variables')
@click.option('--volume', '-v', multiple=True, help='Bind mount a volume')
def run(image, name, port, detach, env, volume):
    """Run a command in a new container."""
    cmd = ['docker', 'run']
    
    if name:
        cmd.extend(['--name', name])
    
    for p in port:
        cmd.extend(['-p', p])
    
    if detach:
        cmd.append('-d')
    
    for e in env:
        cmd.extend(['-e', e])
    
    for v in volume:
        cmd.extend(['-v', v])
    
    cmd.append(image)
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running container: {e}", err=True)
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)

@docker.command()
@click.argument('containers', nargs=-1, required=True)
@click.option('--force', '-f', is_flag=True, help='Force the removal of running containers')
@click.option('--volumes', '-v', is_flag=True, help='Remove the volumes associated with the container')
def rm(containers, force, volumes):
    """Remove one or more containers."""
    cmd = ['docker', 'rm']
    
    if force:
        cmd.append('-f')
    if volumes:
        cmd.append('-v')
    
    cmd.extend(containers)
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error removing containers: {e}", err=True)
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)

@docker.command()
@click.option('--show-all', '-a', is_flag=True, help='Show all containers (default shows just running)')
@click.option('--http-only', is_flag=True, help='Show only containers with HTTP/HTTPS ports')
def url(show_all, http_only):
    """Show containers with their HTTP/HTTPS URLs."""
    try:
        # Get all containers
        cmd = ['docker', 'ps', '--format', '{{.ID}}|{{.Names}}|{{.Status}}|{{.Ports}}']
        if show_all:
            cmd.append('-a')
            
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            click.echo(f"Error listing containers: {result.stderr}", err=True)
            return
            
        running_containers = []
        stopped_containers = []
        
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
                
            try:
                container_id, name, status, ports = line.split('|', 3)
                is_running = 'Up' in status
                
                # Get container details
                container_info = {
                    'id': container_id[:12],  # Short ID
                    'name': name,
                    'status': status,
                    'urls': []
                }
                
                # Get exposed ports and their mappings
                port_mappings = get_container_ports(container_id)
                for port in port_mappings:
                    if port['host_port'] and port['container_port']:
                        # Check if it's HTTP/HTTPS port (common ports)
                        if (port['container_port'] in ['80', '443', '8080', '8443', '3000', '5000', '8000', '8888'] or
                            any(p in port['container_port'] for p in ['80/', '443/', '8080/', '8443/'])):
                            scheme = 'https' if port['container_port'].startswith('443') else 'http'
                            container_info['urls'].append({
                                'url': f"{scheme}://{port['host_ip']}:{port['host_port']}",
                                'port': port['container_port'].split('/')[0]
                            })
                
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
                click.echo(f"\n{click.style('●', fg='green')} {click.style(container['name'], bold=True)} ({container['id']})")
                if container['urls']:
                    for url_info in container['urls']:
                        click.echo(f"   {click.style('→', fg='blue')} {click.style(url_info['url'], fg='blue', underline=True)}")
        
        # Display stopped containers
        if stopped_containers and (show_all or not http_only):
            click.secho("\n⏸️  Stopped Containers:", fg='yellow', bold=True)
            for container in stopped_containers:
                click.echo(f"\n{click.style('●', fg='yellow')} {click.style(container['name'], dim=True)} ({container['id']})")
                if container['urls']:
                    for url_info in container['urls']:
                        click.echo(f"   {click.style('→', fg='blue')} {click.style(url_info['url'], fg='blue', underline=True, dim=True)}")
        
        if not running_containers and not stopped_containers:
            click.echo("No containers found.")
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

@docker.command()
@click.argument('image')
@click.option('--all-tags', '-a', is_flag=True, help='Remove all versions of the image with the given name')
@click.option('--force', '-f', is_flag=True, help='Force removal of the image')
@click.option('--no-prune', is_flag=True, help='Do not delete untagged parents')
def rmi(image, all_tags, force, no_prune):
    """Remove one or more images."""
    cmd = ['docker', 'rmi']
    
    if force:
        cmd.append('-f')
    if no_prune:
        cmd.append('--no-prune')
    
    if all_tags:
        # Get all tags for the image
        try:
            result = subprocess.run(['docker', 'images', '--format', '{{.Repository}}:{{.Tag}}', image],
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                tags = result.stdout.strip().split('\n')
                cmd.extend(tags)
            else:
                click.echo(f"No images found matching '{image}'", err=True)
                return
        except Exception as e:
            click.echo(f"Error finding images: {str(e)}", err=True)
            return
    else:
        cmd.append(image)
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error removing images: {e}", err=True)
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)

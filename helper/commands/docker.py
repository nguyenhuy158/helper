import click
import subprocess
import json

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

import click
import platform
import subprocess

def check_nixos():
    """Check if running on NixOS."""
    try:
        with open('/etc/os-release') as f:
            return 'NixOS' in f.read()
    except FileNotFoundError:
        return False
    except Exception as e:
        click.echo(f"Warning: Could not check if running on NixOS: {e}", err=True)
        return False

def get_nixos_version():
    """Get NixOS version information."""
    if not check_nixos():
        return "Not running NixOS"
    
    try:
        result = subprocess.run(['nixos-version'], 
                              capture_output=True, 
                              text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        return "NixOS version could not be determined"
    except Exception as e:
        return f"Error getting NixOS version: {str(e)}"

@click.group()
def nixos():
    """NixOS related commands."""
    if not check_nixos():
        click.echo("Warning: Not running on NixOS. Some commands may not work as expected.", err=True)

@nixos.command()
def version():
    """Show NixOS version."""
    click.echo(get_nixos_version())

@nixos.command()
@click.argument('package', required=False)
def search(package):
    """Search for Nix packages."""
    if not package:
        click.echo("Please specify a package to search for")
        return
        
    try:
        result = subprocess.run(['nix-env', '-qa', package],
                              capture_output=True,
                              text=True)
        if result.returncode == 0:
            click.echo(result.stdout)
        else:
            click.echo(f"Error searching for package: {result.stderr}", err=True)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

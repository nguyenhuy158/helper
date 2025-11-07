import click
import platform
import subprocess
import socket
import shutil

def run_cmd(cmd):
    print(f"$ {cmd}")
    try:
        result = subprocess.check_output(cmd, shell=True, text=True).strip()
        print(result)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

@click.group()
def cli():
    """Helper CLI - quick system info"""
    pass

@cli.command()
def internal_ip():
    """Show local/internal IP"""
    system = platform.system()
    if system == "Darwin":
        cmd = "ipconfig getifaddr en0"
    elif system == "Linux":
        # Prefer ifconfig if available, else hostname -I
        if shutil.which("ifconfig"):
            cmd = "ifconfig | grep 'inet ' | grep -v 192.168.1.1 | awk '{print $2}' | head -n1"
        else:
            cmd = "hostname -I | awk '{print $1}'"
    else:
        ip = socket.gethostbyname(socket.gethostname())
        print(f"$ python socket.gethostbyname(socket.gethostname())")
        print(ip)
        return
    run_cmd(cmd)

@cli.command()
def public_ip():
    """Show public IP"""
    cmd = "curl -s ifconfig.me"
    run_cmd(cmd)

@cli.command()
def arch():
    """Show CPU architecture"""
    cmd = "uname -m"
    run_cmd(cmd)

@cli.command()
@click.pass_context
def all(ctx):
    """Show all info"""
    click.echo("=== Internal IP ===")
    ctx.invoke(internal_ip)
    click.echo("\n=== Public IP ===")
    ctx.invoke(public_ip)
    click.echo("\n=== Architecture ===")
    ctx.invoke(arch)

if __name__ == "__main__":
    cli()

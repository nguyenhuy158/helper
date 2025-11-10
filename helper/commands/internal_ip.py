import platform
import socket
import shutil
import click
from helper import __version__
from helper.utils import run_cmd

def get_internal_ip():
    """Get the internal IP address based on the operating system."""
    system = platform.system()
    if system == "Darwin":
        cmd = "ipconfig getifaddr en0"
    elif system == "Linux":
        if shutil.which("ifconfig"):
            cmd = "ifconfig | grep 'inet ' | grep -v 192.168.1.1 | awk '{print $2}' | head -n1"
        else:
            cmd = "hostname -I | awk '{print $1}'"
    else:
        ip = socket.gethostbyname(socket.gethostname())
        print(f"$ python socket.gethostbyname(socket.gethostname())")
        print(ip)
        return
    return run_cmd(cmd)

@click.command()
def internal_ip():
    """Display the local/internal IP address.
    
    This command shows the internal (LAN) IP address of your machine.
    It automatically detects the correct network interface based on your OS.
    
    Examples:
        $ h ip
        192.168.1.100
        
    Note: On multi-homed systems, this shows the primary network interface's IP.
    """
    ip = get_internal_ip()
    if ip:
        click.echo(ip)

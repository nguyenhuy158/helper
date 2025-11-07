import platform
import socket
import shutil
from ..utils import run_cmd
import click

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
    """Show local/internal IP"""
    get_internal_ip()

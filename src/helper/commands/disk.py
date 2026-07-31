"""Disk information command."""

import platform
import subprocess

import click
from rich.console import Console
from rich.panel import Panel

from ..utils import format_bytes

console = Console()


def run_command(cmd):
    """Run a shell command and return its output"""
    try:
        result = subprocess.check_output(
            cmd, shell=True, text=True, stderr=subprocess.STDOUT
        ).strip()
        return result if result else "N/A"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output}" if e.output else "Command failed"


def parse_windows_disk_info(disks_output):
    """Parse Windows disk information from wmic output."""
    lines = disks_output.split("\n")
    result = [
        f"{'Drive':<5} {'Total Space':<15} {'Free Space':<15} {'Used Space':<15} {'% Used':<10}"
    ]
    for line in lines[1:]:
        parts = line.strip().split()
        if len(parts) >= 3:
            drive = parts[0]
            try:
                size = int(parts[1])
                free = int(parts[2])
                used = size - free
                pct_used = (used / size) * 100 if size > 0 else 0
                result.append(
                    f"{drive:<5} {format_bytes(size):<15} {format_bytes(free):<15} "
                    f"{format_bytes(used):<15} {pct_used:.1f}%"
                )
            except (ValueError, IndexError):
                continue
    return result


@click.group(name="disk")
@click.pass_context
def disk_cmd(ctx):
    """Disk management commands."""


@disk_cmd.command(name="usage")
def disk_usage():
    """Display disk usage information."""
    output = get_usage()
    console.print(Panel(output, title="Disk Usage", border_style="cyan"))


@disk_cmd.command(name="mount")
def disk_mount():
    """Display mounted filesystems."""
    output = get_mount()
    console.print(Panel(output, title="Mounted Filesystems", border_style="green"))


@disk_cmd.command(name="list")
def disk_list():
    """List disks and their capacities."""
    output = get_list()
    console.print(Panel(output, title="Disk List", border_style="blue"))


def get_usage():
    """Get disk usage information as string."""
    system = platform.system().lower()

    if system in ["linux", "darwin"]:
        output = run_command("df -h")
        return output
    elif system == "windows":
        disks = run_command("wmic logicaldisk get size,freespace,caption")
        if "Caption" in disks:
            result = parse_windows_disk_info(disks)
            return "\n".join(result)
        else:
            return disks
    else:
        return "Unsupported operating system"


def get_mount():
    """Get mounted filesystems information as string."""
    system = platform.system().lower()

    if system in ["linux", "darwin"]:
        output = run_command("mount")
        return output
    elif system == "windows":
        output = run_command("mountvol")
        return output
    return "Unsupported operating system"


def get_list():
    """Get list of disks and their capacities as string."""
    system = platform.system().lower()

    if system in ["linux", "darwin"]:
        output = run_command("df -h")
        lines = output.split("\n")
        if lines:
            count = len(lines) - 1  # minus header
            return f"Number of mounted filesystems: {count}\nDisk capacities:\n{output}"
        return output
    elif system == "windows":
        disks = run_command("wmic logicaldisk get size,freespace,caption")
        if "Caption" in disks:
            lines = disks.split("\n")
            disk_list = [line for line in lines[1:] if line.strip()]
            count = len(disk_list)
            result = parse_windows_disk_info(disks)
            return f"Number of logical disks: {count}\nDisk capacities:\n" + "\n".join(result)
        return disks
    return "Unsupported operating system"


def disk():
    """Disk command group."""
    return disk_cmd

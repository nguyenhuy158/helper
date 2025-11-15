import click
import platform
import subprocess


def run_command(cmd):
    """Run a shell command and return its output"""
    try:
        result = subprocess.check_output(
            cmd, shell=True, text=True, stderr=subprocess.STDOUT
        ).strip()
        return result if result else "N/A"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output}" if e.output else "Command failed"


def format_bytes(size_bytes):
    """Convert bytes to human readable format"""
    if not isinstance(size_bytes, (int, float)):
        try:
            size_bytes = float(size_bytes)
        except (ValueError, TypeError):
            return str(size_bytes)

    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if size_bytes < 1024.0 or unit == "PB":
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def parse_windows_disk_info(disks_output):
    """Parse Windows disk information from wmic output."""
    lines = disks_output.split("\n")
    result = [
        "{:<5} {:<15} {:<15} {:<15} {:<10}".format(
            "Drive", "Total Space", "Free Space", "Used Space", "% Used"
        )
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
                    "{:<5} {:<15} {:<15} {:<15} {:.1f}%".format(
                        drive,
                        format_bytes(size),
                        format_bytes(free),
                        format_bytes(used),
                        pct_used,
                    )
                )
            except (ValueError, IndexError):
                continue
    return result


@click.group(name="disk")
@click.pass_context
def disk_cmd(ctx):
    """Disk management commands."""
    pass


@disk_cmd.command(name="usage")
def disk_usage():
    """Display disk usage information."""
    output = get_usage()
    click.echo(output)


@disk_cmd.command(name="mount")
def disk_mount():
    """Display mounted filesystems."""
    output = get_mount()
    click.echo(output)


@disk_cmd.command(name="list")
def disk_list():
    """List disks and their capacities."""
    output = get_list()
    click.echo(output)


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
    else:
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
        else:
            return output
    elif system == "windows":
        disks = run_command("wmic logicaldisk get size,freespace,caption")
        if "Caption" in disks:
            lines = disks.split("\n")
            disk_list = [line for line in lines[1:] if line.strip()]
            count = len(disk_list)
            result = parse_windows_disk_info(disks)
            return f"Number of logical disks: {count}\nDisk capacities:\n" + "\n".join(result)
        else:
            return disks
    else:
        return "Unsupported operating system"


def disk():
    return disk_cmd
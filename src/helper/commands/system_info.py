"""System information commands."""

import platform
import subprocess

import click

from ..utils import format_bytes


def run_command(cmd):
    """Run a shell command and return its output"""
    try:
        result = subprocess.check_output(
            cmd, shell=True, text=True, stderr=subprocess.STDOUT
        ).strip()
        return result if result else "N/A"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output}" if e.output else "Command failed"


def parse_vm_stat(output):
    """Parse macOS vm_stat output and return human readable memory info"""
    if not output or "Mach Virtual Memory Statistics" not in output:
        return "Memory information not available"

    # Get physical memory using sysctl
    try:
        total_memory = int(run_command("sysctl -n hw.memsize"))
    except (ValueError, subprocess.CalledProcessError):
        return "Error: Could not determine total physical memory"

    lines = output.split("\n")
    mem_info = {}

    for line in lines[1:]:  # Skip header
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip().strip(".")
            try:
                # Convert pages to bytes (1 page = 4KB on macOS)
                pages = int(value.strip().strip("."))
                mem_info[key] = pages * 4096  # 4KB per page
            except (ValueError, AttributeError):
                mem_info[key] = value.strip()

    # Calculate memory usage
    wired_memory = mem_info.get("Pages wired down", 0)
    active_memory = mem_info.get("Pages active", 0)
    inactive_memory = mem_info.get("Pages inactive", 0)
    free_memory = mem_info.get("Pages free", 0)

    # Calculate used memory (wired + active)
    used_memory = wired_memory + active_memory

    # Calculate app memory (active + inactive)
    app_memory = active_memory + inactive_memory

    # Calculate cached files (inactive memory can be purged by the OS)
    cached_files = inactive_memory

    return (
        f"Total: {format_bytes(total_memory)}\n"
        f"Used:  {format_bytes(used_memory)} "
        f"(Apps: {format_bytes(app_memory)}, Wired: {format_bytes(wired_memory)})\n"
        f"Free:  {format_bytes(free_memory)}\n"
        f"Cached: {format_bytes(cached_files)}\n"
        f"Usage: {used_memory/total_memory*100:.1f}%"
    )


def parse_df_output(output):
    """Parse df output and format sizes"""
    if not output:
        return "Disk information not available"

    lines = output.split("\n")
    if not lines:
        return output

    # Keep the header
    result = [lines[0]]

    # Process each line
    for line in lines[1:]:
        if not line.strip():
            continue

        parts = line.split()
        if len(parts) >= 5:
            # Format size columns (assuming standard df -h output)
            parts[1] = format_bytes(
                parts[1]
                .upper()
                .replace("G", "GB")
                .replace("M", "MB")
                .replace("K", "KB")
                .replace("B", "")
                .replace("I", "")
                .strip()
            )
            parts[2] = format_bytes(
                parts[2]
                .upper()
                .replace("G", "GB")
                .replace("M", "MB")
                .replace("K", "KB")
                .replace("B", "")
                .replace("I", "")
                .strip()
            )
            parts[3] = format_bytes(
                parts[3]
                .upper()
                .replace("G", "GB")
                .replace("M", "MB")
                .replace("K", "KB")
                .replace("B", "")
                .replace("I", "")
                .strip()
            )

            # Reconstruct the line with formatted sizes
            result.append(" ".join(parts))
        else:
            result.append(line)

    return "\n".join(result)


def get_os_specific_info():
    """Get OS-specific system information"""
    system = platform.system().lower()

    if system == "darwin":  # macOS
        return {
            "cpu": "sysctl -n machdep.cpu.brand_string",
            "cpu_cores": "sysctl -n hw.ncpu",
            "memory": "vm_stat",
            "disks": "df -h",
            "os_version": "sw_vers",
            "hostname": "hostname",
            "uptime": "uptime",
        }
    elif system == "linux":
        return {
            "cpu": 'cat /proc/cpuinfo | grep "model name" | head -n 1 | cut -d":" -f2',
            "cpu_cores": "nproc",
            "memory": "free -h",
            "disks": "df -h",
            "os_version": "cat /etc/os-release",
            "hostname": "hostname",
            "uptime": "uptime",
        }
    elif system == "windows":
        return {
            "cpu": "wmic cpu get name",
            "cpu_cores": "wmic cpu get NumberOfCores",
            "memory": "wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /Value",
            "disks": "wmic logicaldisk get size,freespace,caption",
            "os_version": 'systeminfo | findstr /B /C:"OS Name" /C:"OS Version"',
            "hostname": "hostname",
            "uptime": "wmic os get lastbootuptime",
        }
    else:
        return None


def format_uptime(uptime_str, system):
    """Format uptime string based on OS"""
    if system == "darwin" or system == "linux":
        # Example: ' 8:53  up 1 day,  3:45, 2 users, load averages: 2.22 2.41 2.35'
        parts = uptime_str.split(",")
        if "up" in parts[0]:
            return "Uptime: " + parts[0].split("up", 1)[1].strip()
    return uptime_str


def get_info():
    """Get system information as a dictionary."""
    system = platform.system().lower()
    commands = get_os_specific_info()

    if not commands:
        return None

    info = {}

    # System Information
    info["system"] = {
        "system": platform.system(),
        "release": platform.release(),
        "node": run_command(commands["hostname"]),
        "machine": platform.machine(),
        "processor": platform.processor() or run_command(commands["cpu"]).strip(),
    }

    # OS Version
    info["os_version"] = run_command(commands["os_version"])

    # Uptime
    uptime_str = run_command(commands["uptime"])
    info["uptime"] = format_uptime(uptime_str, system)

    # CPU
    info["cpu"] = {
        "cores": run_command(commands["cpu_cores"]).strip(),
    }

    if system == "darwin" or system == "linux":
        info["cpu"]["cpu"] = run_command(commands["cpu"]).strip()

        if system == "darwin":
            info["cpu"]["load_avg"] = run_command("sysctl -n vm.loadavg").strip()
    if system == "linux":
        info["cpu"]["load_avg"] = run_command("cat /proc/loadavg").strip()

    # Memory
    if system == "darwin":
        mem_info = run_command("vm_stat")
        info["memory"] = parse_vm_stat(mem_info)
    elif system == "linux":
        mem_info = run_command("free -b")  # Get bytes for consistent formatting
        lines = mem_info.split("\n")
        if len(lines) > 1:
            values = lines[1].split()
            if len(values) >= 7:  # For Mem: line
                total = int(values[1])
                used = int(values[2])
                free = int(values[3])
                info["memory"] = {
                    "total": format_bytes(total),
                    "used": format_bytes(used),
                    "free": format_bytes(free),
                    "usage": f"{used/total*100:.1f}%" if total > 0 else "0%",
                }
    elif system == "windows":
        mem_info = run_command("wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /Value")
        if "TotalVisibleMemorySize" in mem_info and "FreePhysicalMemory" in mem_info:
            total = (
                int(mem_info.split("TotalVisibleMemorySize=")[1].split("\n")[0]) * 1024
            )  # KB to bytes
            free = (
                int(mem_info.split("FreePhysicalMemory=")[1].split("\n")[0]) * 1024
            )  # KB to bytes
            used = total - free
            info["memory"] = {
                "total": format_bytes(total),
                "used": format_bytes(used),
                "free": format_bytes(free),
                "usage": f"{used/total*100:.1f}%" if total > 0 else "0%",
            }
        else:
            info["memory"] = mem_info

    # Disk
    if system == "windows":
        disks = run_command("wmic logicaldisk get size,freespace,caption")
        if "Caption" in disks:
            lines = disks.split("\n")
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
                            f"{drive:<5} {format_bytes(size):<15} {format_bytes(free):<15} "
                            f"{format_bytes(used):<15} {pct_used:.1f}%"
                        )
                    except (ValueError, IndexError):
                        continue
            info["disks"] = "\n".join(result)
        else:
            info["disks"] = disks
    else:
        disks = run_command(
            "df -h" if system != "windows" else "wmic logicaldisk get size,freespace,caption"
        )
        info["disks"] = parse_df_output(disks)

    return info


@click.command()
def system_info():
    """Display system information including CPU, RAM, and disk usage"""
    info = get_info()

    if not info:
        click.echo("Unsupported operating system")
        return

    # System Information
    click.echo("=" * 40 + " System Information " + "=" * 40)
    click.echo(f"System: {info['system']['system']} {info['system']['release']}")
    click.echo(f"Node Name: {info['system']['node']}")
    click.echo(f"Machine: {info['system']['machine']}")
    click.echo(f"Processor: {info['system']['processor']}")

    # OS Version
    click.echo("\n" + "=" * 40 + " OS Version " + "=" * 40)
    click.echo(info["os_version"])

    # Uptime
    click.echo("\n" + "=" * 40 + " Uptime " + "=" * 40)
    click.echo(info["uptime"])

    # CPU Information
    click.echo("\n" + "=" * 40 + " CPU Info " + "=" * 40)
    click.echo(f"CPU Cores: {info['cpu']['cores']}")

    if "cpu" in info["cpu"]:
        click.echo(f"CPU: {info['cpu']['cpu']}")

    if "load_avg" in info["cpu"]:
        click.echo(f"Load Average: {info['cpu']['load_avg']}")

    # Memory Information
    click.echo("\n" + "=" * 40 + " Memory Information " + "=" * 40)
    if isinstance(info["memory"], dict):
        click.echo(
            f"Total: {info['memory']['total']}\n"
            f"Used:  {info['memory']['used']}\n"
            f"Free:  {info['memory']['free']}\n"
            f"Usage: {info['memory']['usage']}"
        )
    else:
        click.echo(info["memory"])

    # Disk Information
    click.echo("\n" + "=" * 40 + " Disk Information " + "=" * 40)
    click.echo(info["disks"])


# Add aliases for the command
sysinfo = system_info
si = system_info

import click
import platform
import subprocess
import sys
from datetime import datetime

def run_command(cmd):
    """Run a shell command and return its output"""
    try:
        result = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT).strip()
        return result if result else "N/A"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output}" if e.output else "Command failed"

def get_size_kb(size_kb):
    """Convert KB to human readable format"""
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if size_kb < 1024.0:
            return f"{size_kb:.1f}{unit}B"
        size_kb /= 1024.0
    return f"{size_kb:.1f}PB"

def get_os_specific_info():
    """Get OS-specific system information"""
    system = platform.system().lower()
    
    if system == 'darwin':  # macOS
        return {
            'cpu': 'sysctl -n machdep.cpu.brand_string',
            'cpu_cores': 'sysctl -n hw.ncpu',
            'memory': 'vm_stat',
            'disks': 'df -h',
            'os_version': 'sw_vers',
            'hostname': 'hostname',
            'uptime': 'uptime'
        }
    elif system == 'linux':
        return {
            'cpu': 'cat /proc/cpuinfo | grep "model name" | head -n 1 | cut -d":" -f2',
            'cpu_cores': 'nproc',
            'memory': 'free -h',
            'disks': 'df -h',
            'os_version': 'cat /etc/os-release',
            'hostname': 'hostname',
            'uptime': 'uptime'
        }
    elif system == 'windows':
        return {
            'cpu': 'wmic cpu get name',
            'cpu_cores': 'wmic cpu get NumberOfCores',
            'memory': 'wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /Value',
            'disks': 'wmic logicaldisk get size,freespace,caption',
            'os_version': 'systeminfo | findstr /B /C:"OS Name" /C:"OS Version"',
            'hostname': 'hostname',
            'uptime': 'wmic os get lastbootuptime'
        }
    else:
        return None

def format_uptime(uptime_str, system):
    """Format uptime string based on OS"""
    if system == 'darwin' or system == 'linux':
        # Example: ' 8:53  up 1 day,  3:45, 2 users, load averages: 2.22 2.41 2.35'
        parts = uptime_str.split(',')
        if 'up' in parts[0]:
            return 'Uptime: ' + parts[0].split('up', 1)[1].strip()
    return uptime_str

@click.command()
def system_info():
    """Display system information including CPU, RAM, and disk usage"""
    system = platform.system().lower()
    commands = get_os_specific_info()
    
    if not commands:
        click.echo("Unsupported operating system")
        return
    
    # System Information
    click.echo("="*40 + " System Information " + "="*40)
    click.echo(f"System: {platform.system()} {platform.release()}")
    click.echo(f"Node Name: {run_command(commands['hostname'])}")
    click.echo(f"Machine: {platform.machine()}")
    click.echo(f"Processor: {platform.processor() or run_command(commands['cpu']).strip()}")
    
    # OS Version
    click.echo("\n" + "="*40 + " OS Version " + "="*40)
    click.echo(run_command(commands['os_version']))
    
    # Uptime
    click.echo("\n" + "="*40 + " Uptime " + "="*40)
    uptime = run_command(commands['uptime'])
    click.echo(format_uptime(uptime, system))
    
    # CPU Information
    click.echo("\n" + "="*40 + " CPU Info " + "="*40)
    cpu_cores = run_command(commands['cpu_cores']).strip()
    click.echo(f"CPU Cores: {cpu_cores}")
    
    if system == 'darwin' or system == 'linux':
        cpu_info = run_command(commands['cpu']).strip()
        click.echo(f"CPU: {cpu_info}")
        
        # CPU Usage (simplified for cross-platform)
        if system == 'darwin':
            load_avg = run_command('sysctl -n vm.loadavg').strip()
            click.echo(f"Load Average: {load_avg}")
        elif system == 'linux':
            load_avg = run_command('cat /proc/loadavg').strip()
            click.echo(f"Load Average: {load_avg}")
    
    # Memory Information
    click.echo("\n" + "="*40 + " Memory Information " + "="*40)
    if system == 'darwin':
        mem_info = run_command('vm_stat')
        click.echo(mem_info)
    elif system == 'linux':
        mem_info = run_command('free -h')
        click.echo(mem_info)
    elif system == 'windows':
        mem_info = run_command('wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /Value')
        click.echo(mem_info)
    
    # Disk Information
    click.echo("\n" + "="*40 + " Disk Information " + "="*40)
    disks = run_command(commands['disks'])
    click.echo(disks)

# Add aliases for the command
sysinfo = system_info
si = system_info

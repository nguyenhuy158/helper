"""Kill processes by name or port."""

import subprocess

import click
import psutil

from ..rich_help import RichHelpCommand


@click.command(cls=RichHelpCommand)
@click.argument("target", required=False)
@click.pass_context
def kill(ctx, target):
    """Kill processes by name or port.

    TARGET can be a process name (e.g., 'python') or a port number (e.g., 8000).
    For names, kills all matching processes. For ports, kills the process listening on that port.

    Examples:
        $ helper kill python
        $ helper kill 8000
    """
    if not target:
        click.echo(ctx.get_help())
        return
    try:
        # Try to parse as port number
        port = int(target)
        # Find process by port using lsof
        try:
            result = subprocess.run(
                ["lsof", "-i", f":{port}", "-t"], capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                pids = result.stdout.strip().split("\n")
                for pid_str in pids:
                    if pid_str:
                        pid = int(pid_str)
                        try:
                            proc = psutil.Process(pid)
                            proc.kill()
                            click.echo(
                                f"Successfully terminated process {proc.name()} "
                                f"(PID: {pid}) listening on port {port}."
                            )
                        except psutil.AccessDenied:
                            click.echo(f"Access denied: cannot kill process {pid} on port {port}.")
            else:
                click.echo(f"No process found listening on port {port}.")
        except FileNotFoundError:
            click.echo("lsof command not found. Please install lsof to kill by port.")
    except ValueError:
        # Treat as process name
        killed = []
        for proc in psutil.process_iter(["pid", "name"]):
            if target.lower() in proc.info["name"].lower():
                try:
                    proc.kill()
                    killed.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
                except psutil.AccessDenied:
                    click.echo(
                        f"Access denied: cannot kill process {proc.info['name']} "
                        f"(PID: {proc.info['pid']})."
                    )
                    continue
        if killed:
            for msg in killed:
                click.echo(f"Successfully terminated process {msg}.")
        else:
            click.echo(f"No process found with name containing '{target}'.")

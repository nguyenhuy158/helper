"""Speed test commands."""

import click
import speedtest
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def format_speed(speed_bps):
    """Convert speed from bits per second to appropriate unit."""
    for unit in ["bps", "Kbps", "Mbps", "Gbps"]:
        if speed_bps < 1000 or unit == "Gbps":
            return f"{speed_bps:.2f} {unit}"
        speed_bps /= 1000


def get_speed():
    """Run speed test and return results as dict."""
    try:
        st = speedtest.Speedtest()

        server = st.get_best_server()

        download_speed = st.download()

        upload_speed = st.upload()

        ping = st.results.ping

        return {
            "client": st.results.client,
            "server": server,
            "ping": ping,
            "download": download_speed,
            "upload": upload_speed,
        }

    except speedtest.SpeedtestException as e:
        return {"error": f"Error running speed test: {e!s}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e!s}"}


@click.command()
@click.option("--simple", "-s", is_flag=True, help="Only show basic speed information")
def speed(simple):
    """Test internet speed using speedtest.net

    This command tests your internet connection's download and upload speeds
    using the speedtest.net service through the Python speedtest-cli library.
    """
    with console.status("[bold green]Running speed test..."):
        result = get_speed()

    if "error" in result:
        console.print(f"[red]{result['error']}[/red]")
        return 1

    client_info = f"Testing from {result['client']['isp']} ({result['client']['ip']})"

    ping = result["ping"]
    download_speed = result["download"]
    upload_speed = result["upload"]

    if simple:
        console.print(f"Ping: [yellow]{ping:.2f} ms[/yellow]")
        console.print(f"Download: [green]{format_speed(download_speed)}[/green]")
        console.print(f"Upload: [blue]{format_speed(upload_speed)}[/blue]")
    else:
        table = Table(title="Speed Test Results", box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold")
        table.add_row("Ping", f"{ping:.2f} ms")
        table.add_row("Download", format_speed(download_speed))
        table.add_row("Upload", format_speed(upload_speed))

        console.print(Panel(table, title="Speed Test", border_style="green", subtitle=client_info))

    return 0


# Add aliases for the command
speed_test = speed
sp = speed

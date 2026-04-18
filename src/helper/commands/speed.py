"""Speed test commands."""

import click
import speedtest


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
        return {"error": f"Error running speed test: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}


@click.command()
@click.option("--simple", "-s", is_flag=True, help="Only show basic speed information")
def speed(simple):
    """Test internet speed using speedtest.net

    This command tests your internet connection's download and upload speeds
    using the speedtest.net service through the Python speedtest-cli library.
    """
    result = get_speed()
    if "error" in result:
        click.echo(result["error"], err=True)
        return 1

    click.echo("Finding best server...")
    click.echo(f"Testing from {result['client']['isp']} " f"({result['client']['ip']})")
    click.echo(
        f"Hosted by {result['server']['name']} ({result['server']['country']}) [{result['server']['d']:.2f} km]"
    )

    click.echo("Testing download speed...")
    click.echo("Testing upload speed...")

    ping = result["ping"]
    download_speed = result["download"]
    upload_speed = result["upload"]

    if simple:
        click.echo(f"Ping: {ping:.2f} ms")
        click.echo(f"Download: {format_speed(download_speed)}")
        click.echo(f"Upload: {format_speed(upload_speed)}")
    else:
        click.echo("\n=== Speed Test Results ===")
        click.echo(f"{'Ping:':<12} {ping:>8.2f} ms")
        click.echo(f"{'Download:':<12} {format_speed(download_speed):>8}")
        click.echo(f"{'Upload:':<12} {format_speed(upload_speed):>8}")

    return 0


# Add aliases for the command
speed_test = speed
sp = speed

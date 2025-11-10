import click
import speedtest
from time import time


def format_speed(speed_bps):
    """Convert speed from bits per second to appropriate unit."""
    for unit in ['bps', 'Kbps', 'Mbps', 'Gbps']:
        if speed_bps < 1000 or unit == 'Gbps':
            return f"{speed_bps:.2f} {unit}"
        speed_bps /= 1000


def run_speedtest(simple_mode=False):
    """Run speed test and return results."""
    try:
        st = speedtest.Speedtest()
        
        click.echo("Finding best server...")
        server = st.get_best_server()
        
        click.echo(f"Testing from {st.results.client['isp']} ({st.results.client['ip']})")
        click.echo(f"Hosted by {server['name']} ({server['country']}) [{server['d']:.2f} km]")
        
        click.echo("Testing download speed...")
        download_speed = st.download()
        
        click.echo("Testing upload speed...")
        upload_speed = st.upload()
        
        ping = st.results.ping
        
        if simple_mode:
            click.echo(f"Ping: {ping:.2f} ms")
            click.echo(f"Download: {format_speed(download_speed)}")
            click.echo(f"Upload: {format_speed(upload_speed)}")
        else:
            click.echo("\n=== Speed Test Results ===")
            click.echo(f"{'Ping:':<12} {ping:>8.2f} ms")
            click.echo(f"{'Download:':<12} {format_speed(download_speed):>8}")
            click.echo(f"{'Upload:':<12} {format_speed(upload_speed):>8}")
            
    except speedtest.SpeedtestException as e:
        click.echo(f"Error running speed test: {str(e)}", err=True)
        return 1
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}", err=True)
        return 1
    
    return 0


@click.command()
@click.option("--simple", "-s", is_flag=True, help="Only show basic speed information")
def speed(simple):
    """Test internet speed using speedtest.net
    
    This command tests your internet connection's download and upload speeds
    using the speedtest.net service through the Python speedtest-cli library.
    """
    return run_speedtest(simple)


# Add aliases for the command
speed_test = speed
sp = speed

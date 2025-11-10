"""Environment variable management commands."""
import os
import click
from pathlib import Path
from ..env_manager import get_env, set_env, load_env, CONFIG_DIR, ENV_FILE


@click.group(name="env", help="Manage environment variables.")
def env():
    """Environment variable management commands."""
    pass


@env.command(name="list")
def list_env_cmd():
    """List all environment variables in a formatted table."""
    env_vars = load_env()
    if not env_vars:
        click.echo("No environment variables set.")
        return
    
    # Find the maximum key length for alignment
    max_key_len = max(len(str(k)) for k in env_vars.keys())
    
    # Print header
    click.echo("Environment Variables:")
    click.echo("-" * (max_key_len + 40))  # 40 is a rough estimate for value + padding
    
    # Print each variable
    for key, value in sorted(env_vars.items()):
        click.echo(f"{key.ljust(max_key_len)} : {value}")
    
    click.echo()  # Add a newline at the end


@env.command(name="get")
@click.argument("key", required=False)
def get_env_cmd(key):
    """Get environment variable(s).
    
    If no key is provided, all environment variables will be shown as a table.
    """
    if not key:
        return list_env_cmd()
        
    env_vars = load_env()
    value = env_vars.get(key, "")
    click.echo(f"{key}={value}")


@env.command(name="set")
@click.argument("key")
@click.argument("value")
def set_env_cmd(key, value):
    """Set an environment variable."""
    set_env(key, value)
    click.echo(f"Set {key}={value}")


@env.command(name="unset")
@click.argument("key")
def unset_env_cmd(key):
    """Unset an environment variable."""
    env_vars = load_env()
    if key in env_vars:
        del env_vars[key]
        save_env(env_vars)
        if key in os.environ:
            del os.environ[key]
        click.echo(f"Unset {key}")
    else:
        click.echo(f"Variable {key} not found", err=True)


def save_env(env_vars):
    """Save environment variables to .env file.
    
    Args:
        env_vars: Dictionary of environment variables to save.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(ENV_FILE, 'w', encoding='utf-8') as f:
        for key, value in env_vars.items():
            f.write(f'{key}="{value}"\n')

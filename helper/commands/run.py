"""Run predefined command snippets."""

import os
import sys
import subprocess

import click

from ..snippets import (
    add_snippet,
    remove_snippet,
    list_snippets,
    get_snippet_command,
    load_snippets,
)


def _get_snippet_by_index_or_name(snippet_name, snippets_list):
    """Get snippet name by index or return the name if it exists."""
    # If it's a digit, try to get by index
    if snippet_name.isdigit():
        index = int(snippet_name) - 1
        if 0 <= index < len(snippets_list):
            return snippets_list[index]
        return None
    # Otherwise check if it's a valid snippet name
    return snippet_name if snippet_name in snippets_list else None


@click.group(name="run", help="Run predefined command snippets.")
def run():
    """Run predefined command snippets.

    Examples:
        # List all snippets
        h run list

        # Show help for a specific command
        h run show --help

        # Add a new snippet
        h run add --help

        # Execute a snippet by name or index
        h run exec click-odoo /path/to/script.py
        h run exec 1 /path/to/script.py

        # Skip confirmation
        h run exec --force click-odoo /path/to/script.py
        h run exec -f 1 /path/to/script.py
    """
    pass  # Required for click command groups


@run.command(name="exec")
@click.argument("snippet")
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.option("-f", "--force", is_flag=True, help="Skip confirmation prompt")
def exec_cmd(snippet, args, force):
    """Execute a snippet with the given arguments.

    Examples:
        h run exec click-odoo /path/to/script.py
        h run exec 1 /path/to/script.py
        h run exec --force 1 /path/to/script.py
    """
    # Handle the 'list' command directly
    if snippet == "list":
        list_cmd()
        return

    # Load snippets and check if the provided snippet exists
    snippets = load_snippets()
    snippets_list = list(snippets.keys())

    if not snippets_list:
        click.echo("No snippets defined. Add some with 'h run add <name> <command>'")
        return

    # Try to get snippet by index or name
    snippet_name = _get_snippet_by_index_or_name(snippet, snippets_list)
    if not snippet_name:
        click.echo(
            f"Error: Snippet '{snippet}' not found. "
            "Use 'h run list' to see available snippets.",
            err=True,
        )
        return

    # Execute the snippet
    _execute_snippet(snippet_name, args, force)


def _execute_snippet(name, args, force):
    """Execute a snippet with the given arguments."""
    # Convert args to a dict of named parameters
    kwargs = {}
    if args:
        kwargs["file"] = args[0]
        kwargs["args"] = " ".join(args[1:]) if len(args) > 1 else ""

    try:
        command = get_snippet_command(name, **kwargs)
        if command is None:
            click.echo(f"Snippet '{name}' not found. Available snippets:", err=True)
            list_cmd()
            sys.exit(1)

        # Always show the command that will be executed
        click.echo(
            f"Command to execute: {click.style(command, fg='yellow', bold=True)}"
        )

        # Ask for confirmation if not in force mode
        if not force and not click.confirm(
            "Do you want to run this command?", default=False
        ):
            click.echo("Command execution cancelled.")
            return

        # Run the command
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Command failed with return code {e.returncode}", err=True)
        sys.exit(e.returncode)
    except Exception as e:  # pylint: disable=broad-except
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@run.command(name="list")
def list_cmd():
    """List all available snippets."""
    snippets = list_snippets()
    if not snippets:
        click.echo("No snippets defined. Add some with 'h run add <name> <command>'")
        return

    click.echo("Available snippets (use 'h run exec <number or name> <args>' to run):")
    click.echo("-" * 70)
    for i, name in enumerate(snippets, 1):
        click.echo(f"{i}. {name}")
    click.echo("\nExample: h run exec 1 /path/to/script.py")


@run.command(name="show")
@click.argument("snippet")
def show_cmd(snippet):
    """Show the command template for a specific snippet by name or index.

    Examples:
        h run show 1
        h run show click-odoo
    """
    snippets = load_snippets()
    snippets_list = list(snippets.keys())

    # Try to get snippet by index or name
    snippet_name = _get_snippet_by_index_or_name(snippet, snippets_list)
    if not snippet_name:
        click.echo(
            f"Snippet '{snippet}' not found. Use 'h run list' to see available snippets.",
            err=True,
        )
        return

    name = snippet_name  # Use the resolved snippet name

    click.echo(f"Snippet: {name}")
    click.echo("Command template:")
    click.echo(f"  {snippets[name]}")

    # Show environment values used in the command
    odoo_container = os.environ.get("ODOO_CONTAINER", "fnp-odoo-1")
    odoo_db_container = os.environ.get("ODOO_DB_CONTAINER", "fnp-db-1")

    click.echo("\nAvailable placeholders:")
    click.echo(
        f"  {{ODOO_CONTAINER}} - Odoo container name (current: {odoo_container})"
    )
    click.echo(
        f"  {{ODOO_DB_CONTAINER}} - DB container name (current: {odoo_db_container})"
    )
    click.echo("  {file} - The first argument after the snippet name")
    click.echo("  {args} - All remaining arguments as a single string")

    click.echo("\nExample usage:")
    example = f"h run {name} /path/to/script.py arg1 arg2"
    click.echo(f"  {example}")
    click.echo(
        "\nNote: {container} and {db_container} are also supported for backward compatibility"
    )


@run.command(name="add")
@click.argument("name")
@click.argument("command", nargs=-1)
def add_cmd(name, command):
    """Add or update a snippet.

    Example:
        h run add click-odoo "docker exec {ODOO_CONTAINER} bash -c \"click-odoo {file}\""

    Note: {container} will be automatically converted to {ODOO_CONTAINER}
    and {db_container} to {ODOO_DB_CONTAINER}
    """
    command_str = " ".join(command)

    # Replace placeholders to use environment variable names directly
    command_str = command_str.replace("{container}", "{ODOO_CONTAINER}").replace(
        "{db_container}", "{ODOO_DB_CONTAINER}"
    )

    add_snippet(name, command_str)
    click.echo(f"Added/updated snippet: {name}")
    click.echo(f"Command: {command_str}")
    click.echo(
        "\nNote: You can use {file} for the first argument and {args} for additional arguments"
    )


@run.command(name="remove")
@click.argument("name")
def remove_cmd(name):
    """Remove a snippet by name."""
    if remove_snippet(name):
        click.echo(f"Removed snippet: {name}")
    else:
        click.echo(f"Snippet '{name}' not found.", err=True)


@run.command(name="edit")
@click.argument("editor", required=False, default=None)
def edit_cmd(editor):
    """Edit snippets file directly in your default editor."""
    from ..snippets import SNIPPETS_FILE

    if not editor:
        editor = os.environ.get("EDITOR", "nano")

    try:
        subprocess.run([editor, str(SNIPPETS_FILE)], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        click.echo(f"Error opening editor: {e}", err=True)
        raise click.Abort()


# exec_cmd has been removed as its functionality is now handled by the main run command

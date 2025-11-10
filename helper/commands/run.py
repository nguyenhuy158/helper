"""Run predefined command snippets."""
import os
import subprocess

import click

from ..snippets import (
    add_snippet, remove_snippet, list_snippets, get_snippet_command,
    load_snippets
)


@click.group(name="run", help="Run predefined command snippets.", invoke_without_command=True)
@click.argument('snippet', required=False)
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.option('-f', '--force', is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def run(ctx, snippet, args, force):
    """Run predefined command snippets.
    
    Examples:
        # List all snippets
        h run list
        
        # Execute a snippet
        h run click-odoo /path/to/script.py
        
        # Skip confirmation
        h run --force click-odoo /path/to/script.py
        h run -f click-odoo /path/to/script.py
    """
    # If no subcommand is provided, try to execute the snippet directly
    if ctx.invoked_subcommand is None:
        if not snippet:
            click.echo("Error: No snippet specified. Use 'h run list' to see available snippets.")
            ctx.exit(1)
        
        # Handle the 'list' command directly
        if snippet == 'list':
            list_cmd()
            return
            
        # Handle other commands by checking if they're valid snippets
        snippets = load_snippets()
        if snippet not in snippets:
            click.echo(f"Error: Snippet '{snippet}' not found. Use 'h run list' to see available snippets.", err=True)
            ctx.exit(1)
            
        # Execute the snippet
        _execute_snippet(snippet, args, force)
        return
        
    # If we get here, it means a subcommand was used
    pass


def _execute_snippet(name, args, force):
    """Execute a snippet with the given arguments."""
    # Convert args to a dict of named parameters
    kwargs = {}
    if args:
        kwargs['file'] = args[0]
        kwargs['args'] = ' '.join(args[1:]) if len(args) > 1 else ''
    
    try:
        command = get_snippet_command(name, **kwargs)
        if command is None:
            click.echo(f"Snippet '{name}' not found. Available snippets:", err=True)
            list_cmd()
            sys.exit(1)
        
        # Always show the command that will be executed
        click.echo(f"Command to execute: {click.style(command, fg='yellow', bold=True)}")
        
        # Ask for confirmation if not in force mode
        if not force and not click.confirm('Do you want to run this command?', default=False):
            click.echo("Command execution cancelled.")
            return
            
        # Run the command
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Command failed with return code {e.returncode}", err=True)
        sys.exit(e.returncode)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def list_cmd():
    """List all available snippets."""
    snippets = list_snippets()
    if not snippets:
        click.echo("No snippets defined. Add some with 'h run add <name> <command>'")
        return
    
    click.echo("Available snippets:")
    click.echo("-" * 50)
    for i, name in enumerate(snippets, 1):
        click.echo(f"{i}. {name}")


@run.command(name="list")
def list_cmd_wrapper():
    """List all available snippets."""
    list_cmd()


@run.command(name="show")
@click.argument("name")
def show_cmd(name):
    """Show the command template for a specific snippet."""
    snippets = load_snippets()
    if name not in snippets:
        click.echo(f"Snippet '{name}' not found.", err=True)
        return
    
    click.echo(f"Snippet: {name}")
    click.echo("Command template:")
    click.echo(f"  {snippets[name]}")
    
    # Get current environment values
    import os
    odoo_container = os.environ.get('ODOO_CONTAINER', 'fnp-odoo-1')
    odoo_db_container = os.environ.get('ODOO_DB_CONTAINER', 'fnp-db-1')
    
    click.echo("\nAvailable placeholders:")
    click.echo(f"  {{ODOO_CONTAINER}} - Odoo container name (current: {odoo_container})")
    click.echo(f"  {{ODOO_DB_CONTAINER}} - DB container name (current: {odoo_db_container})")
    click.echo("  {file} - The first argument after the snippet name")
    click.echo("  {args} - All remaining arguments as a single string")
    
    click.echo("\nExample usage:")
    example = f"h run {name} /path/to/script.py arg1 arg2"
    click.echo(f"  {example}")
    click.echo("\nNote: {container} and {db_container} are also supported for backward compatibility")


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
    command_str = command_str.replace('{container}', '{ODOO_CONTAINER}') \
                           .replace('{db_container}', '{ODOO_DB_CONTAINER}')
    
    add_snippet(name, command_str)
    click.echo(f"Added/updated snippet: {name}")
    click.echo(f"Command: {command_str}")
    click.echo("\nNote: You can use {file} for the first argument and {args} for additional arguments")


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
        editor = os.environ.get('EDITOR', 'nano')
    
    try:
        subprocess.run([editor, str(SNIPPETS_FILE)], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        click.echo(f"Error opening editor: {e}", err=True)
        raise click.Abort()


# exec_cmd has been removed as its functionality is now handled by the main run command
        ctx.exit(1)

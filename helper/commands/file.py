"""File management commands."""
import os
import time
import click
from pathlib import Path
from typing import List, Optional, Tuple, Callable
from datetime import datetime


def get_sorted_files(
    directory: str, 
    extension: Optional[str] = None, 
    sort_key: Callable[[os.DirEntry], float] = None,
    reverse: bool = False
) -> List[Tuple[os.DirEntry, float]]:
    """Get files sorted by specified key.
    
    Args:
        directory: Directory to search in
        extension: Optional file extension to filter by (without dot)
        sort_key: Function to extract sort key from DirEntry
        reverse: If True, sort in descending order
        
    Returns:
        List of (file_entry, sort_key) tuples
    """
    if not os.path.isdir(directory):
        raise click.BadParameter(f"Directory not found: {directory}")
    
    files = []
    with os.scandir(directory) as it:
        for entry in it:
            if not entry.is_file():
                continue
                
            if extension and not entry.name.lower().endswith(f".{extension.lower()}"):
                continue
                
            if sort_key:
                try:
                    key = sort_key(entry)
                    files.append((entry, key))
                except (OSError, ValueError) as e:
                    continue
            else:
                files.append((entry, 0))
    
    # Sort by the sort key
    files.sort(key=lambda x: x[1], reverse=reverse)
    return files


def format_file_info(entry: os.DirEntry, size: bool = True, modified: bool = True) -> str:
    """Format file information for display."""
    info = []
    if size:
        try:
            size_bytes = entry.stat().st_size
            size_str = human_readable_size(size_bytes)
            info.append(f"{size_str:>10}")
        except OSError:
            info.append(" " * 10)
    
    if modified:
        try:
            mtime = entry.stat().st_mtime
            mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            info.append(mtime_str)
        except OSError:
            info.append(" " * 19)
    
    info.append(entry.name)
    return "  ".join(info)


def human_readable_size(size_bytes: int) -> str:
    """Convert size in bytes to human readable format."""
    if size_bytes == 0:
        return "0B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_idx = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_idx < len(units) - 1:
        size /= 1024
        unit_idx += 1
    
    return f"{size:.1f}{units[unit_idx]}"


@click.group(name="file")
@click.option(
    "--directory",
    "-d",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    default=".",
    help="Directory to search in (default: current directory)",
)
@click.option(
    "--extension",
    "-e",
    type=str,
    help="Filter by file extension (without dot)",
)
@click.option(
    "--size",
    "-s",
    is_flag=True,
    help="Show file sizes",
)
@click.option(
    "--modified",
    "-m",
    is_flag=True,
    help="Show last modified time",
)
@click.pass_context
def file_cmd(ctx: click.Context, directory: str, extension: str, size: bool, modified: bool) -> None:
    """File management and processing commands."""
    ctx.ensure_object(dict)
    ctx.obj["directory"] = directory
    ctx.obj["extension"] = extension
    ctx.obj["show_size"] = size
    ctx.obj["show_modified"] = modified


@file_cmd.command(name="newest")
@click.option(
    "--count",
    "-n",
    type=int,
    default=1,
    help="Number of newest files to show (default: 1)",
)
@click.pass_context
def newest_files(ctx: click.Context, count: int) -> None:
    """Show the newest files in the directory."""
    directory = ctx.obj["directory"]
    extension = ctx.obj["extension"]
    show_size = ctx.obj["show_size"]
    show_modified = ctx.obj["show_modified"]
    
    try:
        files = get_sorted_files(
            directory=directory,
            extension=extension,
            sort_key=lambda e: e.stat().st_mtime,
            reverse=True
        )
        
        if not files:
            click.echo("No files found.")
            return
            
        click.echo(f"Newest files in {directory}:")
        for i, (entry, _) in enumerate(files[:count], 1):
            click.echo(f"{i}. {format_file_info(entry, show_size, show_modified)}")
            
    except Exception as e:
        raise click.ClickException(str(e))


@file_cmd.command(name="oldest")
@click.option(
    "--count",
    "-n",
    type=int,
    default=1,
    help="Number of oldest files to show (default: 1)",
)
@click.pass_context
def oldest_files(ctx: click.Context, count: int) -> None:
    """Show the oldest files in the directory."""
    directory = ctx.obj["directory"]
    extension = ctx.obj["extension"]
    show_size = ctx.obj["show_size"]
    show_modified = ctx.obj["show_modified"]
    
    try:
        files = get_sorted_files(
            directory=directory,
            extension=extension,
            sort_key=lambda e: e.stat().st_mtime,
            reverse=False
        )
        
        if not files:
            click.echo("No files found.")
            return
            
        click.echo(f"Oldest files in {directory}:")
        for i, (entry, _) in enumerate(files[:count], 1):
            click.echo(f"{i}. {format_file_info(entry, show_size, show_modified)}")
            
    except Exception as e:
        raise click.ClickException(str(e))


# Add this to register the command group
def file():
    return file_cmd

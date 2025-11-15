"""Utility functions for the helper CLI."""

import subprocess


def format_bytes(size_bytes):
    """Convert bytes to human readable format."""
    if not isinstance(size_bytes, (int, float)):
        try:
            size_bytes = float(size_bytes)
        except (ValueError, TypeError):
            return str(size_bytes)

    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if size_bytes < 1024.0 or unit == "PB":
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def run_cmd(cmd):
    """Run a shell command and print the output."""
    print(f"$ {cmd}")
    try:
        result = subprocess.check_output(cmd, shell=True, text=True).strip()
        print(result)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None

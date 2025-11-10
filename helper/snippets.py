"""Snippet management for frequently used commands."""
import os
from typing import Dict, List, Optional
from .env_manager import CONFIG_DIR
import json
from pathlib import Path

SNIPPETS_FILE = CONFIG_DIR / "snippets.json"


def ensure_snippets_file() -> None:
    """Ensure the snippets file exists with default content if it doesn't exist."""
    if not SNIPPETS_FILE.exists():
        SNIPPETS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SNIPPETS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"snippets": {}}, f, indent=2)


def load_snippets() -> Dict[str, str]:
    """Load all snippets from the snippets file."""
    ensure_snippets_file()
    with open(SNIPPETS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("snippets", {})


def save_snippets(snippets: Dict[str, str]) -> None:
    """Save snippets to the snippets file."""
    ensure_snippets_file()
    with open(SNIPPETS_FILE, 'w', encoding='utf-8') as f:
        json.dump({"snippets": snippets}, f, indent=2)


def add_snippet(name: str, command: str) -> None:
    """Add or update a snippet.
    
    Args:
        name: Name of the snippet
        command: Command template (can include placeholders like {container} or {file})
    """
    snippets = load_snippets()
    snippets[name] = command
    save_snippets(snippets)


def remove_snippet(name: str) -> bool:
    """Remove a snippet by name.
    
    Returns:
        bool: True if snippet was removed, False if not found
    """
    snippets = load_snippets()
    if name in snippets:
        del snippets[name]
        save_snippets(snippets)
        return True
    return False


def list_snippets() -> List[str]:
    """List all available snippet names."""
    snippets = load_snippets()
    return list(snippets.keys())


def get_snippet_command(name: str, **kwargs) -> Optional[str]:
    """Get a formatted command from a snippet.
    
    Args:
        name: Name of the snippet
        **kwargs: Variables to format into the command
        
    Returns:
        Formatted command string or None if snippet not found
    """
    import os
    
    snippets = load_snippets()
    if name not in snippets:
        return None
    
    # Get values from environment with defaults
    odoo_container = os.environ.get('ODOO_CONTAINER', 'fnp-odoo-1')
    odoo_db_container = os.environ.get('ODOO_DB_CONTAINER', 'fnp-db-1')
    
    # Add default variables if not provided
    defaults = {
        # Old style placeholders (for backward compatibility)
        'container': odoo_container,
        'db_container': odoo_db_container,
        # New style placeholders
        'ODOO_CONTAINER': odoo_container,
        'ODOO_DB_CONTAINER': odoo_db_container,
        # File and args placeholders (will be filled by run command)
        'file': '',
        'args': ''
    }
    
    # Update defaults with provided kwargs
    defaults.update(kwargs)
    
    try:
        return snippets[name].format(**defaults)
    except KeyError as e:
        raise ValueError(f"Missing required parameter: {e}") from e

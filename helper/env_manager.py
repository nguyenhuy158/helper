"""Environment variable management for helper tool."""
import os
from pathlib import Path
from typing import Dict, Optional

# Default environment variables
DEFAULT_ENV = {
    "AUTHOR": "nguyenhuy158",
    "REPO": "github",
    "ODOO_CONTAINER": "fnp-odoo-1",
}

# Environment file path
CONFIG_DIR = Path.home() / ".config" / "helper"
ENV_FILE = CONFIG_DIR / ".env"


def ensure_config_dir() -> None:
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_env() -> Dict[str, str]:
    """Load environment variables from .env file or create with defaults.
    
    Returns:
        Dict containing the environment variables.
    """
    # Ensure config directory exists
    ensure_config_dir()
    
    env_vars = DEFAULT_ENV.copy()
    
    # Load existing .env file if it exists
    if ENV_FILE.exists():
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip().strip('"\'')
                    except ValueError:
                        continue
    else:
        # Create .env file with default values
        save_env(env_vars)
    
    # Update os.environ with loaded values
    os.environ.update(env_vars)
    
    return env_vars


def save_env(env_vars: Dict[str, str]) -> None:
    """Save environment variables to .env file.
    
    Args:
        env_vars: Dictionary of environment variables to save.
    """
    ensure_config_dir()
    
    with open(ENV_FILE, 'w', encoding='utf-8') as f:
        for key, value in env_vars.items():
            f.write(f'{key}="{value}"\n')


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get an environment variable value.
    
    Args:
        key: The environment variable name.
        default: Default value if key doesn't exist.
        
    Returns:
        The value of the environment variable or default if not found.
    """
    env_vars = load_env()
    return env_vars.get(key, default)


def set_env(key: str, value: str) -> None:
    """Set an environment variable and save to .env file.
    
    Args:
        key: The environment variable name.
        value: The value to set.
    """
    env_vars = load_env()
    env_vars[key] = value
    save_env(env_vars)
    os.environ[key] = value

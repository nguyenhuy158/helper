"""Shared test fixtures and configuration."""

import pytest
from click.testing import CliRunner

from helper.main import cli


@pytest.fixture
def runner():
    """Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def cli_app(runner):
    """CLI application instance."""
    return runner, cli

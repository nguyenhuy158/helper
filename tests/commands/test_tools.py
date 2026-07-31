"""Tests for tools command.

This module contains tests for the tools command functionality,
including unit tests for the get_tools function and integration tests
for the CLI command output.
"""

from helper.commands.tools import get_tools


class TestGetTools:
    """Test cases for the get_tools function that returns the tool showcase list."""

    def test_returns_non_empty_list(self):
        """Test that get_tools returns a non-empty list of tools."""
        result = get_tools()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_tools_have_required_fields(self):
        """Test that every tool entry has name, description, install, and repo fields."""
        for tool in get_tools():
            assert tool["name"]
            assert tool["description"]
            assert tool["install"]
            assert tool["repo"].startswith("https://")

    def test_includes_pgslim(self):
        """Test that pgslim is included in the tool list."""
        names = [tool["name"] for tool in get_tools()]
        assert "pgslim" in names


class TestToolsCommand:
    """Test cases for the tools CLI command."""

    def test_command_help(self, cli_app):
        """Test that the tools command displays proper help information."""
        runner, cli = cli_app
        result = runner.invoke(cli, ["tools", "--help"])

        assert result.exit_code == 0
        assert "List other tools by the same author" in result.output

    def test_command_output(self, cli_app):
        """Test that the tools command lists all tools by name."""
        runner, cli = cli_app
        result = runner.invoke(cli, ["tools"])

        assert result.exit_code == 0
        assert "pgslim" in result.output
        assert "helper-cli" in result.output

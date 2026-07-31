"""Tests for tools command.

This module contains tests for the tools command functionality,
including unit tests for the get_tools function (remote fetch with
local fallback) and integration tests for the CLI command output.
"""

import json
from unittest.mock import patch

from helper.commands.tools import FALLBACK_TOOLS, get_tools


class TestGetTools:
    """Test cases for the get_tools function."""

    @patch("helper.commands.tools._request")
    def test_fetches_remote_tools_json(self, mock_request):
        """Test that the remote tools.json is fetched and parsed."""
        remote = [{"name": "new-tool", "description": "d", "install": "i", "repo": "https://r"}]
        mock_request.return_value = json.dumps(remote).encode()

        assert get_tools() == remote

    @patch("helper.commands.tools._request")
    def test_falls_back_when_fetch_fails(self, mock_request):
        """Test that the built-in list is returned when the fetch fails."""
        mock_request.side_effect = OSError("offline")

        assert get_tools() == FALLBACK_TOOLS

    def test_fallback_is_non_empty(self):
        """Test that the fallback list has tools."""
        assert len(FALLBACK_TOOLS) > 0

    def test_fallback_tools_have_required_fields(self):
        """Test that every fallback entry has name, description, install, and repo."""
        for tool in FALLBACK_TOOLS:
            assert tool["name"]
            assert tool["description"]
            assert tool["install"]
            assert tool["repo"].startswith("https://")

    def test_fallback_includes_pgslim(self):
        """Test that pgslim is included in the fallback list."""
        names = [tool["name"] for tool in FALLBACK_TOOLS]
        assert "pgslim" in names


class TestToolsCommand:
    """Test cases for the tools CLI command."""

    def test_command_help(self, cli_app):
        """Test that the tools command displays proper help information."""
        runner, cli = cli_app
        result = runner.invoke(cli, ["tools", "--help"])

        assert result.exit_code == 0
        assert "List other tools by the same author" in result.output

    @patch("helper.commands.tools.get_tools")
    def test_command_output(self, mock_get_tools, cli_app):
        """Test that the tools command lists all tools by name."""
        mock_get_tools.return_value = FALLBACK_TOOLS
        runner, cli = cli_app

        result = runner.invoke(cli, ["tools"])

        assert result.exit_code == 0
        assert "pgslim" in result.output
        assert "helper-cli" in result.output

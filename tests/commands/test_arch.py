"""Tests for arch command.

This module contains comprehensive tests for the architecture command functionality,
including both unit tests for the get_arch function and integration tests for the CLI command.
Tests cover successful execution, error handling, and command output formatting.
"""

import subprocess
from unittest.mock import patch

from helper.commands.arch import get_arch


class TestGetArch:
    """Test cases for the get_arch function that retrieves system architecture information.

    This class tests both successful execution and error handling scenarios
    for the get_arch function which uses 'uname -m' command.
    """

    @patch("subprocess.check_output")
    def test_success(self, mock_subprocess):
        """Test successful execution of uname -m command.

        Verifies that the function returns the stripped output from subprocess.check_output
        and that the correct command is called with proper parameters.
        """
        mock_subprocess.return_value = "arm64\n"

        result = get_arch()
        assert result == "arm64"
        mock_subprocess.assert_called_once_with("uname -m", shell=True, text=True)

    @patch("subprocess.check_output")
    def test_error(self, mock_subprocess):
        """Test error handling when uname -m command fails.

        Verifies that when subprocess.check_output raises CalledProcessError,
        the function catches it and returns an appropriate error message.
        """
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "uname -m")

        result = get_arch()
        assert "Error:" in result


class TestArchCommand:
    """Test cases for the arch CLI command.

    This class tests the Click command wrapper that displays architecture
    information to stdout, including the command output format.
    """

    def test_command_help(self, cli_app):
        """Test that the arch command displays proper help information.

        Verifies that running 'helper arch --help' shows the command description
        and usage information without errors.
        """
        runner, cli = cli_app
        result = runner.invoke(cli, ["arch", "--help"])

        assert result.exit_code == 0
        assert "Display system architecture information" in result.output

    @patch("helper.commands.arch.get_arch")
    def test_command_output(self, mock_get_arch, cli_app):
        """Test that the arch command outputs architecture information correctly.

        Verifies that the command prints the 'uname -m' command prefix followed by
        the architecture value returned from get_arch function.
        """
        mock_get_arch.return_value = "x86_64"
        runner, cli = cli_app

        result = runner.invoke(cli, ["arch"])

        assert result.exit_code == 0
        assert "$ uname -m" in result.output
        assert "x86_64" in result.output

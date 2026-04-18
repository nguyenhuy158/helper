"""Tests for public IP command.

This module tests public/external IP address retrieval using external services.
Tests cover successful IP fetching, network error handling, and CLI command output.
"""

import subprocess
from unittest.mock import patch

from helper.commands.public_ip import get_public_ip


class TestGetPublicIP:
    """Test cases for the get_public_ip function that retrieves external IP address.

    This class tests public IP retrieval using curl to ifconfig.me,
    including error handling for network failures and command errors.
    """

    @patch("subprocess.check_output")
    def test_success(self, mock_subprocess):
        """Test successful public IP retrieval."""
        mock_subprocess.return_value = "203.0.113.45\n"

        result = get_public_ip()
        assert result == "203.0.113.45"
        mock_subprocess.assert_called_once_with("curl -s ifconfig.me", shell=True, text=True)

    @patch("subprocess.check_output")
    def test_error(self, mock_subprocess):
        """Test error handling."""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "curl -s ifconfig.me")

        result = get_public_ip()
        assert "Error:" in result


class TestPublicIPCommand:
    """Test cases for the public_ip CLI command.

    This class tests the Click command that displays the public/external IP address
    and verifies the command output format and help information.
    """

    def test_command_help(self, cli_app):
        """Test command help output."""
        runner, cli = cli_app
        result = runner.invoke(cli, ["pubip", "--help"])

        assert result.exit_code == 0
        assert "Display the public (external) IP address" in result.output

    @patch("helper.commands.public_ip.get_public_ip")
    def test_command_output(self, mock_get_ip, cli_app):
        """Test command outputs IP address."""
        mock_get_ip.return_value = "203.0.113.45"
        runner, cli = cli_app

        result = runner.invoke(cli, ["pubip"])

        assert result.exit_code == 0
        assert "$ curl -s ifconfig.me" in result.output
        assert "203.0.113.45" in result.output

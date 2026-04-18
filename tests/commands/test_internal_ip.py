"""Tests for internal IP command.

This module contains tests for the internal IP address retrieval functionality,
covering different operating systems (macOS, Linux) and error scenarios.
Tests include both function-level and command-level testing.
"""

import subprocess
from unittest.mock import patch

from helper.commands.internal_ip import get_internal_ip


class TestGetInternalIP:
    """Test cases for the get_internal_ip function that retrieves local IP address.

    This class tests IP address retrieval on different operating systems (macOS, Linux)
    and error handling when network commands fail.
    """

    @patch("platform.system")
    @patch("subprocess.check_output")
    def test_darwin_success(self, mock_subprocess, mock_platform):
        """Test successful IP retrieval on macOS."""
        mock_platform.return_value = "Darwin"
        mock_subprocess.return_value = "192.168.1.100\n"

        result = get_internal_ip()
        assert result == "192.168.1.100"
        mock_subprocess.assert_called_once_with("ipconfig getifaddr en0", shell=True, text=True)

    @patch("platform.system")
    @patch("subprocess.check_output")
    def test_darwin_error(self, mock_subprocess, mock_platform):
        """Test error handling on macOS."""
        mock_platform.return_value = "Darwin"
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "ipconfig getifaddr en0")

        result = get_internal_ip()
        assert "Error:" in result

    @patch("platform.system")
    @patch("shutil.which")
    @patch("subprocess.check_output")
    def test_linux_with_ifconfig(self, mock_subprocess, mock_which, mock_platform):
        """Test IP retrieval on Linux with ifconfig."""
        mock_platform.return_value = "Linux"
        mock_which.return_value = "/usr/bin/ifconfig"
        mock_subprocess.return_value = "192.168.1.100\n"

        result = get_internal_ip()
        assert result == "192.168.1.100"

    @patch("platform.system")
    @patch("shutil.which")
    @patch("subprocess.check_output")
    def test_linux_without_ifconfig(self, mock_subprocess, mock_which, mock_platform):
        """Test IP retrieval on Linux without ifconfig."""
        mock_platform.return_value = "Linux"
        mock_which.return_value = None
        mock_subprocess.return_value = "192.168.1.100\n"

        result = get_internal_ip()
        assert result == "192.168.1.100"

    @patch("platform.system")
    @patch("socket.gethostbyname")
    @patch("socket.gethostname")
    def test_other_platform(self, mock_gethostname, mock_gethostbyname, mock_platform):
        """Test IP retrieval on other platforms."""
        mock_platform.return_value = "Windows"
        mock_gethostname.return_value = "localhost"
        mock_gethostbyname.return_value = "127.0.0.1"

        result = get_internal_ip()
        assert result == "127.0.0.1"


class TestInternalIPCommand:
    """Test cases for the internal_ip CLI command.

    This class tests the Click command that displays the local/internal IP address
    and verifies the command help and output formatting.
    """

    def test_command_help(self, cli_app):
        """Test command help output."""
        runner, cli = cli_app
        result = runner.invoke(cli, ["ip", "--help"])

        assert result.exit_code == 0
        assert "Display the local/internal IP address" in result.output

    @patch("helper.commands.internal_ip.get_internal_ip")
    def test_command_output(self, mock_get_ip, cli_app):
        """Test command outputs IP address."""
        mock_get_ip.return_value = "192.168.1.100"
        runner, cli = cli_app

        result = runner.invoke(cli, ["ip"])

        assert result.exit_code == 0
        assert "192.168.1.100" in result.output

    @patch("helper.commands.internal_ip.get_internal_ip")
    def test_command_no_output_when_empty(self, mock_get_ip, cli_app):
        """Test command handles empty IP gracefully."""
        mock_get_ip.return_value = ""
        runner, cli = cli_app

        result = runner.invoke(cli, ["ip"])

        assert result.exit_code == 0
        assert result.output.strip() == ""

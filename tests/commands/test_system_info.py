"""Tests for system_info command.

This module tests comprehensive system information gathering across different
operating systems. Tests cover CPU, memory, disk, and OS information retrieval,
command execution, and CLI output formatting.
"""

import pytest
import subprocess
from unittest.mock import patch, MagicMock

from helper.commands.system_info import get_info, system_info, run_command


class TestRunCommand:
    """Test cases for the run_command function that executes shell commands.

    This class tests command execution with proper output capture and error handling,
    including scenarios where commands succeed or fail.
    """

    @patch("subprocess.check_output")
    def test_success(self, mock_subprocess):
        """Test successful command execution."""
        mock_subprocess.return_value = "output\n"

        result = run_command("echo test")
        assert result == "output"
        mock_subprocess.assert_called_once()

    @patch("subprocess.check_output")
    def test_empty_output(self, mock_subprocess):
        """Test command with empty output."""
        mock_subprocess.return_value = ""

        result = run_command("echo")
        assert result == "N/A"

    @patch("subprocess.check_output")
    def test_command_error(self, mock_subprocess):
        """Test command execution error."""
        mock_subprocess.side_effect = subprocess.CalledProcessError(
            1, "bad_command", output="Command failed"
        )

        result = run_command("bad_command")
        assert "Command failed" in result


class TestGetInfo:
    """Test cases for the get_info function that collects system information.

    This class tests system information gathering across different operating systems,
    including CPU, memory, disk, and OS details with proper mocking.
    """

    @patch("platform.system")
    @patch("helper.commands.system_info.run_command")
    @patch("platform.release")
    @patch("platform.machine")
    @patch("platform.processor")
    def test_basic_info_structure(
        self, mock_processor, mock_machine, mock_release, mock_run, mock_system
    ):
        """Test that get_info returns expected structure."""
        mock_system.return_value = "Linux"
        mock_release.return_value = "5.4.0"
        mock_machine.return_value = "x86_64"
        mock_processor.return_value = "Intel"
        mock_run.side_effect = [
            "hostname",
            "os_version",
            "uptime",
            "2",
            "cpu_info",
            "load_avg",
            "              total        used        free      shared  buff/cache   available\nMem:           1024         512         256         0         256         512",
            "disk_info",
        ]

        info = get_info()

        assert info is not None
        assert "system" in info
        assert "os_version" in info
        assert "uptime" in info
        assert "cpu" in info
        assert "memory" in info
        assert "disks" in info

    @patch("platform.system")
    def test_unsupported_os(self, mock_system):
        """Test unsupported operating system."""
        mock_system.return_value = "UnknownOS"

        info = get_info()
        assert info is None


class TestSystemInfoCommand:
    """Test cases for the system_info CLI command.

    This class tests the Click command that displays comprehensive system information
    and verifies the command output formatting and structure.
    """

    def test_command_help(self, cli_app):
        """Test command help output."""
        runner, cli = cli_app
        result = runner.invoke(cli, ["si", "--help"])

        assert result.exit_code == 0
        assert "Display system information" in result.output

    @patch("helper.commands.system_info.get_info")
    def test_command_with_info(self, mock_get_info, cli_app):
        """Test command with valid system info."""
        mock_info = {
            "system": {
                "system": "Linux",
                "release": "5.4.0",
                "node": "test-host",
                "machine": "x86_64",
                "processor": "Intel CPU",
            },
            "os_version": "Ubuntu 20.04",
            "uptime": "Uptime: 1 day",
            "cpu": {"cores": "4", "cpu": "Intel", "load_avg": "1.0 1.0 1.0"},
            "memory": {"total": "8GB", "used": "4GB", "free": "4GB", "usage": "50%"},
            "disks": "/dev/sda 100GB 50GB 50GB 50%",
        }
        mock_get_info.return_value = mock_info

        runner, cli = cli_app
        result = runner.invoke(cli, ["si"])

        assert result.exit_code == 0
        assert "System Information" in result.output
        assert "Linux 5.4.0" in result.output

    @patch("helper.commands.system_info.get_info")
    def test_command_unsupported_os(self, mock_get_info, cli_app):
        """Test command with unsupported OS."""
        mock_get_info.return_value = None

        runner, cli = cli_app
        result = runner.invoke(cli, ["si"])

        assert result.exit_code == 0
        assert "Unsupported operating system" in result.output

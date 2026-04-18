"""Tests for nixos command.

This module tests NixOS-specific functionality including version detection,
version retrieval, and command-line interface. Tests cover both detection
logic and error handling for non-NixOS systems.
"""

import subprocess
from unittest.mock import patch, MagicMock

from helper.commands.nixos import check_nixos, get_nixos_version


class TestCheckNixos:
    """Test cases for the check_nixos function that detects NixOS environment.

    This class tests the detection logic for whether the system is running NixOS
    by checking for the presence of /etc/NIXOS files.
    """

    @patch("builtins.open")
    def test_nixos_detected(self, mock_open):
        """Test NixOS detection when /etc/os-release contains NixOS."""
        mock_file = MagicMock()
        mock_file.read.return_value = "NAME=NixOS"
        mock_open.return_value.__enter__.return_value = mock_file

        result = check_nixos()
        assert result is True

    @patch("builtins.open")
    def test_not_nixos(self, mock_open):
        """Test when not running on NixOS."""
        mock_file = MagicMock()
        mock_file.read.return_value = "NAME=Ubuntu"
        mock_open.return_value.__enter__.return_value = mock_file

        result = check_nixos()
        assert result is False

    @patch("builtins.open")
    def test_file_not_found(self, mock_open):
        """Test when /etc/os-release doesn't exist."""
        mock_open.side_effect = FileNotFoundError()

        result = check_nixos()
        assert result is False


class TestGetNixosVersion:
    """Test cases for the get_nixos_version function that retrieves NixOS version.

    This class tests version retrieval using the nixos-version command,
    including error handling when the command fails or is not available.
    """

    @patch("helper.commands.nixos.check_nixos")
    @patch("subprocess.run")
    def test_version_success(self, mock_subprocess, mock_check):
        """Test successful version retrieval."""
        mock_check.return_value = True
        mock_result = MagicMock()
        mock_result.stdout = "21.11.20220101\n"
        mock_subprocess.return_value = mock_result

        result = get_nixos_version()
        assert result == "21.11.20220101"

    @patch("helper.commands.nixos.check_nixos")
    def test_not_nixos(self, mock_check):
        """Test when not running on NixOS."""
        mock_check.return_value = False

        result = get_nixos_version()
        assert result == "Not running NixOS"

    @patch("helper.commands.nixos.check_nixos")
    @patch("subprocess.run")
    def test_command_error(self, mock_subprocess, mock_check):
        """Test subprocess error."""
        mock_check.return_value = True
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "nixos-version")

        result = get_nixos_version()
        assert "Error getting NixOS version" in result


class TestNixosCommand:
    """Test cases for the nixos CLI command group.

    This class tests the NixOS-related commands and their help output,
    ensuring proper command structure and user guidance.
    """

    def test_command_help(self, cli_app):
        """Test command help output."""
        runner, cli = cli_app
        result = runner.invoke(cli, ["nix", "--help"])

        assert result.exit_code == 0
        assert "NixOS related commands" in result.output

    @patch("helper.commands.nixos.check_nixos")
    def test_version_subcommand(self, mock_check, cli_app):
        """Test version subcommand."""
        mock_check.return_value = True

        with patch("subprocess.run") as mock_subprocess:
            mock_result = MagicMock()
            mock_result.stdout = "21.11\n"
            mock_subprocess.return_value = mock_result

            runner, cli = cli_app
            result = runner.invoke(cli, ["nix", "version"])

            assert result.exit_code == 0
            assert "21.11" in result.output

    @patch("helper.commands.nixos.check_nixos")
    def test_search_subcommand(self, mock_check, cli_app):
        """Test search subcommand."""
        mock_check.return_value = True

        with patch("subprocess.run") as mock_subprocess:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "package-1.0\npackage-2.0\n"
            mock_subprocess.return_value = mock_result

            runner, cli = cli_app
            result = runner.invoke(cli, ["nix", "search", "package"])

            assert result.exit_code == 0
            assert "package-1.0" in result.output

    def test_search_no_package(self, cli_app):
        """Test search subcommand without package argument."""
        runner, cli = cli_app
        result = runner.invoke(cli, ["nix", "search"])

        assert result.exit_code == 0
        assert "Please specify a package to search for" in result.output

    @patch("helper.commands.nixos.check_nixos")
    def test_clean_not_nixos(self, mock_check, cli_app):
        """Test clean subcommand when not on NixOS."""
        mock_check.return_value = False

        runner, cli = cli_app
        result = runner.invoke(cli, ["nix", "clean"])

        assert result.exit_code == 0
        assert "This command can only be run on NixOS" in result.output

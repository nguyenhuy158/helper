"""Tests for venv command.

This module tests virtual environment management functionality including
environment detection, activation, deactivation, and command-line interface.
Tests cover various scenarios like missing environments and path resolution.
"""

from unittest.mock import patch

from helper.commands.venv import find_virtualenv, source_virtualenv, deactivate_virtualenv


class TestFindVirtualenv:
    """Test cases for the find_virtualenv function that locates virtual environments.

    This class tests the logic for finding virtual environment activation scripts
    by searching current and parent directories for common venv locations.
    """

    @patch("os.path.exists")
    @patch("os.getcwd")
    def test_find_in_current_dir(self, mock_cwd, mock_exists):
        """Test finding venv in current directory."""
        mock_cwd.return_value = "/current/dir"
        mock_exists.side_effect = lambda p: "venv/bin/activate" in p

        result = find_virtualenv()
        assert result == "/current/dir/venv/bin/activate"

    @patch("os.path.exists")
    @patch("os.getcwd")
    @patch("os.path.dirname")
    def test_find_in_parent_dir(self, mock_dirname, mock_cwd, mock_exists):
        """Test finding venv in parent directory."""
        mock_cwd.return_value = "/current/dir"
        mock_dirname.side_effect = lambda p: "/parent" if p == "/current/dir" else "/current/dir"
        mock_exists.side_effect = lambda p: "parent/venv/bin/activate" in p

        result = find_virtualenv()
        assert result == "/parent/venv/bin/activate"

    @patch("os.path.exists")
    @patch("os.getcwd")
    def test_no_venv_found(self, mock_cwd, mock_exists):
        """Test when no venv is found."""
        mock_cwd.return_value = "/current/dir"
        mock_exists.return_value = False

        result = find_virtualenv()
        assert result is None


class TestSourceVirtualenv:
    """Test cases for the source_virtualenv function that activates virtual environments.

    This class tests virtual environment activation, including path resolution,
    script validation, and error handling for missing or invalid environments.
    """

    @patch("helper.commands.venv.find_virtualenv")
    @patch("click.echo")
    @patch("os.path.abspath")
    def test_auto_find_venv(self, mock_abspath, mock_echo, mock_find):
        """Test sourcing venv with auto-detection."""
        mock_find.return_value = "/path/to/venv/bin/activate"
        mock_abspath.return_value = "/path/to/venv/bin/activate"

        source_virtualenv()

        mock_echo.assert_any_call('source "/path/to/venv/bin/activate"')

    @patch("helper.commands.venv.find_virtualenv")
    @patch("click.echo")
    @patch("sys.exit")
    def test_no_venv_found(self, mock_exit, mock_echo, mock_find):
        """Test when no venv is found."""
        mock_find.return_value = None

        source_virtualenv()

        mock_echo.assert_any_call(
            "Error: No virtual environment found in current or parent directories.", err=True
        )
        mock_exit.assert_called_once_with(1)

    @patch("os.path.isdir")
    @patch("os.path.exists")
    @patch("click.echo")
    @patch("os.path.abspath")
    def test_provided_path_directory(self, mock_abspath, mock_echo, mock_exists, mock_isdir):
        """Test sourcing venv with provided directory path."""
        mock_isdir.return_value = True
        mock_exists.return_value = True
        mock_abspath.return_value = "/custom/venv/bin/activate"

        source_virtualenv("/custom/venv")

        mock_echo.assert_any_call('source "/custom/venv/bin/activate"')


class TestDeactivateVirtualenv:
    """Test cases for the deactivate_virtualenv function that deactivates virtual environments.

    This class tests the deactivation process and output formatting for
    providing users with the command to deactivate their current environment.
    """

    @patch("click.echo")
    def test_deactivate(self, mock_echo):
        """Test deactivate command."""
        deactivate_virtualenv()

        mock_echo.assert_any_call("deactivate")
        mock_echo.assert_any_call("# Virtual environment deactivated", err=True)


class TestVenvCommand:
    """Test cases for the venv CLI command group.

    This class tests the virtual environment management commands and their
    help output, ensuring proper command structure and user guidance.
    """

    def test_command_help(self, cli_app):
        """Test command help output."""
        runner, cli = cli_app
        result = runner.invoke(cli, ["v", "--help"])

        assert result.exit_code == 0
        assert "Manage Python virtual environments" in result.output

    @patch("helper.commands.venv.source_virtualenv")
    def test_source_subcommand(self, mock_source, cli_app):
        """Test source subcommand."""
        runner, cli = cli_app
        result = runner.invoke(cli, ["v", "source"])

        assert result.exit_code == 0
        mock_source.assert_called_once_with(None)

    @patch("helper.commands.venv.deactivate_virtualenv")
    def test_deactivate_subcommand(self, mock_deactivate, cli_app):
        """Test deactivate subcommand."""
        runner, cli = cli_app
        result = runner.invoke(cli, ["v", "deactivate"])

        assert result.exit_code == 0
        mock_deactivate.assert_called_once()

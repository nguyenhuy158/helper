"""Tests for rsync command.

subprocess is mocked so rsync is never actually executed.
"""

import subprocess
from unittest.mock import patch


class TestRsyncCommand:
    """Test cases for the rsync CLI command."""

    def test_command_help(self, cli_app):
        """Test that the rsync command displays proper help information."""
        runner, cli = cli_app
        result = runner.invoke(cli, ["rsync", "--help"])

        assert result.exit_code == 0
        assert "Synchronize files using rsync" in result.output

    @patch("helper.commands.rsync.subprocess.run")
    def test_runs_rsync_with_common_options(self, mock_run, cli_app):
        """Test that the expected rsync command line is executed and echoed."""
        runner, cli = cli_app

        result = runner.invoke(cli, ["rsync", "/src", "user@host:/dst"])

        assert result.exit_code == 0
        mock_run.assert_called_once_with(
            ["rsync", "-havz", "--progress", "--inplace", "--partial", "/src", "user@host:/dst"],
            check=True,
        )
        assert "Executing: rsync -havz" in result.output

    @patch("helper.commands.rsync.subprocess.run")
    def test_missing_rsync_binary(self, mock_run, cli_app):
        """Test exit code 1 and message when rsync is not installed."""
        mock_run.side_effect = FileNotFoundError
        runner, cli = cli_app

        result = runner.invoke(cli, ["rsync", "/src", "/dst"])

        assert result.exit_code == 1
        assert "rsync command not found" in result.output

    @patch("helper.commands.rsync.subprocess.run")
    def test_propagates_rsync_exit_code(self, mock_run, cli_app):
        """Test that a failing rsync propagates its return code."""
        mock_run.side_effect = subprocess.CalledProcessError(23, "rsync")
        runner, cli = cli_app

        result = runner.invoke(cli, ["rsync", "/src", "/dst"])

        assert result.exit_code == 23
        assert "rsync failed with return code 23" in result.output

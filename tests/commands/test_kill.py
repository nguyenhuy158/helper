"""Tests for kill command.

Covers the port and process-name code paths with subprocess and psutil
mocked so no real process is ever touched.
"""

from unittest.mock import MagicMock, patch


class TestKillCommand:
    """Test cases for the kill CLI command."""

    def test_command_help(self, cli_app):
        """Test that the kill command displays proper help information."""
        runner, cli = cli_app
        result = runner.invoke(cli, ["kill", "--help"])

        assert result.exit_code == 0
        assert "Kill processes by name or port" in result.output

    def test_no_target_shows_help(self, cli_app):
        """Test that running without a target prints usage instead of failing."""
        runner, cli = cli_app
        result = runner.invoke(cli, ["kill"])

        assert result.exit_code == 0
        assert "Usage:" in result.output

    @patch("helper.commands.kill.subprocess.run")
    def test_port_without_listener(self, mock_run, cli_app):
        """Test the message when no process listens on the given port."""
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        runner, cli = cli_app

        result = runner.invoke(cli, ["kill", "8000"])

        assert result.exit_code == 0
        assert "No process found listening on port 8000" in result.output
        mock_run.assert_called_once_with(
            ["lsof", "-i", ":8000", "-t"], capture_output=True, text=True, check=False
        )

    @patch("helper.commands.kill.psutil.process_iter")
    def test_name_without_match(self, mock_iter, cli_app):
        """Test the message when no process name matches."""
        mock_iter.return_value = []
        runner, cli = cli_app

        result = runner.invoke(cli, ["kill", "definitely-not-running"])

        assert result.exit_code == 0
        assert "No process found with name containing" in result.output

    @patch("helper.commands.kill.psutil.process_iter")
    def test_name_match_kills_process(self, mock_iter, cli_app):
        """Test that a matching process is killed and reported."""
        proc = MagicMock()
        proc.info = {"pid": 4242, "name": "myapp"}
        mock_iter.return_value = [proc]
        runner, cli = cli_app

        result = runner.invoke(cli, ["kill", "myapp"])

        assert result.exit_code == 0
        proc.kill.assert_called_once()
        assert "myapp (PID: 4242)" in result.output

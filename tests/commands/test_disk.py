"""Tests for disk command.

Covers the pure parsing/formatting helpers and the CLI subcommands with
shell execution mocked.
"""

from unittest.mock import patch

from helper.commands.disk import get_usage, parse_windows_disk_info


class TestParseWindowsDiskInfo:
    """Test cases for the parse_windows_disk_info function."""

    def test_parses_valid_wmic_output(self):
        """Test that a wmic line is parsed into aligned columns."""
        output = "Caption  FreeSpace     Size\nC:       53687091200   107374182400"

        result = parse_windows_disk_info(output)

        assert len(result) == 2  # header + one drive
        assert result[1].startswith("C:")
        assert "50.0%" in result[1]

    def test_skips_malformed_lines(self):
        """Test that lines without numeric sizes are skipped."""
        output = "Caption  FreeSpace  Size\nX:       not-a-number"

        result = parse_windows_disk_info(output)

        assert len(result) == 1  # header only


class TestGetUsage:
    """Test cases for the get_usage function."""

    @patch("helper.commands.disk.run_command")
    @patch("helper.commands.disk.platform.system")
    def test_unix_uses_df(
        self,
        mock_system,
        mock_run,
    ):
        """Test that df -h is used on Linux/macOS."""
        mock_system.return_value = "Darwin"
        mock_run.return_value = "Filesystem Size Used"

        assert get_usage() == "Filesystem Size Used"
        mock_run.assert_called_once_with("df -h")

    @patch("helper.commands.disk.platform.system")
    def test_unsupported_os(self, mock_system):
        """Test the message for unsupported platforms."""
        mock_system.return_value = "Plan9"

        assert get_usage() == "Unsupported operating system"


class TestDiskCommand:
    """Test cases for the disk CLI command group."""

    def test_command_help(self, cli_app):
        """Test that the disk group lists its subcommands."""
        runner, cli = cli_app
        result = runner.invoke(cli, ["disk", "--help"])

        assert result.exit_code == 0
        for sub in ("usage", "mount", "list"):
            assert sub in result.output

    @patch("helper.commands.disk.get_usage")
    def test_usage_subcommand(self, mock_get_usage, cli_app):
        """Test that disk usage prints the usage panel."""
        mock_get_usage.return_value = "FAKE-DF-OUTPUT"
        runner, cli = cli_app

        result = runner.invoke(cli, ["disk", "usage"])

        assert result.exit_code == 0
        assert "FAKE-DF-OUTPUT" in result.output
        assert "Disk Usage" in result.output

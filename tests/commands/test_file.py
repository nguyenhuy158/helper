"""Tests for file command group registration and help."""


class TestFileCommand:
    """Test cases for the file CLI command group."""

    def test_command_help(self, cli_app):
        """Test that the f group displays proper help information."""
        runner, cli = cli_app
        result = runner.invoke(cli, ["f", "--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.output

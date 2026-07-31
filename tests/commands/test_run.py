"""Tests for run (snippets) command.

Snippet storage and subprocess are mocked so no file or shell command
is touched.
"""

from unittest.mock import patch


class TestRunCommand:
    """Test cases for the run CLI command group."""

    def test_command_help(self, cli_app):
        """Test that the run group displays proper help information."""
        runner, cli = cli_app
        result = runner.invoke(cli, ["run", "--help"])

        assert result.exit_code == 0
        assert "Run predefined command snippets" in result.output

    @patch("helper.commands.run.list_snippets")
    def test_list_empty(self, mock_list, cli_app):
        """Test the hint shown when no snippets are defined."""
        mock_list.return_value = []
        runner, cli = cli_app

        result = runner.invoke(cli, ["run", "list"])

        assert result.exit_code == 0
        assert "No snippets defined" in result.output

    @patch("helper.commands.run.list_snippets")
    def test_list_shows_numbered_snippets(self, mock_list, cli_app):
        """Test that snippets are listed with 1-based indexes."""
        mock_list.return_value = ["deploy", "backup"]
        runner, cli = cli_app

        result = runner.invoke(cli, ["run", "list"])

        assert result.exit_code == 0
        assert "1. deploy" in result.output
        assert "2. backup" in result.output

    @patch("helper.commands.run.load_snippets")
    def test_exec_unknown_snippet(self, mock_load, cli_app):
        """Test the error for a snippet that doesn't exist."""
        mock_load.return_value = {"deploy": "echo deploy"}
        runner, cli = cli_app

        result = runner.invoke(cli, ["run", "exec", "nope"])

        assert result.exit_code == 0
        assert "not found" in result.output

    @patch("helper.commands.run.subprocess.run")
    @patch("helper.commands.run.get_snippet_command")
    @patch("helper.commands.run.load_snippets")
    def test_exec_by_index_with_force(self, mock_load, mock_get, mock_run, cli_app):
        """Test that index 1 resolves to the first snippet and runs it."""
        mock_load.return_value = {"deploy": "echo deploy"}
        mock_get.return_value = "echo deploy"
        runner, cli = cli_app

        result = runner.invoke(cli, ["run", "exec", "--force", "1"])

        assert result.exit_code == 0
        mock_get.assert_called_once_with("deploy")
        mock_run.assert_called_once_with("echo deploy", shell=True, check=True)

    @patch("helper.commands.run.add_snippet")
    def test_add_converts_legacy_placeholders(self, mock_add, cli_app):
        """Test that {container}/{db_container} become env-style placeholders."""
        runner, cli = cli_app

        result = runner.invoke(
            cli, ["run", "add", "shell", "docker exec {container} psql {db_container}"]
        )

        assert result.exit_code == 0
        mock_add.assert_called_once_with(
            "shell", "docker exec {ODOO_CONTAINER} psql {ODOO_DB_CONTAINER}"
        )

"""Tests for odoo scripts command.

This module contains tests for the odoo command functionality,
including unit tests for listing/downloading scripts from GitHub
and integration tests for the interactive CLI flow.
"""

import json
from unittest.mock import patch

from helper.commands.odoo_scripts import download_script, get_catalog, list_scripts

SAMPLE_ENTRIES = [
    {"type": "file", "name": "list_users.py", "url": "https://api/x1", "size": 300},
    {"type": "file", "name": "record_counts.py", "url": "https://api/x2", "size": 500},
    {"type": "file", "name": "README.md", "url": "https://api/x3", "size": 100},
    {"type": "dir", "name": "sub.py", "url": "https://api/x4", "size": 0},
]


class TestListScripts:
    """Test cases for the list_scripts function."""

    @patch("helper.commands.odoo_scripts._request")
    def test_filters_python_files_only(self, mock_request):
        """Test that only .py files (not dirs or other files) are returned."""
        mock_request.return_value = json.dumps(SAMPLE_ENTRIES).encode()

        result = list_scripts()

        assert [s["name"] for s in result] == ["list_users.py", "record_counts.py"]


class TestDownloadScript:
    """Test cases for the download_script function."""

    @patch("helper.commands.odoo_scripts._request")
    def test_writes_file_to_dest_dir(self, mock_request, tmp_path):
        """Test that the script content is written to the destination directory."""
        mock_request.return_value = b"print('hi')"
        script = {"name": "list_users.py", "url": "https://api/x1"}

        dest = download_script(script, dest_dir=str(tmp_path))

        assert dest == str(tmp_path / "list_users.py")
        assert (tmp_path / "list_users.py").read_bytes() == b"print('hi')"
        mock_request.assert_called_once_with("https://api/x1", raw=True)


SAMPLE_CATALOG = {
    "list_users.py": {
        "category": "users",
        "description": "List active users",
        "output": "table: login | name | email",
    },
    "record_counts.py": {
        "category": "db",
        "description": "Count records of common models",
        "output": "table: model | count",
    },
}


class TestGetCatalog:
    """Test cases for the get_catalog function."""

    @patch("helper.commands.odoo_scripts._request")
    def test_returns_parsed_catalog(self, mock_request):
        """Test that catalog.json content is parsed into a dict."""
        mock_request.return_value = json.dumps(SAMPLE_CATALOG).encode()

        assert get_catalog() == SAMPLE_CATALOG

    @patch("helper.commands.odoo_scripts._request")
    def test_returns_empty_dict_on_error(self, mock_request):
        """Test that a missing/unreadable catalog degrades to an empty dict."""
        mock_request.side_effect = ValueError("bad json")

        assert get_catalog() == {}


@patch("helper.commands.odoo_scripts.get_catalog", return_value=SAMPLE_CATALOG)
class TestOdooCommand:
    """Test cases for the odoo CLI command."""

    def test_command_help(self, mock_catalog, cli_app):
        """Test that the odoo command displays proper help information."""
        runner, cli = cli_app
        result = runner.invoke(cli, ["odoo", "--help"])

        assert result.exit_code == 0
        assert "Browse and download click-odoo scripts" in result.output

    @patch("helper.commands.odoo_scripts.download_script")
    @patch("helper.commands.odoo_scripts.list_scripts")
    def test_interactive_selection_downloads(self, mock_list, mock_download, mock_catalog, cli_app):
        """Test that picking a number from the menu downloads that script."""
        mock_list.return_value = [
            {"name": "list_users.py", "url": "https://api/x1", "size": 300},
            {"name": "record_counts.py", "url": "https://api/x2", "size": 500},
        ]
        mock_download.return_value = "./record_counts.py"
        runner, cli = cli_app

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["odoo"], input="2\n\n")

        assert result.exit_code == 0
        mock_download.assert_called_once()
        assert mock_download.call_args[0][0]["name"] == "record_counts.py"
        assert mock_download.call_args[1]["dest_dir"] == "."
        assert "click-odoo" in result.output

    @patch("helper.commands.odoo_scripts.download_script")
    @patch("helper.commands.odoo_scripts.list_scripts")
    def test_save_to_custom_directory(self, mock_list, mock_download, mock_catalog, cli_app):
        """Test that answering the directory prompt saves into that directory."""
        mock_list.return_value = [{"name": "list_users.py", "url": "u", "size": 1}]
        mock_download.return_value = "sub/list_users.py"
        runner, cli = cli_app

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["odoo"], input="1\nsub\n")

        assert result.exit_code == 0
        assert mock_download.call_args[1]["dest_dir"] == "sub"

    @patch("helper.commands.odoo_scripts.download_script")
    @patch("helper.commands.odoo_scripts.list_scripts")
    def test_dir_option_skips_prompt(self, mock_list, mock_download, mock_catalog, cli_app):
        """Test that --dir saves there without prompting for a directory."""
        mock_list.return_value = [{"name": "list_users.py", "url": "u", "size": 1}]
        mock_download.return_value = "sub/list_users.py"
        runner, cli = cli_app

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["odoo", "list_users", "--dir", "sub"])

        assert result.exit_code == 0
        assert "Save to directory" not in result.output
        assert mock_download.call_args[1]["dest_dir"] == "sub"

    @patch("helper.commands.odoo_scripts.list_scripts")
    def test_cancel_selection(self, mock_list, mock_catalog, cli_app):
        """Test that entering 0 cancels without downloading."""
        mock_list.return_value = [{"name": "list_users.py", "url": "u", "size": 1}]
        runner, cli = cli_app

        result = runner.invoke(cli, ["odoo"], input="0\n")

        assert result.exit_code == 0

    @patch("helper.commands.odoo_scripts.download_script")
    @patch("helper.commands.odoo_scripts.list_scripts")
    def test_direct_name_download(self, mock_list, mock_download, mock_catalog, cli_app):
        """Test that passing a name (without .py) downloads directly, no menu."""
        mock_list.return_value = [{"name": "list_users.py", "url": "u", "size": 1}]
        mock_download.return_value = "./list_users.py"
        runner, cli = cli_app

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["odoo", "list_users"], input="\n")

        assert result.exit_code == 0
        mock_download.assert_called_once()

    @patch("helper.commands.odoo_scripts.list_scripts")
    def test_unknown_name_fails(self, mock_list, mock_catalog, cli_app):
        """Test that a term matching nothing exits with an error."""
        mock_list.return_value = [{"name": "list_users.py", "url": "u", "size": 1}]
        runner, cli = cli_app

        result = runner.invoke(cli, ["odoo", "nope"])

        assert result.exit_code == 1
        assert "No script matches 'nope'" in result.output

    @patch("helper.commands.odoo_scripts.download_script")
    @patch("helper.commands.odoo_scripts.list_scripts")
    def test_search_filters_menu_by_category(self, mock_list, mock_download, mock_catalog, cli_app):
        """Test that --search matches catalog category and narrows the menu."""
        mock_list.return_value = [
            {"name": "list_users.py", "url": "u1", "size": 300},
            {"name": "record_counts.py", "url": "u2", "size": 500},
        ]
        mock_download.return_value = "./record_counts.py"
        runner, cli = cli_app

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["odoo", "--search", "db"], input="1\n\n")

        assert result.exit_code == 0
        assert "list_users.py" not in result.output
        assert mock_download.call_args[0][0]["name"] == "record_counts.py"

    @patch("helper.commands.odoo_scripts.list_scripts")
    def test_menu_shows_category_and_description(self, mock_list, mock_catalog, cli_app):
        """Test that the menu table includes catalog category and description."""
        mock_list.return_value = [{"name": "list_users.py", "url": "u", "size": 1}]
        runner, cli = cli_app

        result = runner.invoke(cli, ["odoo"], input="0\n")

        assert result.exit_code == 0
        assert "users" in result.output
        assert "List active users" in result.output

    @patch("helper.commands.odoo_scripts.download_script")
    @patch("helper.commands.odoo_scripts.list_scripts")
    def test_output_example_printed_after_download(
        self, mock_list, mock_download, mock_catalog, cli_app
    ):
        """Test that the catalog output example is printed after download."""
        mock_list.return_value = [{"name": "list_users.py", "url": "u", "size": 1}]
        mock_download.return_value = "./list_users.py"
        runner, cli = cli_app

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["odoo", "list_users"], input="\n")

        assert result.exit_code == 0
        assert "table: login | name | email" in result.output

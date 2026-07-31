"""Tests for docker command group registration and help."""

from helper.commands.docker.urls import _parse_port_string


class TestParsePortString:
    """Test cases for the _parse_port_string helper."""

    def test_port_with_protocol(self):
        assert _parse_port_string("8069/tcp") == ("8069", "tcp")

    def test_mapped_port(self):
        assert _parse_port_string("0.0.0.0:8080->80/tcp") == ("80", "tcp")

    def test_bare_port(self):
        assert _parse_port_string("5432") == ("5432", "tcp")


class TestDockerCommand:
    """Test cases for the d (docker) CLI command group."""

    def test_command_help(self, cli_app):
        """Test that the d group displays proper help information."""
        runner, cli = cli_app
        result = runner.invoke(cli, ["d", "--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_lazy_group_resolves(self, cli_app):
        """Test that the lazily loaded docker group is a real click group."""
        import click

        runner, cli = cli_app
        ctx = click.Context(cli)

        cmd = cli.get_command(ctx, "d")

        assert cmd is not None
        assert isinstance(cmd, click.Group)

    def test_url_subcommand_registered(self, cli_app):
        """Test that the url subcommand exists (was lost to misplaced decorators)."""
        import click

        runner, cli = cli_app
        ctx = click.Context(cli)

        docker_group = cli.get_command(ctx, "d")

        assert "url" in docker_group.commands
        assert "-parse-port-string" not in docker_group.commands
        assert set(docker_group.commands) >= {"ps", "run", "rm", "rmi", "url", "clean", "disk-used"}

    def test_ui_subcommand_registered(self, cli_app):
        """Test that the dashboard ui subcommand exists on the group."""
        import click

        runner, cli = cli_app
        ctx = click.Context(cli)

        docker_group = cli.get_command(ctx, "d")

        assert "ui" in docker_group.commands

    def test_group_invokes_without_subcommand(self, cli_app):
        """Bare `h d` must not error out with 'Missing command'."""
        import click

        runner, cli = cli_app
        ctx = click.Context(cli)

        docker_group = cli.get_command(ctx, "d")

        assert docker_group.invoke_without_command is True

    def test_dashboard_import_is_lazy(self):
        """Importing the docker package must not import textual."""
        import sys

        import helper.commands.docker  # noqa: F401

        assert "helper.commands.docker.dashboard" not in sys.modules

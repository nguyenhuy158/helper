"""Tests for the loguru-based logging setup."""

import subprocess

from helper.log import set_level


class TestSubprocessTracing:
    def test_vvv_traces_spawned_commands(self, capfd):
        """At verbosity >= 3 every subprocess command is logged to stderr."""
        set_level(3)
        try:
            subprocess.run(["echo", "hello"], capture_output=True)
            err = capfd.readouterr().err
            assert "$ echo hello" in err
        finally:
            set_level(0)

    def test_quiet_below_debug(self, capfd):
        """Below -vvv the trace stays silent even if the patch is active."""
        set_level(3)
        set_level(0)
        subprocess.run(["echo", "hello"], capture_output=True)
        err = capfd.readouterr().err
        assert "$ echo hello" not in err

    def test_shell_string_command_logged_verbatim(self, capfd):
        """shell=True string commands are logged as-is."""
        set_level(3)
        try:
            subprocess.run("echo hello", shell=True, capture_output=True)
            err = capfd.readouterr().err
            assert "$ echo hello" in err
        finally:
            set_level(0)

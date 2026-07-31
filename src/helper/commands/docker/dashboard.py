"""Full-screen interactive Docker dashboard (lazydocker-style) built on Textual.

Launched by `h d` (no subcommand) or `h d ui`. Requires the optional
`textual` dependency: install with `pip install 'helper-cli[tui]'`.
"""

import json
import subprocess

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    RichLog,
    TabbedContent,
    TabPane,
)

REFRESH_SECONDS = 3.0
LOG_TAIL = 200


def _docker_json_lines(args):
    """Run a docker listing command with `--format {{json .}}` and parse each line."""
    result = subprocess.run(
        ["docker", *args, "--format", "{{json .}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "docker command failed")
    return [json.loads(line) for line in result.stdout.splitlines() if line.strip()]


class ConfirmScreen(ModalScreen[bool]):
    """Modal yes/no confirmation dialog."""

    BINDINGS = [
        Binding("y", "confirm", "Yes"),
        Binding("n", "cancel", "No"),
        Binding("escape", "cancel", "No", show=False),
    ]

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Label(self.message, id="confirm-message")
            with Horizontal(id="confirm-buttons"):
                yield Button("Yes (y)", variant="error", id="yes")
                yield Button("No (n)", variant="primary", id="no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)


class DockerDashboard(App):
    """Interactive dashboard for Docker containers and images."""

    TITLE = "helper — docker dashboard"

    CSS = """
    #containers-table { width: 3fr; }
    #logs { width: 2fr; border-left: heavy $accent; padding: 0 1; }
    ConfirmScreen { align: center middle; }
    #confirm-dialog {
        width: 64;
        height: auto;
        border: thick $error;
        background: $surface;
        padding: 1 2;
    }
    #confirm-message { width: 100%; content-align: center middle; }
    #confirm-buttons { height: auto; align-horizontal: center; }
    #confirm-buttons Button { margin: 1 2 0 2; }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("a", "toggle_all", "All/Running"),
        Binding("s", "start_stop", "Start/Stop"),
        Binding("t", "restart", "Restart"),
        Binding("x", "remove", "Remove"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.show_all = False
        self._containers = []
        self._images = []
        self._logs_for = None

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="tab-containers"):
            with TabPane("Containers", id="tab-containers"), Horizontal():
                yield DataTable(id="containers-table")
                yield RichLog(id="logs", wrap=False, highlight=False)
            with TabPane("Images", id="tab-images"):
                yield DataTable(id="images-table")
        yield Footer()

    def on_mount(self) -> None:
        containers = self.query_one("#containers-table", DataTable)
        containers.cursor_type = "row"
        containers.add_columns("ID", "Name", "Image", "State", "Status", "Ports")

        images = self.query_one("#images-table", DataTable)
        images.cursor_type = "row"
        images.add_columns("Repository", "Tag", "ID", "Size", "Created")

        self.refresh_data()
        self.set_interval(REFRESH_SECONDS, self.refresh_containers)

    # ------------------------------------------------------------------ data

    def refresh_data(self) -> None:
        self.refresh_containers()
        self.refresh_images()

    def refresh_containers(self) -> None:
        args = ["ps", "-a"] if self.show_all else ["ps"]
        try:
            data = _docker_json_lines(args)
        except (RuntimeError, json.JSONDecodeError) as exc:
            self.notify(str(exc), title="docker ps", severity="error")
            return

        table = self.query_one("#containers-table", DataTable)
        prev_id = self._selected_container_id()
        table.clear()
        self._containers = data
        for c in data:
            state = c.get("State") or ("running" if c.get("Status", "").startswith("Up") else "")
            table.add_row(
                c.get("ID", "")[:12],
                c.get("Names", ""),
                c.get("Image", ""),
                state,
                c.get("Status", ""),
                c.get("Ports", ""),
            )
        if prev_id:
            for i, c in enumerate(data):
                if c.get("ID") == prev_id:
                    table.move_cursor(row=i)
                    break
        self.sub_title = "all containers" if self.show_all else "running containers"

    def refresh_images(self) -> None:
        try:
            data = _docker_json_lines(["images"])
        except (RuntimeError, json.JSONDecodeError) as exc:
            self.notify(str(exc), title="docker images", severity="error")
            return

        table = self.query_one("#images-table", DataTable)
        table.clear()
        self._images = data
        for img in data:
            table.add_row(
                img.get("Repository", ""),
                img.get("Tag", ""),
                img.get("ID", "")[:12],
                img.get("Size", ""),
                img.get("CreatedSince", ""),
            )

    # ------------------------------------------------------------- selection

    def _selected_container(self):
        table = self.query_one("#containers-table", DataTable)
        row = table.cursor_row
        if row is None or not (0 <= row < len(self._containers)):
            return None
        return self._containers[row]

    def _selected_container_id(self):
        container = self._selected_container()
        return container.get("ID") if container else None

    def _selected_image(self):
        table = self.query_one("#images-table", DataTable)
        row = table.cursor_row
        if row is None or not (0 <= row < len(self._images)):
            return None
        return self._images[row]

    def _containers_tab_active(self) -> bool:
        return self.query_one(TabbedContent).active == "tab-containers"

    # ------------------------------------------------------------------ logs

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id != "containers-table":
            return
        container = self._selected_container()
        if container is None:
            return
        cid = container.get("ID", "")
        if cid == self._logs_for:
            return
        self._logs_for = cid
        self.run_worker(
            lambda: self._load_logs(cid),
            thread=True,
            exclusive=True,
            group="logs",
        )

    def _load_logs(self, cid: str) -> None:
        result = subprocess.run(
            ["docker", "logs", "--tail", str(LOG_TAIL), cid],
            capture_output=True,
            text=True,
            check=False,
        )
        text = (result.stdout + result.stderr) or "(no logs)"
        self.call_from_thread(self._show_logs, cid, text)

    def _show_logs(self, cid: str, text: str) -> None:
        if cid != self._logs_for:
            return
        log = self.query_one("#logs", RichLog)
        log.clear()
        log.write(text)

    # --------------------------------------------------------------- actions

    def action_refresh(self) -> None:
        self.refresh_data()

    def action_toggle_all(self) -> None:
        self.show_all = not self.show_all
        self.refresh_containers()

    def action_start_stop(self) -> None:
        container = self._selected_container()
        if container is None:
            return
        name = container.get("Names") or container.get("ID", "")
        running = container.get("Status", "").startswith("Up")
        verb = "stop" if running else "start"
        self._docker_action([verb, name], f"{verb} {name}")

    def action_restart(self) -> None:
        container = self._selected_container()
        if container is None:
            return
        name = container.get("Names") or container.get("ID", "")
        self._docker_action(["restart", name], f"restart {name}")

    def action_remove(self) -> None:
        if self._containers_tab_active():
            container = self._selected_container()
            if container is None:
                return
            name = container.get("Names") or container.get("ID", "")
            message = f"Remove container '{name}'? (docker rm -f)"
            args = ["rm", "-f", name]
        else:
            image = self._selected_image()
            if image is None:
                return
            name = f"{image.get('Repository', '')}:{image.get('Tag', '')}"
            message = f"Remove image '{name}'? (docker rmi)"
            args = ["rmi", image.get("ID", "")]

        def on_confirm(confirmed) -> None:
            if confirmed:
                self._docker_action(args, f"remove {name}")

        self.push_screen(ConfirmScreen(message), on_confirm)

    def _docker_action(self, args, label: str) -> None:
        self.notify(f"Running: docker {' '.join(args)}", title=label, timeout=2)
        self.run_worker(
            lambda: self._exec_and_refresh(args, label),
            thread=True,
            group="docker-action",
        )

    def _exec_and_refresh(self, args, label: str) -> None:
        result = subprocess.run(
            ["docker", *args], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            self.call_from_thread(self.notify, f"OK: {label}", timeout=3)
        else:
            self.call_from_thread(
                self.notify,
                result.stderr.strip() or "docker command failed",
                title=label,
                severity="error",
            )
        self.call_from_thread(self.refresh_data)

"""Textual picker for odoo-scripts: live filter, code preview, Enter to select.

Used by `h odoo` when the optional `textual` dependency is installed and the
session is interactive; otherwise the command falls back to the plain
numbered menu. Import this module lazily — never at package import time.
"""

from rich.syntax import Syntax
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import DataTable, Footer, Header, Input, RichLog

from ..gh import fetch as _request


def _fmt_size(size: int) -> str:
    return f"{size} B" if size < 1024 else f"{size / 1024:.1f} KB"


class ScriptPicker(App):
    """Full-screen script browser; exits with the chosen script dict or None."""

    TITLE = "helper — odoo scripts"

    CSS = """
    #search { dock: top; }
    #scripts-table { width: 3fr; }
    #preview { width: 2fr; border-left: heavy $accent; padding: 0 1; }
    """

    BINDINGS = [
        Binding("escape", "cancel_or_blur", "Cancel"),
        Binding("q", "cancel", "Quit", show=False),
        Binding("slash", "focus_search", "Search", key_display="/"),
        Binding("enter", "pick", "Download", show=True),
    ]

    def __init__(self, scripts, catalog, initial_filter: str = "") -> None:
        super().__init__()
        self._all = scripts
        self._catalog = catalog
        self._initial = initial_filter
        self._visible = []
        self._preview_cache = {}
        self._preview_for = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(
            value=self._initial,
            placeholder="Type to filter — Enter to jump to the list",
            id="search",
        )
        with Horizontal():
            yield DataTable(id="scripts-table")
            yield RichLog(id="preview", wrap=False, highlight=False)
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#scripts-table", DataTable)
        table.cursor_type = "row"
        table.add_columns("Name", "Catg", "Description", "Size")
        self._refilter(self._initial)
        table.focus()

    # ----------------------------------------------------------- filtering

    def _refilter(self, term: str) -> None:
        term = term.lower().strip()
        table = self.query_one("#scripts-table", DataTable)
        table.clear()
        self._visible = []
        for script in self._all:
            meta = self._catalog.get(script["name"], {})
            haystack = " ".join(
                [script["name"], meta.get("category", ""), meta.get("description", "")]
            ).lower()
            if term and term not in haystack:
                continue
            self._visible.append(script)
            table.add_row(
                script["name"],
                meta.get("category", "-"),
                meta.get("description", "-"),
                _fmt_size(script.get("size", 0)),
            )
        self.sub_title = f"{len(self._visible)}/{len(self._all)} scripts"

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search":
            self._refilter(event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.query_one("#scripts-table", DataTable).focus()

    # ----------------------------------------------------------- selection

    def _selected(self):
        table = self.query_one("#scripts-table", DataTable)
        row = table.cursor_row
        if row is None or not (0 <= row < len(self._visible)):
            return None
        return self._visible[row]

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        script = self._selected()
        if script is not None:
            self.exit(script)

    def action_pick(self) -> None:
        script = self._selected()
        if script is not None:
            self.exit(script)

    def action_focus_search(self) -> None:
        self.query_one("#search", Input).focus()

    def action_cancel(self) -> None:
        self.exit(None)

    def action_cancel_or_blur(self) -> None:
        search = self.query_one("#search", Input)
        if search.has_focus:
            self.query_one("#scripts-table", DataTable).focus()
        else:
            self.exit(None)

    # ------------------------------------------------------------- preview

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        script = self._selected()
        if script is None:
            return
        name = script["name"]
        if name == self._preview_for:
            return
        self._preview_for = name
        cached = self._preview_cache.get(name)
        if cached is not None:
            self._show_preview(name, cached)
            return
        self.run_worker(
            lambda: self._fetch_preview(script),
            thread=True,
            exclusive=True,
            group="preview",
        )

    def _fetch_preview(self, script) -> None:
        try:
            content = _request(script["url"], raw=True).decode("utf-8", errors="replace")
        except Exception as exc:  # network/API errors → show in the pane, don't crash
            content = f"# preview unavailable: {exc}"
        self._preview_cache[script["name"]] = content
        self.call_from_thread(self._show_preview, script["name"], content)

    def _show_preview(self, name: str, content: str) -> None:
        if name != self._preview_for:
            return
        log = self.query_one("#preview", RichLog)
        log.clear()
        log.write(Syntax(content, "python", line_numbers=True))

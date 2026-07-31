"""Shared rich-formatted help rendering for helper CLI groups.

Every click group in helper renders the same styled help screen — a bold
usage line, a one-line description, a magenta commands table and a compact
options footer — so `helper --help` and `helper <group> --help` look alike.
"""

import click
from rich.console import Console
from rich.markup import escape
from rich.table import Table

SHORT_HELP_WIDTH = 70


def _options_footer(ctx, group, extra_options=()):
    """Build the one-line options footer, e.g. `Options: -h help   |   ...`."""
    bits = []
    for param in group.get_params(ctx):
        if not isinstance(param, click.Option) or param.hidden:
            continue
        flag = min(param.opts + list(param.secondary_opts), key=len)
        bits.append(f"[bold]{escape(flag)}[/bold] {param.name}")
    bits.extend(extra_options)
    return (
        "[dim]Options:[/dim] "
        + "  ".join(bits)
        + f"   [dim]|   {ctx.command_path} <command> --help for details[/dim]"
    )


def _commands_table(ctx, group, categories=None):
    """Build the commands table; with categories a leading category column."""
    table = Table(border_style="magenta", show_header=False, pad_edge=False, box=None)
    if categories:
        table.add_column("Category", style="yellow", no_wrap=True)
    table.add_column("Command", style="bold cyan", no_wrap=True)
    table.add_column("Description", style="")

    def row(cmd_name, cmd, category=None):
        cells = [cmd_name, cmd.get_short_help_str(SHORT_HELP_WIDTH)]
        if categories:
            cells.insert(0, category or "")
        table.add_row(*cells)

    listed = set()
    for category, names in (categories or {}).items():
        for j, cmd_name in enumerate(names):
            cmd = group.get_command(ctx, cmd_name)
            if cmd is None or cmd.hidden:
                continue
            listed.add(cmd_name)
            row(cmd_name, cmd, f"─ {category}" if j == 0 else "")
        table.add_section()

    leftovers = [n for n in group.list_commands(ctx) if n not in listed]
    for j, cmd_name in enumerate(leftovers):
        cmd = group.get_command(ctx, cmd_name)
        if cmd is None or cmd.hidden:
            continue
        row(cmd_name, cmd, "─ Other" if j == 0 else "")
    return table


def render_group_help(
    ctx, formatter, *, categories=None, intro=None, show_description=True, extra_options=()
):
    """Render the shared help screen for a click group into `formatter`.

    categories: optional {category: [command names]} mapping; commands not
    listed there fall under "Other". Without it the table is flat.
    intro: optional rich renderable printed above the usage line.
    extra_options: extra pre-formatted entries for the options footer, for
    flags handled outside click's parser (e.g. the global -v).
    """
    group = ctx.command
    console = Console()
    with console.capture() as capture:
        if intro is not None:
            console.print(intro)
        usage = " ".join(group.collect_usage_pieces(ctx))
        console.print(f"[bold]Usage:[/bold] {ctx.command_path} [dim]{escape(usage)}[/dim]")
        if show_description:
            description = (group.help or "").strip().split("\n\n")[0]
            if description:
                console.print(escape(description))
        console.print(_commands_table(ctx, group, categories))
        console.print(_options_footer(ctx, group, extra_options))
    formatter.write(capture.get())


class RichHelpGroup(click.Group):
    """Click group whose --help uses the shared rich help screen."""

    def format_help(self, ctx, formatter):
        render_group_help(ctx, formatter)

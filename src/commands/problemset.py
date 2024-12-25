"""
Problemset-related commands.
"""

from typing import Optional

import click
from rich.box import ROUNDED
from rich.console import Console
from rich.table import Table

from ..context import Context

console = Console()


@click.group()
def problemset():
    """Manage and interact with problemsets."""
    pass


@problemset.command()
@click.pass_obj
def list(ctx: Context):
    """List problemsets you have joined."""
    try:
        problemsets = ctx.api_client.get_user_problemsets()
        if not problemsets:
            console.print("[yellow]No problemsets found.[/yellow]")
            return

        # Sort problemsets by ID in ascending order
        problemsets = sorted(problemsets, key=lambda ps: ps.id)

        table = Table(
            title="Your Problemsets",
            title_style="bold blue",
            box=ROUNDED,
            header_style="bold cyan",
            show_lines=True,
            padding=(0, 1),
        )

        table.add_column("ID", justify="center", style="cyan", no_wrap=True)
        table.add_column("Name", style="green")
        table.add_column("Type", style="magenta")
        table.add_column("Start Time", style="yellow")
        table.add_column("End Time", style="yellow")

        for ps in problemsets:
            table.add_row(
                str(ps.id),
                ps.name,
                ps.type.value,
                str(ps.start_time),
                str(ps.end_time),
            )

        console.print()
        console.print(table)
        console.print()
    except Exception as e:
        console.print(f"[red]Failed to fetch problemsets: {str(e)}[/red]")


@problemset.command()
@click.argument("problemset_id", type=int)
@click.pass_obj
def show(ctx: Context, problemset_id: int):
    """Show details of a specific problemset."""
    try:
        ps = ctx.api_client.get_problemset(problemset_id)

        # Create a rich table for problemset info
        table = Table(
            title=f"Problemset: {ps.name}",
            title_style="bold blue",
            box=ROUNDED,
            header_style="bold cyan",
            show_lines=True,
            padding=(0, 1),
        )

        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        table.add_row("ID", str(ps.id))
        table.add_row("Name", ps.name)
        table.add_row("Description", ps.description or "N/A")
        table.add_row("Type", ps.type.value)
        table.add_row("Start Time", str(ps.start_time))
        table.add_row("End Time", str(ps.end_time))
        table.add_row(
            "Late Submission",
            (
                str(ps.late_submission_deadline)
                if ps.late_submission_deadline
                else "Not Allowed"
            ),
        )

        # Add allowed languages
        langs = (
            ", ".join(lang.value for lang in ps.allowed_languages)
            if ps.allowed_languages
            else "All"
        )
        table.add_row("Allowed Languages", langs)

        console.print()
        console.print(table)

        # Show problems in problemset
        if ps.problems:
            problems_table = Table(
                title="Problems in Problemset",
                title_style="bold blue",
                box=ROUNDED,
                header_style="bold cyan",
                show_lines=True,
                padding=(0, 1),
            )
            problems_table.add_column(
                "ID", justify="center", style="cyan", no_wrap=True
            )
            problems_table.add_column("Title", style="green")

            for problem in ps.problems:
                if problem.title:  # Only show published problems
                    problems_table.add_row(str(problem.id), problem.title)

            console.print()
            console.print(problems_table)

        console.print()
    except Exception as e:
        console.print(f"[red]Failed to fetch problemset: {str(e)}[/red]")


@problemset.command()
@click.argument("problemset_id", type=int)
@click.pass_obj
def join(ctx: Context, problemset_id: int):
    """Join a problemset."""
    try:
        ctx.api_client.join_problemset(problemset_id)
        console.print(f"[green]Successfully joined problemset {problemset_id}[/green]")
    except Exception as e:
        console.print(f"[red]Failed to join problemset: {str(e)}[/red]")


@problemset.command()
@click.argument("problemset_id", type=int)
@click.pass_obj
def quit(ctx: Context, problemset_id: int):
    """Quit a problemset."""
    try:
        ctx.api_client.quit_problemset(problemset_id)
        console.print(f"[green]Successfully quit problemset {problemset_id}[/green]")
    except Exception as e:
        console.print(f"[red]Failed to quit problemset: {str(e)}[/red]")

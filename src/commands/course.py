"""
Course-related commands for the ACM-OJ CLI.
"""

from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..api_client import APIClient

console = Console()


@click.group()
def course():
    """Manage courses."""
    pass


@course.command()
@click.option("--keyword", help="Filter courses by keyword")
@click.option("--term", type=int, help="Filter courses by term ID")
@click.option("--tag", type=int, help="Filter courses by tag ID")
@click.option("--cursor", type=int, help="Pagination cursor")
def list(
    keyword: Optional[str],
    term: Optional[int],
    tag: Optional[int],
    cursor: Optional[int],
):
    """List available courses."""
    client = APIClient()

    page_number = 1  # Track the current page
    while True:
        console.clear()
        console.rule(f"[bold cyan]📚 Courses - Page {page_number}[/bold cyan]")

        courses, next_cursor = client.get_courses(
            keyword=keyword, term=term, tag=tag, cursor=cursor
        )

        if not courses:
            console.print(
                Panel("[bold red]No more courses found.[/bold red]", expand=False)
            )
            return

        # Display Course Table
        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column("ID", style="dim", width=5)
        table.add_column("Name", style="bold cyan")
        table.add_column("Term", style="bold green")
        table.add_column("Tag", style="bold yellow")
        table.add_column("Description", style="italic", overflow="fold")

        for course in courses:
            table.add_row(
                str(course.id),
                course.name,
                course.term.name if course.term else "—",
                course.tag.name if course.tag else "—",
                course.description or "—",
            )

        console.print(table)

        # Pagination Navigation
        if not next_cursor:
            console.print(
                "\n[bold green]✅ End of results. No more pages available.[/bold green]"
            )
            break

        console.print(
            Panel(
                "[bold cyan]Press [Enter] to load the next page[/bold cyan] | "
                "[bold yellow]Type 'q' to quit[/bold yellow]",
                expand=False,
            )
        )

        proceed = click.prompt(
            "What would you like to do?",
            default="",
            show_default=False,
        )

        if proceed.lower() == "q":
            console.print(
                "\n[bold yellow]👋 Exiting course list. Goodbye![/bold yellow]"
            )
            break

        cursor = next_cursor
        page_number += 1


@course.command()
def enrolled():
    """List courses you are enrolled in."""
    client = APIClient()
    courses = client.get_user_courses()

    if not courses:
        click.echo("You are not enrolled in any courses.")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Term")
    table.add_column("Tag")
    table.add_column("Description")

    for course in courses:
        table.add_row(
            str(course.id),
            course.name,
            course.term.name if course.term else "",
            course.tag.name if course.tag else "",
            course.description or "",
        )

    console.print(table)


@course.command()
@click.argument("course_id", type=int)
def show(course_id: int):
    """Show details of a specific course."""
    client = APIClient()
    try:
        course = client.get_course(course_id)
    except Exception as e:
        console.print(
            f"[bold red]❌ Failed to fetch course details: {str(e)}[/bold red]"
        )
        return

    # Display Course Header
    console.print(
        Panel.fit(
            f"[bold cyan]{course.name}[/bold cyan] (ID: {course.id})",
            title="📚 Course Details",
            border_style="cyan",
        )
    )

    # Display Course Information in Table
    table = Table(box=None, show_header=False)
    table.add_column("Field", style="bold magenta")
    table.add_column("Value", style="bold white", overflow="fold")

    if course.description:
        table.add_row("📝 Description", course.description)
    else:
        table.add_row("📝 Description", "[dim]No description provided[/dim]")

    if course.term:
        term_text = (
            f"{course.term.name} ({course.term.start_time} - {course.term.end_time})"
        )
        table.add_row("📅 Term", term_text)
    else:
        table.add_row("📅 Term", "[dim]No term information[/dim]")

    if course.tag:
        table.add_row("🏷️ Tag", course.tag.name)
    else:
        table.add_row("🏷️ Tag", "[dim]No tag available[/dim]")

    console.print(table)

    # Display Join/Quit Options
    actions = []
    if course.join_url:
        actions.append("[green]✅ You can join this course[/green]")
    if course.quit_url:
        actions.append("[yellow]🚪 You can quit this course[/yellow]")

    if actions:
        console.print(
            Panel.fit("\n".join(actions), title="🔗 Actions", border_style="green")
        )
    else:
        console.print(
            Panel.fit(
                "[dim]No actions available[/dim]",
                title="🔗 Actions",
                border_style="grey50",
            )
        )


@course.command()
@click.argument("course_id", type=int)
def join(course_id: int):
    """Join a course."""
    client = APIClient()
    try:
        client.join_course(course_id)
        click.echo(f"Successfully joined course {course_id}")
    except Exception as e:
        click.echo(f"Failed to join course: {str(e)}", err=True)


@course.command()
@click.argument("course_id", type=int)
def quit(course_id: int):
    """Quit a course."""
    client = APIClient()
    try:
        client.quit_course(course_id)
        click.echo(f"Successfully quit course {course_id}")
    except Exception as e:
        click.echo(f"Failed to quit course: {str(e)}", err=True)


@course.command()
@click.argument("course_id", type=int)
def problemsets(course_id: int):
    """List problemsets in a course."""
    client = APIClient()
    problemsets = client.get_course_problemsets(course_id)

    if not problemsets:
        click.echo("No problemsets found in this course.")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Start Time")
    table.add_column("End Time")
    table.add_column("Late Deadline")
    table.add_column("Description")

    for ps in problemsets:
        table.add_row(
            str(ps.id),
            ps.name,
            ps.type.value,
            str(ps.start_time),
            str(ps.end_time),
            str(ps.late_submission_deadline) if ps.late_submission_deadline else "",
            ps.description or "",
        )

    console.print(table)

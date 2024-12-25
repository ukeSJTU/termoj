"""
User related commands.
"""

import click

from ..context import Context


@click.group()
def user():
    """User related commands."""
    pass


@user.command()
@click.pass_obj
def courses(ctx: Context):
    """List enrolled courses."""
    try:
        courses = ctx.api_client.get_user_courses()
        if not courses:
            click.echo("You are not enrolled in any courses.")
            return

        click.echo("Enrolled courses:")
        for course in courses:
            click.echo(f"- {course.name} (ID: {course.id})")
            if course.term and course.term.name:
                click.echo(f"  Term: {course.term.name}")
            if course.description:
                click.echo(f"  {course.description}")
            click.echo("")  # Empty line between courses
    except Exception as e:
        click.echo(f"Failed to fetch courses: {str(e)}", err=True)


@user.command()
@click.pass_obj
def problemsets(ctx: Context):
    """List enrolled problemsets (contests/homework/exams)."""
    try:
        problemsets = ctx.api_client.get_user_problemsets()
        if not problemsets:
            click.echo("You are not enrolled in any problemsets.")
            return

        click.echo("Enrolled problemsets:")
        for ps in problemsets:
            ps_type = ps.type.value.title() if ps.type else "Unknown"
            click.echo(f"- [{ps_type}] {ps.name} (ID: {ps.id})")
            if ps.course and ps.course.name:
                click.echo(f"  Course: {ps.course.name}")
            if ps.start_time and ps.end_time:
                click.echo(f"  Period: {ps.start_time} to {ps.end_time}")
            if ps.description:
                click.echo(f"  {ps.description}")
            click.echo("")  # Empty line between problemsets
    except Exception as e:
        click.echo(f"Failed to fetch problemsets: {str(e)}", err=True)

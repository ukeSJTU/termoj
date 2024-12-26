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
            ctx.display_message("You are not enrolled in any courses.")
            return

        # Display courses in a table format
        headers = ["ID", "Name", "Term", "Description"]
        rows = []
        for course in courses:
            rows.append(
                [
                    course.id,
                    course.name,
                    course.term.name if course.term else "",
                    course.description or "",
                ]
            )
        ctx.display_table(headers, rows)
    except Exception as e:
        ctx.display_message(f"Failed to fetch courses: {str(e)}")


@user.command()
@click.pass_obj
def problemsets(ctx: Context):
    """List enrolled problemsets (contests/homework/exams)."""
    try:
        problemsets = ctx.api_client.get_user_problemsets()
        if not problemsets:
            ctx.display_message("You are not enrolled in any problemsets.")
            return

        # Display problemsets in a table format
        headers = ["ID", "Type", "Name", "Course", "Period", "Description"]
        rows = []
        for ps in problemsets:
            ps_type = ps.type.value.title() if ps.type else "Unknown"
            period = (
                f"{ps.start_time} to {ps.end_time}"
                if ps.start_time and ps.end_time
                else ""
            )
            rows.append(
                [
                    ps.id,
                    ps_type,
                    ps.name,
                    ps.course.name if ps.course else "",
                    period,
                    ps.description or "",
                ]
            )
        ctx.display_table(headers, rows)
    except Exception as e:
        ctx.display_message(f"Failed to fetch problemsets: {str(e)}")

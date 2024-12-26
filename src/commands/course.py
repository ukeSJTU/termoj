"""
Course-related commands for the ACM-OJ CLI.
"""

from typing import Optional

import click

from ..context import Context


@click.group()
def course():
    """Manage courses."""
    pass


@course.command()
@click.option("--keyword", help="Filter courses by keyword")
@click.option("--term", type=int, help="Filter courses by term ID")
@click.option("--tag", type=int, help="Filter courses by tag ID")
@click.option("--cursor", type=int, help="Pagination cursor")
@click.pass_obj
def list(
    ctx: Context,
    keyword: Optional[str],
    term: Optional[int],
    tag: Optional[int],
    cursor: Optional[int],
):
    """List available courses."""
    page_number = 1  # Track the current page
    while True:
        ctx.display_message(f"Courses - Page {page_number}")

        try:
            courses, next_cursor = ctx.api_client.get_courses(
                keyword=keyword, term=term, tag=tag, cursor=cursor
            )
            if not courses:
                ctx.display_message("No more courses found.")
                return

            headers = ["ID", "Name", "Term", "Tag", "Description"]
            rows = [
                [
                    course.id,
                    course.name,
                    course.term.name if course.term else "—",
                    course.tag.name if course.tag else "—",
                    course.description or "—",
                ]
                for course in courses
            ]
            ctx.display_table(headers, rows)

            if not next_cursor:
                ctx.display_message("End of results. No more pages available.")
                break

            proceed = click.prompt(
                "Press [Enter] to load the next page or type 'q' to quit",
                default="",
                show_default=False,
            )
            if proceed.lower() == "q":
                ctx.display_message("Exiting course list. Goodbye!")
                break

            cursor = next_cursor
            page_number += 1

        except Exception as e:
            ctx.display_message(f"Failed to fetch courses: {str(e)}")
            break


@course.command()
@click.pass_obj
def enrolled(ctx: Context):
    """List courses you are enrolled in."""
    try:
        courses = ctx.api_client.get_user_courses()
        if not courses:
            ctx.display_message("You are not enrolled in any courses.")
            return

        headers = ["ID", "Name", "Term", "Tag", "Description"]
        rows = [
            [
                course.id,
                course.name,
                course.term.name if course.term else "—",
                course.tag.name if course.tag else "—",
                course.description or "—",
            ]
            for course in courses
        ]
        ctx.display_table(headers, rows)

    except Exception as e:
        ctx.display_message(f"Failed to fetch enrolled courses: {str(e)}")


@course.command()
@click.argument("course_id", type=int)
@click.pass_obj
def show(ctx: Context, course_id: int):
    """Show details of a specific course."""
    try:
        course = ctx.api_client.get_course(course_id)
        ctx.display_message(f"Course Details: {course.name} (ID: {course.id})")

        headers = ["Field", "Value"]
        rows = [
            ["Description", course.description or "No description provided"],
            [
                "Term",
                (
                    f"{course.term.name} ({course.term.start_time} - {course.term.end_time})"
                    if course.term
                    else "No term information"
                ),
            ],
            ["Tag", course.tag.name if course.tag else "No tag available"],
        ]
        ctx.display_table(headers, rows)

        actions = []
        if course.join_url:
            actions.append("You can join this course")
        if course.quit_url:
            actions.append("You can quit this course")

        if actions:
            ctx.display_message("\n".join(actions))
        else:
            ctx.display_message("No actions available for this course.")

    except Exception as e:
        ctx.display_message(f"Failed to fetch course details: {str(e)}")


@course.command()
@click.argument("course_id", type=int)
@click.pass_obj
def join(ctx: Context, course_id: int):
    """Join a course."""
    try:
        ctx.api_client.join_course(course_id)
        ctx.display_message(f"Successfully joined course {course_id}")
    except Exception as e:
        ctx.display_message(f"Failed to join course: {str(e)}")


@course.command()
@click.argument("course_id", type=int)
@click.pass_obj
def quit(ctx: Context, course_id: int):
    """Quit a course."""
    try:
        ctx.api_client.quit_course(course_id)
        ctx.display_message(f"Successfully quit course {course_id}")
    except Exception as e:
        ctx.display_message(f"Failed to quit course: {str(e)}")


@course.command()
@click.argument("course_id", type=int)
@click.pass_obj
def problemsets(ctx: Context, course_id: int):
    """List problemsets in a course."""
    try:
        problemsets = ctx.api_client.get_course_problemsets(course_id)
        if not problemsets:
            ctx.display_message("No problemsets found in this course.")
            return

        headers = [
            "ID",
            "Name",
            "Type",
            "Start Time",
            "End Time",
            "Late Deadline",
            "Description",
        ]
        rows = [
            [
                ps.id,
                ps.name,
                ps.type.value,
                str(ps.start_time),
                str(ps.end_time),
                (
                    str(ps.late_submission_deadline)
                    if ps.late_submission_deadline
                    else "—"
                ),
                ps.description or "—",
            ]
            for ps in problemsets
        ]
        ctx.display_table(headers, rows)

    except Exception as e:
        ctx.display_message(f"Failed to fetch problemsets: {str(e)}")

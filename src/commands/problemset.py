"""
Problemset-related commands.
"""

from typing import Optional

import click

from ..context import Context


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
            ctx.display_message("No problemsets found.")
            return

        # Sort problemsets by ID in ascending order
        problemsets = sorted(
            problemsets, key=lambda ps: ps.id if ps.id is not None else float("inf")
        )

        headers = ["ID", "Name", "Type", "Start Time", "End Time"]
        rows = [
            [
                ps.id,
                ps.name,
                ps.type.value,
                str(ps.start_time),
                str(ps.end_time),
            ]
            for ps in problemsets
        ]

        ctx.display_table(headers, rows)

    except Exception as e:
        ctx.display_message(f"Failed to fetch problemsets: {str(e)}")


@problemset.command()
@click.argument("problemset_id", type=int)
@click.pass_obj
def show(ctx: Context, problemset_id: int):
    """Show details of a specific problemset."""
    try:
        ps = ctx.api_client.get_problemset(problemset_id)

        # Display problemset details
        headers = ["Property", "Value"]
        rows = [
            ["ID", str(ps.id)],
            ["Name", ps.name],
            ["Description", ps.description or "N/A"],
            ["Type", ps.type.value],
            ["Start Time", str(ps.start_time)],
            ["End Time", str(ps.end_time)],
            [
                "Late Submission",
                (
                    str(ps.late_submission_deadline)
                    if ps.late_submission_deadline
                    else "Not Allowed"
                ),
            ],
            [
                "Allowed Languages",
                (
                    ", ".join(lang.value for lang in ps.allowed_languages)
                    if ps.allowed_languages
                    else "All"
                ),
            ],
        ]
        ctx.display_table(headers, rows)

        # Show problems in problemset
        if ps.problems:
            problem_headers = ["ID", "Title"]
            problem_rows = [
                [problem.id, problem.title] for problem in ps.problems if problem.title
            ]
            ctx.display_message("Problems in Problemset:")
            ctx.display_table(problem_headers, problem_rows)

    except Exception as e:
        ctx.display_message(f"Failed to fetch problemset: {str(e)}")


@problemset.command()
@click.argument("problemset_id", type=int)
@click.pass_obj
def join(ctx: Context, problemset_id: int):
    """Join a problemset."""
    try:
        ctx.api_client.join_problemset(problemset_id)
        ctx.display_message(f"Successfully joined problemset {problemset_id}")
    except Exception as e:
        ctx.display_message(f"Failed to join problemset: {str(e)}")


@problemset.command()
@click.argument("problemset_id", type=int)
@click.pass_obj
def quit(ctx: Context, problemset_id: int):
    """Quit a problemset."""
    try:
        ctx.api_client.quit_problemset(problemset_id)
        ctx.display_message(f"Successfully quit problemset {problemset_id}")
    except Exception as e:
        ctx.display_message(f"Failed to quit problemset: {str(e)}")

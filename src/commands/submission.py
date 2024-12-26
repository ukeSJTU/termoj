"""
Submission-related commands.
"""

import time
from typing import List, Optional

import click

from ..context import Context
from ..models import Profile, Submission, SubmissionBrief


@click.group()
def submission():
    """Manage and track submissions."""
    pass


@submission.command()
@click.argument("submission_id", type=int)
@click.option(
    "--watch", "-w", is_flag=True, help="Watch submission status in real-time"
)
@click.option(
    "--interval",
    "-i",
    type=int,
    default=2,
    help="Polling interval in seconds when watching",
)
@click.pass_obj
def status(ctx: Context, submission_id: int, watch: bool, interval: int):
    """
    Check the status of a submission.

    If --watch is specified, continuously poll for updates until the submission is complete.
    """

    def display_status(submission: Submission):
        """Helper function to display submission status."""
        headers = ["Attribute", "Value"]
        rows = [
            ["ID", submission.id],
            ["Status", submission.status.value if submission.status else "N/A"],
        ]

        if submission.score is not None and submission.should_show_score:
            rows.append(["Score", submission.score])

        if submission.time_msecs is not None:
            rows.append(["Time", f"{submission.time_msecs} ms"])

        if submission.memory_bytes is not None:
            memory_mb = submission.memory_bytes / (1024 * 1024)
            rows.append(["Memory", f"{memory_mb:.2f} MB"])

        if submission.message:
            rows.append(["Message", submission.message])

        if submission.details:
            test_cases = submission.details.get("tests", [])
            for i, test in enumerate(test_cases, 1):
                rows.append([f"Test {i} Status", test.get("status", "Unknown")])
                if "time_msecs" in test:
                    rows.append([f"Test {i} Time", f"{test['time_msecs']} ms"])
                if "memory_bytes" in test:
                    memory_mb = test["memory_bytes"] / (1024 * 1024)
                    rows.append([f"Test {i} Memory", f"{memory_mb:.2f} MB"])
                if "message" in test:
                    rows.append([f"Test {i} Message", test["message"]])

        ctx.display_table(headers, rows)

    try:
        if not watch:
            # Single status check
            submission = ctx.api_client.get_submission(submission_id)
            display_status(submission)
        else:
            # Watch mode - poll until submission is complete
            ctx.display_message("Watching submission status (Ctrl+C to stop)...")
            completed_statuses = {
                "accepted",
                "wrong_answer",
                "compile_error",
                "runtime_error",
                "time_limit_exceeded",
                "memory_limit_exceeded",
                "system_error",
            }

            while True:
                submission = ctx.api_client.get_submission(submission_id)
                click.clear()  # Clear terminal
                display_status(submission)

                if submission.status.value in completed_statuses:
                    break

                time.sleep(interval)

    except KeyboardInterrupt:
        ctx.display_message("Stopped watching submission status.")
    except Exception as e:
        ctx.display_message(f"Failed to get submission status: {str(e)}")


@submission.command()
@click.option("--problem", "-p", type=int, help="Filter by problem ID")
@click.option("--status", "-s", type=str, help="Filter by submission status")
@click.option("--language", "-l", type=str, help="Filter by programming language")
@click.option("--cursor", "-c", type=str, help="Pagination cursor for submissions")
@click.pass_obj
def list(
    ctx: Context,
    problem: Optional[int],
    status: Optional[str],
    language: Optional[str],
    cursor: Optional[str],
):
    """List your recent submissions."""
    try:
        profile: Profile = ctx.api_client.get_profile()
        username = profile.username

        # Build query parameters
        params = {
            "username": username,
            "problem_id": problem,
            "status": status,
            "lang": language,
            "cursor": cursor,
        }
        params = {k: v for k, v in params.items() if v is not None}

        submissions: List[SubmissionBrief] = ctx.api_client.get_submissions(**params)

        if not submissions:
            ctx.display_message("No submissions found.")
            return

        headers = [
            "ID",
            "Problem ID",
            "Problem Title",
            "Language",
            "Status",
            "Created At",
        ]
        rows = []
        for sub in submissions:
            problem_id = (
                str(sub.problem.id) if sub.problem and sub.problem.id else "N/A"
            )
            problem_title = (
                sub.problem.title if sub.problem and sub.problem.title else "N/A"
            )
            status_text = sub.status.value if sub.status else "N/A"
            language_text = sub.language.value if sub.language else "N/A"
            created_at = (
                sub.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if sub.created_at
                else "N/A"
            )
            rows.append(
                [
                    sub.id,
                    problem_id,
                    problem_title,
                    language_text,
                    status_text,
                    created_at,
                ]
            )

        ctx.display_table(headers, rows)

        if cursor:
            ctx.display_message(f"Next cursor: {cursor}")
            ctx.display_message("Use '--cursor <cursor>' to load the next page.")

    except Exception as e:
        ctx.display_message(f"Failed to list submissions: {str(e)}")

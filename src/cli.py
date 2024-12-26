"""
Main CLI entry point for the ACM-OJ tool.
"""

import click

from . import __version__
from .api_client import APIClient
from .commands.auth import auth
from .commands.config import config
from .commands.course import course
from .commands.problem import problem
from .commands.problemset import problemset
from .commands.submission import submission
from .commands.user import user
from .context import Context


class CustomGroup(click.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context_settings = {
            "help_option_names": ["-h", "--help"],
        }


@click.group(cls=CustomGroup)
@click.version_option(
    "0.1.0",
    "-v",
    "--version",
    message="%(prog)s, version %(version)s",
)
@click.pass_context
def cli(ctx: click.Context):
    """ACM Online Judge CLI tool.

    A command-line interface for interacting with the ACM-OJ platform.

    Common commands:
    - config view: View all configuration settings
    - config get <option>: View a specific configuration option
    - config set <option> <value>: Set a configuration option
    - config reset: Reset to default settings
    - config init: Initialize configuration

    Configuration options:
    - display_mode: Control output style (plain/rich/cartoon)

    - auth login: Log in using your personal access token
    - auth whoami: Show current user information
    - auth logout: Log out and clear token

    - user courses: List enrolled courses
    - user problemsets: List enrolled problemsets

    - problem show: Show problem details
    - problem submit: Submit a solution

    - problemset list: List available problems

    - submission status: Check submission status
    - submission list: List your submissions

    - course list: List available courses
    - course enrolled: List enrolled courses
    - course show: Show course details
    - course join: Join a course
    - course problemsets: List course problemsets

    Run 'termoj COMMAND --help' for more information on a command.
    """
    ctx.obj = Context()
    # Initialize API client
    ctx.obj.api_client = APIClient()


# Register command groups
cli.add_command(auth)
cli.add_command(config)
cli.add_command(user)
cli.add_command(problem)
cli.add_command(problemset)
cli.add_command(submission)
cli.add_command(course)


if __name__ == "__main__":
    cli()

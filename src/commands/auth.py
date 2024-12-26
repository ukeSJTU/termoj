"""
Authentication related commands.
"""

import click

from ..context import Context


@click.group()
def auth():
    """Authentication related commands."""
    pass


@auth.command()
@click.argument("token")
@click.pass_obj
def login(ctx: Context, token: str):
    """
    Log in using a personal access token.

    Get your token from ACM-OJ website: Profile -> API -> Generate Token
    """
    try:
        ctx.api_client.set_token(token)
        # Verify token by getting profile
        profile = ctx.api_client.get_profile()
        ctx.display_message(f"Successfully logged in as {profile.username}!")
    except Exception as e:
        ctx.display_message(f"Login failed: {str(e)}")


@auth.command()
@click.pass_obj
def whoami(ctx: Context):
    """Show current user information."""
    try:
        profile = ctx.api_client.get_profile()
        headers = ["Attribute", "Value"]
        rows = [
            ["Username", profile.username],
            ["Name", profile.friendly_name or "N/A"],
            ["Student ID", profile.student_id or "N/A"],
        ]
        ctx.display_table(headers, rows)
    except Exception as e:
        ctx.display_message("Not logged in or session expired.")


@auth.command()
@click.pass_obj
def logout(ctx: Context):
    """Log out by clearing the stored token."""
    try:
        ctx.api_client.clear_token()
        ctx.display_message("Successfully logged out!")
    except Exception as e:
        ctx.display_message(f"Logout failed: {str(e)}")

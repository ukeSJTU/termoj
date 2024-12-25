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
        click.echo(f"Successfully logged in as {profile.username}!")
    except Exception as e:
        click.echo(f"Login failed: {str(e)}", err=True)


@auth.command()
@click.pass_obj
def whoami(ctx: Context):
    """Show current user information."""
    try:
        profile = ctx.api_client.get_profile()
        click.echo(f"Logged in as: {profile.username}")
        if profile.friendly_name != None:
            click.echo(f"Name: {profile.friendly_name}")
        if profile.student_id != None:
            click.echo(f"Student ID: {profile.student_id}")
    except Exception as e:
        click.echo("Not logged in or session expired.", err=True)


@auth.command()
@click.pass_obj
def logout(ctx: Context):
    """Log out by clearing the stored token."""
    ctx.api_client.clear_token()
    click.echo("Successfully logged out!")

"""
Configuration management commands.
"""

import click

from ..context import Context


@click.group()
def config():
    """Configuration management commands."""
    pass


@config.command()
@click.pass_obj
def view(ctx: Context):
    """View current configuration settings."""
    headers = ["Setting", "Value"]
    rows = [
        ["Display Mode", ctx.config.display_mode],
        ["Config Directory", str(ctx.config.config_dir)],
        ["Logs Directory", str(ctx.config.logs_dir)],
    ]
    ctx.display_table(headers, rows)


@config.command()
@click.argument("option")
@click.argument("value")
@click.pass_obj
def set(ctx: Context, option: str, value: str):
    """Set a configuration option.

    OPTION is the name of the option to set
    VALUE is the new value for the option

    Available options:
    - display_mode: plain, rich, or cartoon
    """
    try:
        if option == "display_mode":
            if value not in ["plain", "rich", "cartoon"]:
                raise ValueError(
                    f"Invalid display mode: {value}. Must be one of: plain, rich, cartoon"
                )
            ctx.update_display_mode(value)
            ctx.display_message(f"Option {option} set to: {value}")
        else:
            ctx.display_message(f"Unknown option: {option}")
    except Exception as e:
        ctx.display_message(f"Error: {str(e)}")


@config.command()
@click.argument("option")
@click.pass_obj
def get(ctx: Context, option: str):
    """Get the value of a configuration option.

    OPTION is the name of the option to get

    Available options:
    - display_mode: Current display mode setting
    """
    try:
        if option == "display_mode":
            ctx.display_message(f"display_mode = {ctx.config.display_mode}")
        else:
            ctx.display_message(f"Unknown option: {option}")
    except Exception as e:
        ctx.display_message(f"Error: {str(e)}")


@config.command()
@click.confirmation_option(prompt="Are you sure you want to reset all settings?")
@click.pass_obj
def reset(ctx: Context):
    """Reset all settings to default values."""
    try:
        # Reset to default values
        ctx.config._config = {"token": None, "display_mode": "rich"}
        ctx.config._save_config()
        ctx.update_display_mode("rich")
        ctx.display_message("Configuration has been reset to default values.")
    except Exception as e:
        ctx.display_message(f"Error resetting configuration: {str(e)}")


@config.command()
@click.pass_obj
def init(ctx: Context):
    """Initialize configuration with default settings."""
    try:
        if not ctx.config.config_file.exists():
            ctx.config._config = {"token": None, "display_mode": "rich"}
            ctx.config._save_config()
            ctx.display_message("Configuration initialized with default settings.")
        else:
            ctx.display_message(
                "Configuration file already exists. Use 'reset' to start fresh."
            )
    except Exception as e:
        ctx.display_message(f"Error initializing configuration: {str(e)}")

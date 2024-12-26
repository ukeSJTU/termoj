"""
Context management for the CLI tool.
"""

from typing import Any, List, Optional

from .api_client import APIClient
from .config import Config
from .ui_controller import UIController


class Context:
    """Context object to share state between CLI commands."""

    def __init__(self):
        self.config = Config()
        self.api_client: Optional[APIClient] = None
        self.ui = UIController(self.config.display_mode)

    def display_table(self, headers: List[str], rows: List[List[Any]]) -> None:
        """Display data in tabular format using current display mode."""
        self.ui.display_table(headers, rows)

    def display_message(self, message: str, style: Optional[str] = None) -> None:
        """Display message using current display mode."""
        self.ui.display_message(message, style)

    def update_display_mode(self, mode: str) -> None:
        """Update the display mode."""
        self.config.display_mode = mode
        self.ui.set_display_mode(mode)

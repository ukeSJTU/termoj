"""
Context management for the CLI tool.
"""

from typing import Optional

from .api_client import APIClient


class Context:
    """Context object to share state between CLI commands."""

    def __init__(self):
        self.api_client: Optional[APIClient] = None

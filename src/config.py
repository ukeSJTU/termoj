"""
Configuration management for the ACM-OJ CLI tool.
"""

import json
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, Optional


class Config:
    """Manages CLI tool configuration and credentials."""

    def __init__(self):
        """Initialize configuration with default values."""
        self.config_dir = Path.home() / ".termoj"
        self.config_file = self.config_dir / "config.json"
        self.logs_dir = self.config_dir / "logs"
        self._config: Dict = {
            "token": None,
            "display_mode": "rich",
        }
        # Create config directory first
        self.config_dir.mkdir(exist_ok=True)
        self._load_config()
        self._setup_logging()

    def _setup_logging(self):
        """Set up logging configuration."""
        self.logs_dir.mkdir(exist_ok=True)
        log_file = self.logs_dir / "acm_oj.log"

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Create file handler
        file_handler = RotatingFileHandler(
            log_file, maxBytes=1024 * 1024, backupCount=3  # 1MB
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.WARNING)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

    def _load_config(self):
        """Load configuration from file."""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                self._config = json.load(f)

    def _save_config(self):
        """Save current configuration to file."""
        self.config_dir.mkdir(exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(self._config, f, indent=2)

    @property
    def token(self) -> Optional[str]:
        """Get stored authentication token."""
        return self._config.get("token")

    @token.setter
    def token(self, value: Optional[str]):
        """Store authentication token."""
        self._config["token"] = value
        self._save_config()

    @property
    def display_mode(self) -> str:
        """Get current display mode."""
        return self._config.get("display_mode", "rich")

    @display_mode.setter
    def display_mode(self, mode: str) -> None:
        """Set display mode."""
        if mode not in ["plain", "rich", "cartoon"]:
            raise ValueError(f"Invalid display mode: {mode}")
        self._config["display_mode"] = mode
        self._save_config()

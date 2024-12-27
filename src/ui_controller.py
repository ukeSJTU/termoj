"""
UI controller for the ACM-OJ CLI tool.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from rich import print as rich_print
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text


class DisplayStrategy(ABC):
    @abstractmethod
    def display_table(self, headers: List[str], rows: List[List[Any]]) -> None:
        pass

    @abstractmethod
    def display_message(self, message: str, style: Optional[str] = None) -> None:
        pass


class PlainDisplay(DisplayStrategy):
    def display_table(self, headers: List[str], rows: List[List[Any]]) -> None:
        # Simple ASCII table
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        # Print headers
        header_row = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
        print(header_row)
        print("-" * len(header_row))

        # Print rows
        for row in rows:
            print(" | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)))

    def display_message(self, message: str, style: Optional[str] = None) -> None:
        print(message)


class RichDisplay(DisplayStrategy):
    def __init__(self):
        self.console = Console()
        self.styles = {
            "success": "green",
            "error": "red",
            "warning": "yellow",
            "info": "blue",
        }

    def display_table(self, headers: List[str], rows: List[List[Any]]) -> None:
        table = Table()
        for header in headers:
            table.add_column(header)
        for row in rows:
            table.add_row(*[str(cell) for cell in row])
        self.console.print(table)

    def display_message(self, message: str, style: Optional[str] = None) -> None:
        if style in self.styles:
            self.console.print(message, style=self.styles[style])
        else:
            rich_print(message)


class CartoonDisplay(DisplayStrategy):
    def __init__(self):
        self.console = Console()
        self.emojis = {"success": "✨", "error": "💥", "info": "💡", "warning": "⚠️"}

    def display_table(self, headers: List[str], rows: List[List[Any]]) -> None:
        table = Table(style="bold magenta")
        for header in headers:
            table.add_column(f"🎯 {header}", style="cyan")
        for row in rows:
            table.add_row(*[f"✨ {str(cell)}" for cell in row])
        self.console.print(table)

    def display_message(self, message: str, style: Optional[str] = None) -> None:
        if style == "error":
            rich_print(f"{self.emojis['error']} {message}")
        elif style == "warning":
            rich_print(f"{self.emojis['warning']} {message}")
        elif style == "success":
            rich_print(f"{self.emojis['success']} {message}")
        else:
            rich_print(f"{self.emojis['info']} {message}")


class UIController:
    def __init__(self, display_mode: str = "plain"):
        self.display_strategies = {
            "plain": PlainDisplay(),
            "rich": RichDisplay(),
            "cartoon": CartoonDisplay(),
        }
        self.set_display_mode(display_mode)

    def set_display_mode(self, mode: str) -> None:
        if mode not in self.display_strategies:
            raise ValueError(f"Invalid display mode: {mode}")
        self.current_strategy = self.display_strategies[mode]

    def display_table(self, headers: List[str], rows: List[List[Any]]) -> None:
        self.current_strategy.display_table(headers, rows)

    def display_message(self, message: str, style: Optional[str] = None) -> None:
        self.current_strategy.display_message(message, style)

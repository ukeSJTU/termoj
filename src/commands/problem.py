"""
Problem-specific commands.
"""

import re
from typing import Optional

import click
from pylatexenc.latex2text import LatexNodes2Text
from rich.box import ROUNDED, SIMPLE
from rich.columns import Columns
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table

from ..context import Context

console = Console()


def process_latex(text: str) -> str:
    """Process LaTeX math expressions in text.

    Converts both inline ($...$) and display ($$...$$) math to ASCII.
    """

    def replace_math(match):
        latex = match.group(1)
        return LatexNodes2Text().latex_to_text(latex)

    # Replace display math first ($$...$$)
    text = re.sub(r"\$\$(.*?)\$\$", lambda m: "\n" + replace_math(m) + "\n", text)
    # Then replace inline math ($...$)
    text = re.sub(r"\$(.*?)\$", replace_math, text)
    return text


def format_code_block(code: str, language: str = "") -> Syntax:
    """Format code blocks with syntax highlighting."""
    return Syntax(code, language, theme="monokai", line_numbers=True)


@click.group()
def problem():
    """Manage and interact with problems."""
    pass


@problem.command()
@click.argument("problem_id", type=int)
@click.pass_obj
def show(ctx: Context, problem_id: int):
    """Show details of a specific problem."""
    try:
        problem = ctx.api_client.get_problem(problem_id)

        # --- HEADER ---
        console.print(
            Panel(
                f"[bold blue]Problem {problem.id}: {problem.title}[/bold blue]",
                border_style="blue",
                expand=True,
            )
        )
        console.print(Rule(style="blue"))

        # --- DESCRIPTION ---
        description_text = process_latex(
            problem.description or "No description provided."
        )
        console.print(
            Panel(
                Markdown(description_text),
                title="[bold cyan]Description[/bold cyan]",
                border_style="cyan",
                expand=False,
                padding=(1, 2),
            )
        )

        # --- INPUT & OUTPUT FORMAT ---
        input_text = process_latex(problem.input or "No input format provided.")
        output_text = process_latex(problem.output or "No output format provided.")

        console.print(
            Columns(
                [
                    Panel(
                        Markdown(input_text),
                        title="[bold green]Input Format[/bold green]",
                        border_style="green",
                        padding=(1, 2),
                        expand=True,
                    ),
                    Panel(
                        Markdown(output_text),
                        title="[bold yellow]Output Format[/bold yellow]",
                        border_style="yellow",
                        padding=(1, 2),
                        expand=True,
                    ),
                ],
                equal=True,
                expand=True,
            )
        )

        # --- CONSTRAINTS & LANGUAGES ---
        constraints_text = process_latex(
            problem.data_range or "No constraints provided."
        )
        languages_text = (
            ", ".join(str(lang) for lang in problem.languages_accepted)
            if problem.languages_accepted
            else "No languages specified."
        )

        console.print(
            Columns(
                [
                    Panel(
                        Markdown(constraints_text),
                        title="[bold magenta]Constraints[/bold magenta]",
                        border_style="magenta",
                        padding=(1, 2),
                        expand=True,
                    ),
                    Panel(
                        f"[green]{languages_text}[/green]",
                        title="[bold blue]Accepted Languages[/bold blue]",
                        border_style="blue",
                        padding=(1, 2),
                        expand=True,
                    ),
                ],
                equal=True,
                expand=True,
            )
        )

        # --- EXAMPLES (Side by Side per Test Case) ---
        console.print(Rule(style="cyan"))
        console.print("[bold cyan]Examples[/bold cyan]")

        if problem.examples:
            for i, example in enumerate(problem.examples, start=1):
                input_example = example.input or "No Input Provided"
                output_example = example.output or "No Output Provided"
                explanation = example.description or ""

                console.print(
                    Columns(
                        [
                            Panel(
                                format_code_block(input_example),
                                title=f"[bold cyan]Example {i} - Input[/bold cyan]",
                                border_style="cyan",
                                padding=(1, 2),
                                expand=True,
                            ),
                            Panel(
                                format_code_block(output_example),
                                title=f"[bold cyan]Example {i} - Output[/bold cyan]",
                                border_style="cyan",
                                padding=(1, 2),
                                expand=True,
                            ),
                        ],
                        equal=True,
                        expand=True,
                    )
                )

                if explanation:
                    console.print(
                        Panel(
                            Markdown(process_latex(explanation)),
                            title="[bold cyan]Explanation[/bold cyan]",
                            border_style="cyan",
                            padding=(1, 2),
                        )
                    )
                console.print(Rule(style="cyan"))
        else:
            console.print("[italic]No examples provided.[/italic]")

    except Exception as e:
        console.print(f"[red]Failed to fetch problem details: {str(e)}[/red]")


@problem.command()
@click.argument("problem_id", type=int)
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--language",
    "-l",
    required=True,
    type=click.Choice(
        ["cpp", "python", "java", "git", "verilog"], case_sensitive=False
    ),
)
@click.pass_obj
def submit(ctx: Context, problem_id: int, file: str, language: str):
    """Submit a solution to a problem."""
    try:
        with open(file, "r") as f:
            code = f.read()

        result = ctx.api_client.submit_solution(problem_id, code, language.lower())
        submission_id = result.id

        if submission_id:
            ctx.display_message(
                f"Solution submitted successfully!\n"
                f"Submission ID: {submission_id}\n"
                f"Use 'termoj submission status {submission_id}' to check the result."
            )
        else:
            ctx.display_message("Submission failed: No submission ID received.")

    except Exception as e:
        ctx.display_message(f"Submission failed: {str(e)}")

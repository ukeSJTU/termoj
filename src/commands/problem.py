"""
Problem-specific commands.
"""

import re
from typing import Optional

import click
from pylatexenc.latex2text import LatexNodes2Text
from rich.box import ROUNDED, SIMPLE
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

        # Display problem title in a fancy panel
        title_panel = Panel(
            f"Problem {problem.id}: {problem.title}",
            style="bold blue",
            box=ROUNDED,
            border_style="blue",
        )
        console.print()
        console.print(title_panel)

        # Process and display description with markdown and LaTeX support
        if problem.description:
            console.print()
            console.print(Rule(style="dim"))
            console.print("\n[bold blue]Description[/bold blue]")
            md_text = process_latex(problem.description)
            console.print(Markdown(md_text))

        # Process and display input format
        if problem.input:
            console.print()
            console.print(Rule(style="dim"))
            console.print("\n[bold blue]Input Format[/bold blue]")
            md_text = process_latex(problem.input)
            console.print(Markdown(md_text))

        # Process and display output format
        if problem.output:
            console.print()
            console.print(Rule(style="dim"))
            console.print("\n[bold blue]Output Format[/bold blue]")
            md_text = process_latex(problem.output)
            console.print(Markdown(md_text))

        # Display examples in panels with syntax highlighting
        if problem.examples:
            console.print()
            console.print(Rule(style="dim"))
            console.print("\n[bold blue]Examples[/bold blue]")

            for i, example in enumerate(problem.examples, 1):
                console.print(f"\n[bold cyan]Example {i}[/bold cyan]")

                if example.input:
                    input_panel = Panel(
                        format_code_block(example.input),
                        title="[bold cyan]Input[/bold cyan]",
                        box=SIMPLE,
                        padding=(1, 2),
                    )
                    console.print(input_panel)

                if example.output:
                    output_panel = Panel(
                        format_code_block(example.output),
                        title="[bold cyan]Output[/bold cyan]",
                        box=SIMPLE,
                        padding=(1, 2),
                    )
                    console.print(output_panel)

                if example.description:
                    explanation_panel = Panel(
                        Markdown(process_latex(example.description)),
                        title="[bold cyan]Explanation[/bold cyan]",
                        box=SIMPLE,
                        padding=(1, 2),
                    )
                    console.print(explanation_panel)

        # Process and display constraints
        if problem.data_range:
            console.print()
            console.print(Rule(style="dim"))
            console.print("\n[bold blue]Constraints[/bold blue]")
            md_text = process_latex(problem.data_range)
            constraints_panel = Panel(
                Markdown(md_text), box=SIMPLE, padding=(1, 2), border_style="blue"
            )
            console.print(constraints_panel)

        # Display accepted languages in a panel
        if problem.languages_accepted:
            console.print()
            console.print(Rule(style="dim"))
            langs = ", ".join(str(lang) for lang in problem.languages_accepted)
            lang_panel = Panel(
                f"[green]{langs}[/green]",
                title="[bold blue]Accepted Languages[/bold blue]",
                box=ROUNDED,
                padding=(1, 2),
            )
            console.print("\n", lang_panel)
            console.print()

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
            success_panel = Panel(
                f"[green]Solution submitted successfully![/green]\n"
                f"[cyan]Submission ID:[/cyan] {submission_id}\n"
                f"[dim]Use 'termoj submission status {submission_id}' to check the result.[/dim]",
                box=ROUNDED,
                border_style="green",
            )
            console.print(success_panel)
        else:
            console.print("[red]Submission failed: No submission ID received.[/red]")

    except Exception as e:
        console.print(f"[red]Submission failed: {str(e)}[/red]")

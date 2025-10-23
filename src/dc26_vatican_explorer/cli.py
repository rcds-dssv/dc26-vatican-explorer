"""Console script for dc26_vatican_explorer."""

import typer
from rich.console import Console

from dc26_vatican_explorer import utils

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for dc26_vatican_explorer."""
    console.print("Replace this message by putting your code into "
               "dc26_vatican_explorer.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()

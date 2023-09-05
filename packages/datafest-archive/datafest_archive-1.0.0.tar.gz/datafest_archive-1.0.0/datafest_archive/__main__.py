import typer
from rich.console import Console

from datafest_archive import project_call_subcommand, version, website_subcommand

app = typer.Typer(
    name="datafest-archive",
    help="DataFestArchive is a Python package designed to generate the DataFestArchive website from past versions of DataFest",
    add_completion=False,
)

app.add_typer(
    website_subcommand.app,
    name="website",
    help="Create pages of projects and people (students and advisors) from the database (sqlite3) using wowchemy-hugo-academic.",
)

app.add_typer(
    project_call_subcommand.app,
    name="project-call",
    help="Reads the spreadsheet and imports the data into the database (sqlite3).",
)

console = Console()


def version_callback(print_version: bool) -> None:
    """Print the version of the package."""
    if print_version:
        console.print(f"[yellow]datafest-archive[/] version: [bold blue]{version}[/]")
        raise typer.Exit()


@app.command()
def main(
    print_version: bool = typer.Option(
        None,
        "-v",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Prints the version of the datafest-archive package.",
    ),
) -> None:
    console.print(f"[bold blue]DataFestArchive[/] version: [bold blue]{version}[/]")


if __name__ == "__main__":
    app()

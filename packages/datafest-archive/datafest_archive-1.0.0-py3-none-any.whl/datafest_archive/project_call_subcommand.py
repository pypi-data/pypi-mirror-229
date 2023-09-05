from typing import Annotated

from pathlib import Path

import typer

from datafest_archive.spreadsheet.__main__ import import_spreadsheet

app = typer.Typer()


@app.command()
def import_data(
    spreadsheet_path: Annotated[
        Path,
        typer.Argument(help="Spreadsheet file to use.", default=None),
    ],
    database_file: Annotated[
        Path,
        typer.Argument(help="Database sqlite3 file", default=None),
    ],
) -> None:
    import_spreadsheet(spreadsheet_path, database_file)


if __name__ == "__main__":
    app()

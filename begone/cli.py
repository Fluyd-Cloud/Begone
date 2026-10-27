"""Command line interface: ``begone --help``."""

import logging
from pathlib import Path
from typing import Annotated

import typer

from begone import readme
from begone.arcep import ArcepClient
from begone.build import collect, load_database, read_list, write
from begone.diff import summarize
from begone.ranges import sanitize, to_international
from begone.version import ListVersion

app = typer.Typer(no_args_is_help=True, add_completion=False)

DatabaseOption = Annotated[Path, typer.Option(help="YAML database")]
DistOption = Annotated[Path, typer.Option(help="Directory of the generated lists")]
ReadmeOption = Annotated[Path, typer.Option(help="README to keep in sync")]
VersionOption = Annotated[Path, typer.Option(help="Version file")]


def fail(message: str) -> None:
    typer.secho(message, fg=typer.colors.RED, err=True)
    raise typer.Exit(1)


@app.callback()
def main(verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False) -> None:
    """Builds Begone blocking lists for French numbers."""
    logging.basicConfig(level=logging.INFO if verbose else logging.ERROR, format="%(levelname)s %(message)s")


@app.command()
def build(
    database: DatabaseOption = Path("data/numbers.yaml"),
    dist: DistOption = Path("dist"),
    readme_file: ReadmeOption = Path("README.md"),
    cache_dir: Annotated[Path | None, typer.Option(help="Reuse ARCEP responses stored in this directory")] = None,
) -> None:
    """Fetches ARCEP ranges and generates every list and the README links."""
    db = load_database(database)
    result = collect(db, ArcepClient(cache_dir=cache_dir))
    if result.empty_operators:
        fail(f"no range found for: {', '.join(result.empty_operators)}")

    sizes = write(db, result, dist)
    for file, size in sizes.items():
        typer.echo(f"{size:6} {dist / file}")
    if empty := [file for file, size in sizes.items() if size == 0]:
        fail(f"empty lists: {', '.join(empty)}")

    if readme.update_file(readme_file, db):
        typer.echo(f"updated {readme_file}")


@app.command()
def check(
    database: DatabaseOption = Path("data/numbers.yaml"),
    dist: DistOption = Path("dist"),
    readme_file: ReadmeOption = Path("README.md"),
) -> None:
    """Checks, without network, that the database, lists and README agree."""
    db = load_database(database)
    errors = []

    expected = {block_list.file for block_list in db.lists}
    for file in sorted(expected):
        path = dist / file
        if not path.exists():
            errors.append(f"{path} is missing, run `make build`")
        elif not read_list(path):
            errors.append(f"{path} is empty")
    for path in sorted(dist.glob("*.xml")):
        if path.name not in expected:
            errors.append(f"{path} is not declared in {database}")

    if readme.update(readme_file.read_text(), db) != readme_file.read_text():
        errors.append(f"{readme_file} is out of date, run `make build`")

    if errors:
        fail("\n".join(errors))
    typer.echo("OK")


@app.command()
def lookup(number: Annotated[str, typer.Argument(help="Phone number, e.g. 01 87 68 68 87")]) -> None:
    """Finds the ARCEP operator mnemonic (mnemo) owning a French number."""
    national = sanitize(number)
    if national.startswith("+33"):
        national = "0" + national[3:]
    found = ArcepClient().lookup(national)
    if not found:
        fail(f"no range found for {national}")
        return
    typer.echo(f"{found.mnemo}  {to_international(found.start)} - {to_international(found.end)}")


@app.command()
def diff(
    old: Annotated[Path, typer.Argument(help="Previous dist directory")],
    new: Annotated[Path, typer.Argument(help="New dist directory")] = Path("dist"),
    database: DatabaseOption = Path("data/numbers.yaml"),
) -> None:
    """Prints a Markdown summary of the changes between two dist directories."""
    typer.echo(summarize(load_database(database), old, new))


@app.command()
def bump(
    structural: Annotated[bool, typer.Option(help="Also bump the version (new list or operator)")] = False,
    version_file: VersionOption = Path("begone.version"),
) -> None:
    """Bumps the build number of the published lists."""
    version = ListVersion.read(version_file).bump(structural)
    version.write(version_file)
    typer.echo(f"{version.version} (build {version.build})")


@app.command()
def version(version_file: VersionOption = Path("begone.version")) -> None:
    """Prints the version of the published lists."""
    typer.echo(ListVersion.read(version_file).version)


def run() -> None:
    app()


if __name__ == "__main__":
    run()

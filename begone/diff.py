"""Summarizes the changes between two versions of the ``dist/`` directory."""

from pathlib import Path

from begone.build import Database, read_list


def _numbers(path: Path) -> set[str]:
    return {entry["number"] for entry in read_list(path)} if path.exists() else set()


def summarize(database: Database, old_dir: Path, new_dir: Path) -> str:
    """Returns a Markdown table of added and removed patterns, per changed list."""
    rows = []
    for block_list in database.lists:
        old = _numbers(old_dir / block_list.file)
        new = _numbers(new_dir / block_list.file)
        if old != new:
            rows.append(
                f"| {block_list.title} | `{block_list.file}` | {len(new)} | +{len(new - old)} | -{len(old - new)} |"
            )
    if not rows:
        return "No change."
    header = "| List | File | Patterns | Added | Removed |\n|---|---|---:|---:|---:|"
    return "\n".join([header, *rows])

"""Keeps the download links of the README in sync with the database."""

import re
from pathlib import Path

from begone.build import Database

BASE_URL = "https://raw.githubusercontent.com/Fluyd-Cloud/Begone/refs/heads/main/dist"
START = "<!-- lists:start -->"
END = "<!-- lists:end -->"
INDENT = "   "


def render(database: Database) -> str:
    """Renders the bullet list of downloadable lists, children under their parent."""
    lines = []

    def add(parent: str | None, depth: int) -> None:
        for block_list in database.lists:
            if block_list.parent != parent:
                continue
            suffix = " (recommended)" if block_list.recommended else ""
            link = f"[{block_list.title}]({BASE_URL}/{block_list.file})"
            lines.append(f"{INDENT}{'  ' * depth}- {link}{suffix}")
            add(block_list.tag, depth + 1)

    add(None, 0)
    return "\n".join(lines)


def update(readme: str, database: Database) -> str:
    """Returns the README with the lists section regenerated."""
    pattern = re.compile(f"{re.escape(START)}\n.*?{re.escape(END)}", re.DOTALL)
    if not pattern.search(readme):
        raise ValueError(f"README must contain the {START} and {END} markers")
    block = f"{START}\n{render(database)}\n{INDENT}{END}"
    return pattern.sub(lambda _: block, readme, count=1)


def update_file(path: Path, database: Database) -> bool:
    """Updates the README in place and returns True if it changed."""
    current = path.read_text()
    updated = update(current, database)
    if updated != current:
        path.write_text(updated)
    return updated != current

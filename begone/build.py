"""Builds the Begone lists described in the YAML database."""

import plistlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

import yaml

from begone.arcep import NumberRange
from begone.ranges import PatternSet, range_to_pattern, sanitize

ALL_TAG = "all"
CATEGORY_BLOCKED = "0"
# Ranges shorter than this would block whole geographic areas.
MIN_PATTERN_LENGTH = 5


class RangeSource(Protocol):
    """Anything able to list the ranges of an operator, like ``ArcepClient``."""

    def ranges(self, mnemo: str) -> list[NumberRange]: ...


class ConfigError(ValueError):
    """Raised when the YAML database is inconsistent."""


@dataclass(frozen=True)
class BlockList:
    """A list published in ``dist/``."""

    tag: str
    file: str
    title: str
    parent: str | None = None
    recommended: bool = False


@dataclass(frozen=True)
class Operator:
    """A source of numbers: explicit patterns and/or ARCEP operator mnemonics."""

    title: str
    tags: tuple[str, ...]
    numbers: tuple[str, ...] = ()
    mnemos: tuple[str, ...] = ()


@dataclass(frozen=True)
class Database:
    """The content of the YAML database."""

    lists: tuple[BlockList, ...]
    operators: tuple[Operator, ...]


@dataclass
class Result:
    """The entries of every list, by tag."""

    entries: dict[str, list[dict[str, str]]] = field(default_factory=dict)
    empty_operators: list[str] = field(default_factory=list)


def load_database(path: Path) -> Database:
    """Loads and validates the YAML database."""
    raw: dict[str, Any] = yaml.safe_load(path.read_text())

    lists = tuple(
        BlockList(
            tag=tag,
            file=item["file"],
            title=item["title"],
            parent=item.get("parent"),
            recommended=item.get("recommended", False),
        )
        for tag, item in raw["lists"].items()
    )
    operators = tuple(
        Operator(
            title=item["title"],
            tags=tuple(item.get("tags", [])),
            numbers=tuple(item.get("numbers", [])),
            mnemos=tuple(item.get("mnemos", [])),
        )
        for item in raw["operators"]
    )
    database = Database(lists, operators)
    validate(database)
    return database


def validate(database: Database) -> None:
    """Checks that tags, lists and files are consistent."""
    errors = []
    tags = {block_list.tag for block_list in database.lists}
    used_tags = {tag for operator in database.operators for tag in operator.tags}

    if ALL_TAG not in tags:
        errors.append(f"a list with the '{ALL_TAG}' tag is required")
    for tag in sorted(used_tags - tags):
        errors.append(f"tag '{tag}' is used by an operator but has no list")
    for tag in sorted(tags - used_tags - {ALL_TAG}):
        errors.append(f"list '{tag}' has no operator")
    for block_list in database.lists:
        if block_list.parent and block_list.parent not in tags:
            errors.append(f"list '{block_list.tag}' has an unknown parent '{block_list.parent}'")
    files = [block_list.file for block_list in database.lists]
    for file in sorted({f for f in files if files.count(f) > 1}):
        errors.append(f"file '{file}' is used by several lists")
    for operator in database.operators:
        if not operator.numbers and not operator.mnemos:
            errors.append(f"operator '{operator.title}' has neither numbers nor mnemos")
        if not operator.tags:
            errors.append(f"operator '{operator.title}' has no tag")

    if errors:
        raise ConfigError("invalid database:\n- " + "\n- ".join(errors))


def _entry(title: str, number: str) -> dict[str, str]:
    return {"title": title, "addNational": "true", "category": CATEGORY_BLOCKED, "number": number}


def collect(database: Database, client: RangeSource) -> Result:
    """Resolves every operator into Begone entries, grouped by list tag.

    Operators are processed in order: a pattern already covered by a previous
    operator is skipped, so each number appears once in the complete list.
    """
    result = Result()
    seen = PatternSet()

    for operator in database.operators:
        patterns = [sanitize(number) for number in operator.numbers]
        for mnemo in operator.mnemos:
            ranges = client.ranges(mnemo)
            if not ranges:
                result.empty_operators.append(f"{operator.title} ({mnemo})")
            patterns += [sanitize(range_to_pattern(r.start, r.end)) for r in ranges]

        group = []
        for pattern in patterns:
            if len(pattern) < MIN_PATTERN_LENGTH or seen.covers(pattern):
                continue
            seen.add(pattern)
            group.append(_entry(operator.title, pattern))

        for tag in {*operator.tags, ALL_TAG}:
            result.entries.setdefault(tag, []).extend(group)

    for group in result.entries.values():
        group.sort(key=lambda entry: (entry["title"], entry["number"]))
    return result


def write(database: Database, result: Result, output_dir: Path) -> dict[str, int]:
    """Writes every list as a Begone plist file and returns their sizes."""
    output_dir.mkdir(parents=True, exist_ok=True)
    sizes = {}
    for block_list in database.lists:
        entries = result.entries.get(block_list.tag, [])
        with (output_dir / block_list.file).open("wb") as f:
            plistlib.dump(entries, f)
        sizes[block_list.file] = len(entries)
    return sizes


def read_list(path: Path) -> list[dict[str, str]]:
    """Reads a Begone plist file."""
    with path.open("rb") as f:
        entries: list[dict[str, str]] = plistlib.load(f)
    return entries

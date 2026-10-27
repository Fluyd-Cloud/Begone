"""Number pattern helpers.

A pattern is an E.164 number where trailing digits may be replaced by ``#``
wildcards, e.g. ``+33187680###`` matches ``+33187680000`` to ``+33187680999``.
"""

import re

WILDCARD = "#"


def sanitize(number: str) -> str:
    """Removes every character that is not part of a pattern (spaces, dots...)."""
    return re.sub(r"[^+0-9#]", "", number)


def to_international(number: str) -> str:
    """Converts a French national number (``0X...``) to its ``+33`` form."""
    return "+33" + number[1:] if number.startswith("0") else number


def range_to_pattern(start: str, end: str) -> str:
    """Builds the smallest pattern covering the ``start``-``end`` number range.

    The common prefix of both bounds is kept and the remaining digits are
    replaced by wildcards.
    """
    common_length = next(
        (i for i, (a, b) in enumerate(zip(start, end, strict=False)) if a != b),
        len(start),
    )
    pattern = start[:common_length] + WILDCARD * (len(start) - common_length)
    return to_international(pattern)


class PatternSet:
    """A set of patterns able to tell whether a pattern is already covered."""

    def __init__(self) -> None:
        self._prefixes: set[tuple[int, str]] = set()

    def covers(self, pattern: str) -> bool:
        """Returns True if every number matched by ``pattern`` is already matched."""
        prefix = pattern.rstrip(WILDCARD)
        return any((len(pattern), prefix[:i]) in self._prefixes for i in range(len(prefix) + 1))

    def add(self, pattern: str) -> None:
        """Adds a pattern to the set."""
        self._prefixes.add((len(pattern), pattern.rstrip(WILDCARD)))

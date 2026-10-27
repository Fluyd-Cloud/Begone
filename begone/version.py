"""Reads and bumps the ``begone.version`` file.

The first line is the version, bumped on structural changes (a new list, a new
operator), the second line is the build number, bumped on every update.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ListVersion:
    """The version of the published lists."""

    version: str
    build: int

    @classmethod
    def read(cls, path: Path) -> "ListVersion":
        version, build = path.read_text().split()
        return cls(version, int(build))

    def write(self, path: Path) -> None:
        path.write_text(f"{self.version}\n{self.build}")

    def bump(self, structural: bool = False) -> "ListVersion":
        """Returns the next version; ``structural`` also bumps the minor version."""
        version = self.version
        if structural:
            major, minor = version.split(".")
            version = f"{major}.{int(minor) + 1}"
        return ListVersion(version, self.build + 1)

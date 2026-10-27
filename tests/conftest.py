from pathlib import Path

import pytest

from begone.arcep import NumberRange

DATABASE = """
lists:
  spam:
    file: spam.xml
    title: Spam Numbers
    recommended: true
  voip:
    file: voip.xml
    title: VOIP Numbers
  acme:
    file: acme.xml
    title: Acme Numbers
    parent: voip
  all:
    file: full.xml
    title: Complete List
operators:
  - title: Démarchage
    tags: [spam]
    numbers: ['+33 1 62 ## ## ##']
  - title: Acme
    tags: [voip, acme]
    mnemos: [ACME]
"""

RANGES = {
    "ACME": [
        NumberRange("0187680000", "0187689999", "ACME"),
        NumberRange("0939080000", "0939080999", "ACME"),
        # Already covered by the Démarchage pattern.
        NumberRange("0162000000", "0162009999", "ACME"),
    ],
}


class FakeClient:
    def __init__(self, ranges: dict[str, list[NumberRange]] | None = None) -> None:
        self._ranges = RANGES if ranges is None else ranges

    def ranges(self, mnemo: str) -> list[NumberRange]:
        return self._ranges.get(mnemo, [])


@pytest.fixture
def database_file(tmp_path: Path) -> Path:
    path = tmp_path / "numbers.yaml"
    path.write_text(DATABASE)
    return path


@pytest.fixture
def client() -> FakeClient:
    return FakeClient()

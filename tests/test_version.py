from pathlib import Path

from begone.version import ListVersion


def test_bump(tmp_path: Path) -> None:
    path = tmp_path / "begone.version"
    path.write_text("1.3\n4")

    version = ListVersion.read(path)
    assert version.bump() == ListVersion("1.3", 5)
    assert version.bump(structural=True) == ListVersion("1.4", 5)

    version.bump().write(path)
    assert path.read_text() == "1.3\n5"

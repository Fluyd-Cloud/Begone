import plistlib
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from begone import build, cli
from tests.conftest import FakeClient

runner = CliRunner()


@pytest.fixture
def project(tmp_path: Path, database_file: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(cli, "ArcepClient", lambda **_: FakeClient())
    (tmp_path / "README.md").write_text("   <!-- lists:start -->\n   <!-- lists:end -->\n")
    (tmp_path / "begone.version").write_text("1.3\n4")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def invoke(*args: str) -> str:
    result = runner.invoke(cli.app, [*args, *(["--database", "numbers.yaml"] if args[0] != "bump" else [])])
    assert result.exit_code == 0, result.output
    return result.output


def test_build_then_check(project: Path) -> None:
    output = invoke("build")

    assert "3 dist/full.xml" in output
    assert "updated README.md" in output
    assert "[Acme Numbers]" in (project / "README.md").read_text()
    assert invoke("check") == "OK\n"


def test_check_detects_problems(project: Path) -> None:
    invoke("build")
    (project / "dist" / "acme.xml").unlink()
    (project / "dist" / "stale.xml").write_bytes(b"")

    result = runner.invoke(cli.app, ["check", "--database", "numbers.yaml"])

    assert result.exit_code == 1
    assert "dist/acme.xml is missing" in result.output
    assert "dist/stale.xml is not declared" in result.output


def test_build_fails_on_empty_operator(project: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "ArcepClient", lambda **_: FakeClient({}))

    result = runner.invoke(cli.app, ["build", "--database", "numbers.yaml"])

    assert result.exit_code == 1
    assert "no range found for: Acme (ACME)" in result.output


def test_diff(project: Path) -> None:
    invoke("build")
    shutil.copytree(project / "dist", project / "old")
    old = build.read_list(project / "old" / "acme.xml")
    with (project / "old" / "acme.xml").open("wb") as f:
        plistlib.dump([old[0], {**old[0], "number": "+33999######"}], f)

    output = invoke("diff", "old")

    assert "| Acme Numbers | `acme.xml` | 2 | +1 | -1 |" in output
    assert "VOIP" not in output


def test_bump(project: Path) -> None:
    assert invoke("bump", "--structural") == "1.4 (build 5)\n"
    assert (project / "begone.version").read_text() == "1.4\n5"

from pathlib import Path

import pytest

from begone.build import ConfigError, collect, load_database, read_list, write
from tests.conftest import FakeClient


def numbers(entries: list[dict[str, str]]) -> list[str]:
    return [entry["number"] for entry in entries]


def test_collect_groups_and_deduplicates(database_file: Path, client: FakeClient) -> None:
    result = collect(load_database(database_file), client)

    assert numbers(result.entries["spam"]) == ["+33162######"]
    assert numbers(result.entries["acme"]) == ["+3318768####", "+33939080###"]
    assert result.entries["voip"] == result.entries["acme"]
    assert numbers(result.entries["all"]) == ["+3318768####", "+33939080###", "+33162######"]
    assert result.entries["all"][0] == {
        "title": "Acme",
        "addNational": "true",
        "category": "0",
        "number": "+3318768####",
    }


def test_collect_reports_operators_without_ranges(database_file: Path) -> None:
    result = collect(load_database(database_file), FakeClient({}))

    assert result.empty_operators == ["Acme (ACME)"]


def test_write_plist(database_file: Path, client: FakeClient, tmp_path: Path) -> None:
    database = load_database(database_file)
    sizes = write(database, collect(database, client), tmp_path / "dist")

    assert sizes == {"spam.xml": 1, "voip.xml": 2, "acme.xml": 2, "full.xml": 3}
    assert numbers(read_list(tmp_path / "dist" / "acme.xml")) == ["+3318768####", "+33939080###"]


@pytest.mark.parametrize(
    ("before", "after", "error"),
    [
        ("tags: [voip, acme]", "tags: [voip, acmee]", "tag 'acmee' is used by an operator but has no list"),
        ("tags: [voip, acme]", "tags: [voip]", "list 'acme' has no operator"),
        ("parent: voip", "parent: vop", "unknown parent 'vop'"),
        ("file: voip.xml", "file: spam.xml", "file 'spam.xml' is used by several lists"),
        ("mnemos: [ACME]", "mnemos: []", "operator 'Acme' has neither numbers nor mnemos"),
    ],
)
def test_invalid_database(database_file: Path, before: str, after: str, error: str) -> None:
    database_file.write_text(database_file.read_text().replace(before, after))

    with pytest.raises(ConfigError, match=error):
        load_database(database_file)


def test_repository_database_is_valid() -> None:
    load_database(Path(__file__).parent.parent / "data" / "numbers.yaml")

from pathlib import Path

import pytest

from begone import readme
from begone.build import load_database

URL = readme.BASE_URL


def test_render_nests_children(database_file: Path) -> None:
    assert readme.render(load_database(database_file)) == "\n".join([
        f"   - [Spam Numbers]({URL}/spam.xml) (recommended)",
        f"   - [VOIP Numbers]({URL}/voip.xml)",
        f"     - [Acme Numbers]({URL}/acme.xml)",
        f"   - [Complete List]({URL}/full.xml)",
    ])


def test_update_replaces_section(database_file: Path) -> None:
    database = load_database(database_file)
    text = "intro\n   <!-- lists:start -->\n   - old\n   <!-- lists:end -->\noutro\n"

    updated = readme.update(text, database)

    assert updated.startswith("intro\n   <!-- lists:start -->\n   - [Spam Numbers]")
    assert updated.endswith("   <!-- lists:end -->\noutro\n")
    assert readme.update(updated, database) == updated


def test_update_requires_markers(database_file: Path) -> None:
    with pytest.raises(ValueError, match="markers"):
        readme.update("no markers", load_database(database_file))

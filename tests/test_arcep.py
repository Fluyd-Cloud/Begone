from pathlib import Path
from typing import Any

import pytest
import requests

from begone.arcep import API_URL, ArcepClient, ArcepError, NumberRange


class FakeResponse:
    def __init__(self, payload: Any) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        pass

    def json(self) -> Any:
        return self.payload


class FakeSession:
    """Returns the queued responses in order; exceptions are raised."""

    def __init__(self, responses: list[Any]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, Any]] = []

    def get(self, url: str, params: Any = None, timeout: float = 0) -> FakeResponse:
        self.calls.append((url, params))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return FakeResponse(response)


def row(start: str, end: str, mnemo: str = "GETG") -> dict[str, str]:
    return {"Tranche_Debut": start, "Tranche_Fin": end, "Mnémo": mnemo}


def page(rows: list[dict[str, str]], next_url: str | None = None) -> dict[str, Any]:
    return {"data": rows, "links": {"next": next_url}}


def client(responses: list[Any], **kwargs: Any) -> tuple[ArcepClient, FakeSession]:
    session = FakeSession(responses)
    return ArcepClient(session=session, backoff=0, **kwargs), session  # type: ignore[arg-type]


def test_ranges_follows_pages_and_retries() -> None:
    arcep, session = client([
        requests.ConnectionError("reset"),
        {"message": "rate limited"},
        page([row("0187680000", "0187689999")], next_url="https://next"),
        page([row("0939080000", "0939080999")]),
    ])

    assert arcep.ranges("GETG") == [
        NumberRange("0187680000", "0187689999", "GETG"),
        NumberRange("0939080000", "0939080999", "GETG"),
    ]
    assert session.calls[0] == (API_URL, {"Mnémo__exact": "GETG", "page_size": 50})
    assert session.calls[-1] == ("https://next", None)
    # Cached in memory.
    assert arcep.ranges("GETG") == arcep.ranges("GETG")
    assert len(session.calls) == 4


def test_ranges_gives_up() -> None:
    arcep, _ = client([requests.ConnectionError("reset")] * 3, retries=3)

    with pytest.raises(ArcepError, match="giving up"):
        arcep.ranges("GETG")


def test_ranges_disk_cache(tmp_path: Path) -> None:
    arcep, _ = client([page([row("0187680000", "0187689999")])], cache_dir=tmp_path)
    expected = arcep.ranges("GETG")

    offline, session = client([], cache_dir=tmp_path)
    assert offline.ranges("GETG") == expected
    assert session.calls == []


def test_lookup() -> None:
    arcep, _ = client([page([row("0187680000", "0187689999"), row("0187670000", "0187679999", "INIT")])])

    assert arcep.lookup("0187686887") == NumberRange("0187680000", "0187689999", "GETG")


def test_lookup_unallocated() -> None:
    arcep, _ = client([page([row("0187670000", "0187679999", "INIT")])])

    assert arcep.lookup("0187686887") is None

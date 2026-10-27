"""Client for the ARCEP numbering resources published on data.gouv.fr."""

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

RESOURCE_ID = "90e8bdd0-0f5c-47ac-bd39-5f46463eb806"
API_URL = f"https://tabular-api.data.gouv.fr/api/resources/{RESOURCE_ID}/data/"
PAGE_SIZE = 50


class ArcepError(RuntimeError):
    """Raised when the ARCEP API cannot be queried."""


@dataclass(frozen=True)
class NumberRange:
    """A number range allocated to an operator, in national format."""

    start: str
    end: str
    mnemo: str


class ArcepClient:
    """Fetches number ranges, with retries and an optional on-disk cache."""

    def __init__(
        self,
        cache_dir: Path | None = None,
        retries: int = 8,
        timeout: float = 30,
        backoff: float = 1,
        session: requests.Session | None = None,
    ) -> None:
        self.cache_dir = cache_dir
        self.retries = retries
        self.timeout = timeout
        self.backoff = backoff
        self.session = session or requests.Session()
        self._memory: dict[str, list[NumberRange]] = {}

    def _get(self, url: str, params: dict[str, str | int] | None = None) -> dict[str, Any]:
        """GETs a page of the API, retrying on network errors and bad responses."""
        error: Exception | None = None
        for attempt in range(self.retries):
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
                    raise ArcepError(f"unexpected response: {str(payload)[:200]}")
                return payload
            except (requests.RequestException, ValueError, ArcepError) as e:
                error = e
                delay = min(self.backoff * 2**attempt, 60)
                logger.warning("ARCEP request failed (%s), retrying in %ss", e, delay)
                time.sleep(delay)
        raise ArcepError(f"giving up on {url} after {self.retries} attempts") from error

    def _cache_file(self, mnemo: str) -> Path | None:
        return self.cache_dir / f"{mnemo}.json" if self.cache_dir else None

    def ranges(self, mnemo: str) -> list[NumberRange]:
        """Returns every number range allocated to the operator ``mnemo``."""
        if mnemo in self._memory:
            return self._memory[mnemo]

        cache_file = self._cache_file(mnemo)
        if cache_file and cache_file.exists():
            rows = json.loads(cache_file.read_text())
        else:
            rows = []
            url: str | None = API_URL
            params: dict[str, str | int] | None = {"Mnémo__exact": mnemo, "page_size": PAGE_SIZE}
            while url:
                page = self._get(url, params)
                rows.extend(page["data"])
                url = page.get("links", {}).get("next")
                params = None  # the next link already carries the query
            if cache_file:
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                cache_file.write_text(json.dumps(rows, ensure_ascii=False, indent=1))

        result = [NumberRange(row["Tranche_Debut"], row["Tranche_Fin"], row["Mnémo"]) for row in rows]
        self._memory[mnemo] = result
        return result

    def lookup(self, number: str) -> NumberRange | None:
        """Finds the range containing a national number (``0XXXXXXXXX``)."""
        page = self._get(
            API_URL,
            {"Tranche_Debut__less": number, "Tranche_Debut__sort": "desc", "page_size": PAGE_SIZE},
        )
        for row in page["data"]:
            start, end = row["Tranche_Debut"], row["Tranche_Fin"]
            if len(start) == len(number) and start <= number <= end:
                return NumberRange(start, end, row["Mnémo"])
        return None

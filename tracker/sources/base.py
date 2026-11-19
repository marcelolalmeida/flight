from __future__ import annotations

from typing import Protocol

from ..models import Flight, Watch


class Source(Protocol):
    airline: str

    def fetch(self, watch: Watch) -> list[Flight]:
        """Return all flights/fares found for the watch. Raise on failure."""
        ...

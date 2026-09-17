"""Provider contract: read precomputed facts, never train on request or startup."""

from typing import Protocol


class FactsProvider(Protocol):
    def get(self, section: str) -> dict | list: ...


class ReplayProvider:
    def get(self, section):
        from backend.api.models import Snapshot

        return Snapshot.objects.get(name=section).payload

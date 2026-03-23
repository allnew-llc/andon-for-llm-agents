# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Base class for vault event notifiers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class VaultEvent(Enum):
    """Types of vault events that can trigger notifications."""

    SYNC_OK = "sync_ok"
    SYNC_FAIL = "sync_fail"
    ROTATE = "rotate"
    ADD = "add"
    REMOVE = "remove"
    AUDIT_DRIFT = "audit_drift"
    AUDIT_OK = "audit_ok"


@dataclass
class EventPayload:
    """Payload for a vault event notification. Never contains secret values."""

    event: VaultEvent
    secret_name: str
    targets: list[str] = field(default_factory=list)
    ok_count: int = 0
    fail_count: int = 0
    message: str = ""


class Notifier(ABC):
    """Base class for sending vault event notifications."""

    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    @abstractmethod
    def notify(self, payload: EventPayload) -> bool:
        """Send a notification. Returns True on success. Never sends secret values."""

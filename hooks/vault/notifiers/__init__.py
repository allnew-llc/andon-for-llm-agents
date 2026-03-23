# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Notification integrations for vault events."""
from __future__ import annotations

from .base import Notifier, VaultEvent
from .datadog import DatadogNotifier
from .pagerduty import PagerDutyNotifier
from .slack import SlackNotifier
from .teams import TeamsNotifier

NOTIFIER_MAP: dict[str, type[Notifier]] = {
    "slack": SlackNotifier,
    "teams": TeamsNotifier,
    "datadog": DatadogNotifier,
    "pagerduty": PagerDutyNotifier,
}


def get_notifier(name: str, webhook_url: str) -> Notifier:
    """Return a notifier instance."""
    cls = NOTIFIER_MAP.get(name)
    if cls is None:
        supported = ", ".join(sorted(NOTIFIER_MAP.keys()))
        raise ValueError(f"Unknown notifier: {name} (supported: {supported})")
    return cls(webhook_url=webhook_url)


__all__ = [
    "Notifier",
    "VaultEvent",
    "SlackNotifier",
    "TeamsNotifier",
    "DatadogNotifier",
    "PagerDutyNotifier",
    "NOTIFIER_MAP",
    "get_notifier",
]

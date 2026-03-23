# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Platform drivers for secret deployment targets."""
from __future__ import annotations

from .base import PlatformDriver
from .cloudflare import CloudflarePagesDriver
from .local import LocalDriver
from .vercel import VercelDriver

DRIVER_MAP: dict[str, type[PlatformDriver]] = {
    "cloudflare-pages": CloudflarePagesDriver,
    "vercel": VercelDriver,
    "local": LocalDriver,
}


def get_driver(platform: str) -> PlatformDriver:
    """Return a driver instance for the given platform name."""
    cls = DRIVER_MAP.get(platform)
    if cls is None:
        raise ValueError(f"Unknown platform: {platform}")
    return cls()


__all__ = [
    "PlatformDriver",
    "CloudflarePagesDriver",
    "VercelDriver",
    "LocalDriver",
    "DRIVER_MAP",
    "get_driver",
]

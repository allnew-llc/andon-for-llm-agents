# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Platform drivers for secret deployment targets."""
from __future__ import annotations

from .aws_ssm import AWSSSMDriver
from .base import PlatformDriver
from .cloudflare import CloudflarePagesDriver
from .flyio import FlyIODriver
from .github import GitHubActionsDriver
from .heroku import HerokuDriver
from .local import LocalDriver
from .netlify import NetlifyDriver
from .vercel import VercelDriver

DRIVER_MAP: dict[str, type[PlatformDriver]] = {
    "cloudflare-pages": CloudflarePagesDriver,
    "vercel": VercelDriver,
    "local": LocalDriver,
    "github-actions": GitHubActionsDriver,
    "heroku": HerokuDriver,
    "netlify": NetlifyDriver,
    "flyio": FlyIODriver,
    "aws-ssm": AWSSSMDriver,
}


def get_driver(platform: str) -> PlatformDriver:
    """Return a driver instance for the given platform name."""
    cls = DRIVER_MAP.get(platform)
    if cls is None:
        supported = ", ".join(sorted(DRIVER_MAP.keys()))
        raise ValueError(f"Unknown platform: {platform} (supported: {supported})")
    return cls()


__all__ = [
    "PlatformDriver",
    "AWSSSMDriver",
    "CloudflarePagesDriver",
    "FlyIODriver",
    "GitHubActionsDriver",
    "HerokuDriver",
    "LocalDriver",
    "NetlifyDriver",
    "VercelDriver",
    "DRIVER_MAP",
    "get_driver",
]

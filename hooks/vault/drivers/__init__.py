# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Platform drivers for secret deployment targets."""
from __future__ import annotations

from .aws_ssm import AWSSSMDriver
from .azure import AzureKeyVaultDriver
from .base import PlatformDriver
from .cloudflare import CloudflarePagesDriver
from .digitalocean import DigitalOceanDriver
from .flyio import FlyIODriver
from .gcp import GCPSecretManagerDriver
from .github import GitHubActionsDriver
from .gitlab import GitLabCIDriver
from .heroku import HerokuDriver
from .local import LocalDriver
from .netlify import NetlifyDriver
from .railway import RailwayDriver
from .supabase import SupabaseDriver
from .vercel import VercelDriver

DRIVER_MAP: dict[str, type[PlatformDriver]] = {
    "aws-ssm": AWSSSMDriver,
    "azure-keyvault": AzureKeyVaultDriver,
    "cloudflare-pages": CloudflarePagesDriver,
    "digitalocean": DigitalOceanDriver,
    "flyio": FlyIODriver,
    "gcp-secrets": GCPSecretManagerDriver,
    "github-actions": GitHubActionsDriver,
    "gitlab-ci": GitLabCIDriver,
    "heroku": HerokuDriver,
    "local": LocalDriver,
    "netlify": NetlifyDriver,
    "railway": RailwayDriver,
    "supabase": SupabaseDriver,
    "vercel": VercelDriver,
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
    "AzureKeyVaultDriver",
    "CloudflarePagesDriver",
    "DigitalOceanDriver",
    "FlyIODriver",
    "GCPSecretManagerDriver",
    "GitHubActionsDriver",
    "GitLabCIDriver",
    "HerokuDriver",
    "LocalDriver",
    "NetlifyDriver",
    "RailwayDriver",
    "SupabaseDriver",
    "VercelDriver",
    "DRIVER_MAP",
    "get_driver",
]

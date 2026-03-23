# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Platform drivers for secret deployment targets."""
from __future__ import annotations

from .alibaba import AlibabaKMSDriver
from .aws_sm import AWSSecretsManagerDriver
from .aws_ssm import AWSSSMDriver
from .azure import AzureKeyVaultDriver
from .base import PlatformDriver
from .bitbucket import BitbucketPipelinesDriver
from .circleci import CircleCIDriver
from .cloudflare import CloudflarePagesDriver
from .digitalocean import DigitalOceanDriver
from .flyio import FlyIODriver
from .gcp import GCPSecretManagerDriver
from .github import GitHubActionsDriver
from .gitlab import GitLabCIDriver
from .heroku import HerokuDriver
from .huawei import HuaweiCSMSDriver
from .jdcloud import JDCloudKMSDriver
from .local import LocalDriver
from .naver import NaverCloudDriver
from .netlify import NetlifyDriver
from .nhn import NHNCloudDriver
from .railway import RailwayDriver
from .render import RenderDriver
from .sakura import SakuraCloudDriver
from .supabase import SupabaseDriver
from .tencent import TencentSSMDriver
from .terraform import TerraformCloudDriver
from .vercel import VercelDriver
from .volcengine import VolcengineKMSDriver

DRIVER_MAP: dict[str, type[PlatformDriver]] = {
    "alibaba-kms": AlibabaKMSDriver,
    "aws-secrets-manager": AWSSecretsManagerDriver,
    "aws-ssm": AWSSSMDriver,
    "azure-keyvault": AzureKeyVaultDriver,
    "bitbucket-pipelines": BitbucketPipelinesDriver,
    "circleci": CircleCIDriver,
    "cloudflare-pages": CloudflarePagesDriver,
    "digitalocean": DigitalOceanDriver,
    "flyio": FlyIODriver,
    "gcp-secrets": GCPSecretManagerDriver,
    "github-actions": GitHubActionsDriver,
    "gitlab-ci": GitLabCIDriver,
    "heroku": HerokuDriver,
    "huawei-csms": HuaweiCSMSDriver,
    "jdcloud-kms": JDCloudKMSDriver,
    "local": LocalDriver,
    "naver-cloud": NaverCloudDriver,
    "netlify": NetlifyDriver,
    "nhn-cloud": NHNCloudDriver,
    "railway": RailwayDriver,
    "render": RenderDriver,
    "sakura-cloud": SakuraCloudDriver,
    "supabase": SupabaseDriver,
    "tencent-ssm": TencentSSMDriver,
    "terraform-cloud": TerraformCloudDriver,
    "vercel": VercelDriver,
    "volcengine-kms": VolcengineKMSDriver,
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
    "AlibabaKMSDriver",
    "AWSSecretsManagerDriver",
    "AWSSSMDriver",
    "AzureKeyVaultDriver",
    "BitbucketPipelinesDriver",
    "CircleCIDriver",
    "CloudflarePagesDriver",
    "DigitalOceanDriver",
    "FlyIODriver",
    "GCPSecretManagerDriver",
    "GitHubActionsDriver",
    "GitLabCIDriver",
    "HerokuDriver",
    "HuaweiCSMSDriver",
    "JDCloudKMSDriver",
    "LocalDriver",
    "NaverCloudDriver",
    "NetlifyDriver",
    "NHNCloudDriver",
    "RailwayDriver",
    "RenderDriver",
    "SakuraCloudDriver",
    "SupabaseDriver",
    "TencentSSMDriver",
    "TerraformCloudDriver",
    "VercelDriver",
    "VolcengineKMSDriver",
    "DRIVER_MAP",
    "get_driver",
]

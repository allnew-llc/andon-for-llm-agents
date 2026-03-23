# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Platform drivers for secret deployment targets."""
from __future__ import annotations

from .alibaba import AlibabaKMSDriver
from .aws_sm import AWSSecretsManagerDriver
from .aws_ssm import AWSSSMDriver
from .azure import AzureKeyVaultDriver
from .azure_devops import AzureDevOpsDriver
from .base import PlatformDriver
from .bitbucket import BitbucketPipelinesDriver
from .circleci import CircleCIDriver
from .cloudflare import CloudflarePagesDriver
from .deno import DenoDeployDriver
from .digitalocean import DigitalOceanDriver
from .docker import DockerSwarmDriver
from .flyio import FlyIODriver
from .gcp import GCPSecretManagerDriver
from .github import GitHubActionsDriver
from .gitlab import GitLabCIDriver
from .hasura import HasuraCloudDriver
from .heroku import HerokuDriver
from .huawei import HuaweiCSMSDriver
from .jdcloud import JDCloudKMSDriver
from .kubernetes import KubernetesDriver
from .laravel_forge import LaravelForgeDriver
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
    # Cloud — Global
    "aws-secrets-manager": AWSSecretsManagerDriver,
    "aws-ssm": AWSSSMDriver,
    "azure-keyvault": AzureKeyVaultDriver,
    "gcp-secrets": GCPSecretManagerDriver,
    # Cloud — Asia
    "alibaba-kms": AlibabaKMSDriver,
    "huawei-csms": HuaweiCSMSDriver,
    "jdcloud-kms": JDCloudKMSDriver,
    "naver-cloud": NaverCloudDriver,
    "nhn-cloud": NHNCloudDriver,
    "sakura-cloud": SakuraCloudDriver,
    "tencent-ssm": TencentSSMDriver,
    "volcengine-kms": VolcengineKMSDriver,
    # PaaS / Hosting
    "cloudflare-pages": CloudflarePagesDriver,
    "digitalocean": DigitalOceanDriver,
    "flyio": FlyIODriver,
    "hasura-cloud": HasuraCloudDriver,
    "heroku": HerokuDriver,
    "laravel-forge": LaravelForgeDriver,
    "netlify": NetlifyDriver,
    "railway": RailwayDriver,
    "render": RenderDriver,
    "supabase": SupabaseDriver,
    "vercel": VercelDriver,
    "deno-deploy": DenoDeployDriver,
    # CI/CD
    "azure-devops": AzureDevOpsDriver,
    "bitbucket-pipelines": BitbucketPipelinesDriver,
    "circleci": CircleCIDriver,
    "github-actions": GitHubActionsDriver,
    "gitlab-ci": GitLabCIDriver,
    # IaC / Orchestration
    "docker-swarm": DockerSwarmDriver,
    "kubernetes": KubernetesDriver,
    "terraform-cloud": TerraformCloudDriver,
    # Local
    "local": LocalDriver,
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
    "DRIVER_MAP",
    "get_driver",
]

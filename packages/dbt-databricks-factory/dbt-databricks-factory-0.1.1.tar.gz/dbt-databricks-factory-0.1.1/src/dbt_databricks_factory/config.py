from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


@dataclass(frozen=True)
class ClusterConfig:
    """Cluster config."""

    existing_cluster_id: str | None = None
    job_cluster_key: str | None = None
    new_cluster: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.existing_cluster_id is not None and (self.job_cluster_key is not None or self.new_cluster is not None):
            raise ValueError("Either existing_cluster_id or job_cluster_key or new_cluster must be provided")
        if self.existing_cluster_id is None and self.job_cluster_key is None and self.new_cluster is None:
            raise ValueError("Either existing_cluster_id or job_cluster_key or new_cluster must be provided")

    def to_json(self) -> dict[str, Any]:
        """Convert cluster config to JSON.

        Returns:
            dict[str, Any]: Cluster config in JSON format.
        """
        if self.existing_cluster_id is not None:
            return {"existing_cluster_id": self.existing_cluster_id}
        config: dict[str, Any] = {}
        if self.job_cluster_key is not None:
            config.update({"job_cluster_key": self.job_cluster_key})
        if self.new_cluster is not None:
            config.update({"new_cluster": self.new_cluster})
        return config


@dataclass(frozen=True)
class LibrariesConfig:
    """Libraries config."""

    libraries: list[str]

    def to_json(self) -> dict[str, Any]:
        """Convert libraries config to JSON.

        Returns:
            dict[str, Any]: Libraries config in JSON format.
        """
        return {"libraries": [{"pypi": {"package": library}} for library in self.libraries]}


class GitProvider(Enum):
    """Git provider."""

    GITHUB = "gitHub"
    GITHUB_ENTERPRISE = "gitHubEnterprise"
    GITLAB = "gitLab"
    GITLAB_ENTERPRISE_EDITION = "gitLabEnterpriseEdition"
    BITBUCKET_SERVER = "bitbucketServer"
    BITBUCKET_CLOUD = "bitbucketCloud"
    AWS_CODE_COMMIT = "awsCodeCommit"
    AZURE_DEV_OPS_SERVICES = "azureDevOpsServices"


@dataclass(frozen=True)
class DbtProjectConfig:
    """Dbt project config."""

    project_dir: str
    profiles_dir: str
    git_url: str
    git_provider: GitProvider
    git_branch: str | None = None
    git_commit: str | None = None
    git_tag: str | None = None

    def __post_init__(self) -> None:
        if [self.git_branch, self.git_commit, self.git_tag].count(None) != 2:
            raise ValueError("Exactly one of git_branch or git_commit or git_tag must be provided")


@dataclass(frozen=True)
class DatabricksJobConfig:
    """Databricks job config."""

    job_name: str
    job_clusters: list[ClusterConfig]
    task_clusters: dict[str, ClusterConfig]
    libraries_config: LibrariesConfig
    default_task_cluster: ClusterConfig | None = None


@dataclass(frozen=True)
class ScheduleConfig:
    """Schedule config."""

    quartz_cron_expression: str
    timezone_id: str

    def to_json(self) -> dict[str, Any]:
        """Convert schedule config to JSON.

        Returns:
            dict[str, Any]: Schedule config in JSON format.
        """
        return {
            "schedule": {
                "quartz_cron_expression": self.quartz_cron_expression,
                "timezone_id": self.timezone_id,
            }
        }

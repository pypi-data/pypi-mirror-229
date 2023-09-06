from __future__ import annotations

import re
from enum import Enum
from typing import Any

from dbt_graph_builder.builder import (
    DbtManifestGraph,
    GraphConfiguration,
    create_tasks_graph,
    load_dbt_manifest,
)
from dbt_graph_builder.node_type import NodeType

from .config import DatabricksJobConfig, DbtProjectConfig, ScheduleConfig


class TaskType(Enum):
    """Task type enum."""

    RUN = "run"
    TEST = "test"


_normalize_node_name_regex = re.compile(r"[^a-zA-Z0-9_\-]")
_contract_node_name_regex = re.compile(r"_{2,}")


def normalize_node_name(node_name: str) -> str:
    """Normalize node name.

    Args:
        node_name (str): Node name.

    Returns:
        str: Normalized node name.
    """
    node_name = _normalize_node_name_regex.sub("_", node_name)
    node_name = _contract_node_name_regex.sub("_", node_name)
    return node_name.lower()


class DatabricksGraphBuilder:
    """Databricks graph builder."""

    def __init__(
        self,
        dbt_project_config: DbtProjectConfig,
        databricks_job_config: DatabricksJobConfig,
        schedule_config: ScheduleConfig | None = None,
    ):
        """Create a new instance of DatabricksGraphBuilder.

        Args:
            dbt_project_config (DbtProjectConfig): Dbt project config.
            databricks_job_config (DatabricksJobConfig): Databricks job config.
            schedule_config (ScheduleConfig, optional): Schedule configuration. Defaults to None.
        """
        self._dbt_project_config = dbt_project_config
        self._databricks_job_config = databricks_job_config
        self._schedule_config = schedule_config
        self._tasks_graph: DbtManifestGraph | None = None

    def build(
        self,
        path: str,
        graph_config: GraphConfiguration | None = None,
    ) -> dict[str, Any]:
        """Build Databricks job config.

        Args:
            path (str): Path to dbt project.
            graph_config (GraphConfiguration, optional): Graph configuration. Defaults to None.

        Returns:
            dict[str, Any]: Databricks job config.
        """
        self._tasks_graph = create_tasks_graph(load_dbt_manifest(path), graph_config)
        tasks: list[dict[str, Any]] = []
        for node in self._tasks_graph.get_graph_nodes():
            tasks.extend(self._build_task(node))
        self._tasks_graph = None
        return {
            "name": self._databricks_job_config.job_name,
            "tasks": tasks,
            "job_clusters": [cluster.to_json() for cluster in self._databricks_job_config.job_clusters],
            "git_source": self._git_source(),
            "format": "MULTI_TASK",
            **self._schedule(),
        }

    def _git_source(self) -> dict[str, Any]:
        git_source = {
            "git_url": self._dbt_project_config.git_url,
            "git_provider": self._dbt_project_config.git_provider.value,
        }
        if self._dbt_project_config.git_branch is not None:
            git_source["git_branch"] = self._dbt_project_config.git_branch
        if self._dbt_project_config.git_commit is not None:
            git_source["git_commit"] = self._dbt_project_config.git_commit
        if self._dbt_project_config.git_tag is not None:
            git_source["git_tag"] = self._dbt_project_config.git_tag
        return git_source

    def _schedule(self) -> dict[str, Any]:
        if self._schedule_config is None:
            return {}
        return self._schedule_config.to_json()

    def _build_task(self, node: tuple[str, dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
        if node[1]["node_type"] == NodeType.RUN_TEST:
            return (self._build_run_test_task(node, TaskType.RUN), self._build_run_test_task(node, TaskType.TEST))
        raise NotImplementedError(f"Node type {node[1]['node_type']} is not supported")

    def _build_run_test_task(self, node: tuple[str, dict[str, Any]], task_type: TaskType) -> dict[str, Any]:
        return {
            "task_key": f"{normalize_node_name(node[0])}-{task_type.value}",
            "dbt_task": {
                "project_directory": self._project_dir(),
                "commands": [
                    "dbt deps",
                    f"dbt {task_type.value} --profiles-dir {self._profiles_dir()} --select {node[1]['select']}",
                ],
            },
            **self._depends_on(node, task_type),
            **self._cluster_spec(node[0]),
        }

    def _depends_on(self, node: tuple[str, dict[str, Any]], task_type: TaskType) -> dict[str, Any]:
        if task_type == TaskType.RUN:
            predecessors: list[str] = list(self._tasks_graph.graph.predecessors(node[0]))  # type: ignore
            if not predecessors:
                return {}
            return {
                "depends_on": [{"task_key": f"{normalize_node_name(dependant)}-test"} for dependant in predecessors]
            }
        if task_type == TaskType.TEST:
            return {"depends_on": [{"task_key": f"{normalize_node_name(node[0])}-run"}]}
        raise NotImplementedError(f"Task type {task_type} is not supported")

    def _cluster_spec(self, node: str) -> dict[str, Any]:
        if (
            node not in self._databricks_job_config.task_clusters
            and self._databricks_job_config.default_task_cluster is None
        ):
            raise ValueError(f"Task cluster for node {node} is not defined")
        return {
            **self._databricks_job_config.libraries_config.to_json(),
            **self._databricks_job_config.task_clusters.get(  # type: ignore
                node, self._databricks_job_config.default_task_cluster
            ).to_json(),
        }

    def _profiles_dir(self) -> str:
        return self._dbt_project_config.profiles_dir

    def _project_dir(self) -> str:
        return self._dbt_project_config.project_dir

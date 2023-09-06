from __future__ import annotations

import json

import click

from .builder import DatabricksGraphBuilder
from .config import (
    ClusterConfig,
    DatabricksJobConfig,
    DbtProjectConfig,
    GitProvider,
    LibrariesConfig,
    ScheduleConfig,
)


@click.group()
def cli() -> None:
    """CLI entrypoint."""


@cli.command()
@click.argument(
    "manifest-file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
@click.option("--job-name", required=True, help="Name of the job to create.")
@click.option("--project-dir", required=True, help="Path to dbt project directory.")
@click.option("--profiles-dir", required=True, help="Path to dbt profiles directory.")
@click.option("--cron-schedule", help="Cron schedule for the job.")
@click.option("--job-cluster", multiple=True, type=click.Tuple([str, str]), help="Job cluster config.")
@click.option(
    "--task-cluster",
    multiple=True,
    type=click.Tuple([str, str]),
    help="Job cluster name or existing cluster id.",
)
@click.option("--default-task-cluster", help="Default task cluster name or existing cluster id.")
@click.option("--library", multiple=True, type=str, help="Libraries config.")
@click.option("--git-url", required=True, help="Git url.")
@click.option("--git-branch", help="Git branch.")
@click.option("--git-commit", help="Git commit.")
@click.option("--git-tag", help="Git tag.")
@click.option(
    "--git-provider",
    required=True,
    help="Git provider.",
    type=click.Choice([provider.value for provider in GitProvider]),
)
@click.option("--pretty", is_flag=True, help="Pretty print the output.")
def create_job(
    job_name: str,
    manifest_file: str,
    project_dir: str,
    profiles_dir: str,
    cron_schedule: str | None,
    job_cluster: list[tuple[str, str]],
    task_cluster: list[tuple[str, str]],
    default_task_cluster: str | None,
    library: list[str],
    git_url: str,
    git_branch: str | None,
    git_commit: str | None,
    git_tag: str | None,
    git_provider: str,
    pretty: bool,
) -> None:
    """Create a job."""  # noqa: DCO020, DCO050
    create_job_cli(
        job_name,
        manifest_file,
        project_dir,
        profiles_dir,
        cron_schedule,
        job_cluster,
        task_cluster,
        default_task_cluster,
        library,
        git_url,
        git_branch,
        git_commit,
        git_tag,
        git_provider,
        pretty,
    )


def create_job_cli(
    job_name: str,
    manifest_file: str,
    project_dir: str,
    profiles_dir: str,
    cron_schedule: str | None,
    job_cluster: list[tuple[str, str]],
    task_cluster: list[tuple[str, str]],
    default_task_cluster: str | None,
    library: list[str],
    git_url: str,
    git_branch: str | None,
    git_commit: str | None,
    git_tag: str | None,
    git_provider: str,
    pretty: bool,
    output_file: str | None = None,
) -> None:
    """Create a job.

    Args:
        job_name (str): Name of the job to create.
        manifest_file (str): Path to dbt manifest file.
        project_dir (str): Path to dbt project directory.
        profiles_dir (str): Path to dbt profiles directory.
        cron_schedule (str | None): Cron schedule for the job.
        job_cluster (list[tuple[str, str]]): Job cluster list. List contains of tuples of cluster names and config.
        task_cluster (list[tuple[str, str]]): Task cluster list. List contains of tuples of cluster names and config.
        default_task_cluster (str | None): Default task cluster name.
        library (list[str]): List of libraries.
        git_url (str): Git url.
        git_branch (str | None): Git branch.
        git_commit (str | None): Git commit.
        git_tag (str | None): Git tag.
        git_provider (str): Git provider.
        pretty (bool): Pretty print the output.
        output_file (str | None): Output file path.

    Raises:
        BadParameter: Either task cluster or default task cluster must be provided
    """
    if len(task_cluster) == 0 and default_task_cluster is None:
        raise click.BadParameter("Either task cluster or default task cluster must be provided")

    job_clusters: list[ClusterConfig] = []
    for cluster_key, new_cluster in job_cluster:
        if new_cluster is not None and new_cluster.startswith("@"):
            with open(new_cluster[1:]) as file:
                new_cluster = file.read()
        job_clusters.append(ClusterConfig(job_cluster_key=cluster_key, new_cluster=json.loads(new_cluster)))

    if default_task_cluster is not None:
        default_task_cluster_config = (
            ClusterConfig(job_cluster_key=default_task_cluster)
            if len(job_clusters)
            else ClusterConfig(existing_cluster_id=default_task_cluster)
        )
    else:
        default_task_cluster_config = None

    builder = DatabricksGraphBuilder(
        DbtProjectConfig(
            project_dir, profiles_dir, git_url, GitProvider(git_provider), git_branch, git_commit, git_tag
        ),
        DatabricksJobConfig(
            job_name,
            job_clusters=job_clusters,
            task_clusters={
                task: ClusterConfig(job_cluster_key=cluster)
                if len(job_clusters)
                else ClusterConfig(existing_cluster_id=cluster)
                for task, cluster in task_cluster
            },
            libraries_config=LibrariesConfig(library),
            default_task_cluster=default_task_cluster_config,
        ),
        schedule_config=ScheduleConfig(cron_schedule, "UTC") if cron_schedule is not None else None,
    )
    output = json.dumps(builder.build(manifest_file), indent=2 if pretty else None)
    if output_file is not None:
        with open(output_file, "w") as file:
            file.write(output)
    else:
        click.echo(output)


if __name__ == "__main__":
    cli()

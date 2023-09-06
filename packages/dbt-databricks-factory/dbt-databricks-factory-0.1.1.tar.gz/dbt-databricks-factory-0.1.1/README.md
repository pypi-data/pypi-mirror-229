# dbt-databricks-factory

[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue)](https://github.com/getindata/dbt-databricks-factory)
[![PyPI Version](https://badge.fury.io/py/dbt-databricks-factory.svg)](https://pypi.org/project/dbt-databricks-factory/)
[![Downloads](https://pepy.tech/badge/dbt-databricks-factory)](https://pepy.tech/project/dbt-databricks-factory)

Creates dbt based GCP workflows.

## Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install [dbt-databricks-factory](https://pypi.org/project/dbt-databricks-factory/) for [dp (data-pipelines-cli)]:

```bash
pip install dbt-databricks-factory
```


## Usage
To create a new dbt workflow json schema, run:
```bash
python -m dbt_databricks_factory.cli create-job \
    --job-name '<job name>' \
    --project-dir '<dbt project directory>' \
    --profiles-dir '<path to profiles directory>' \
    --git-provider '<git provider>' \
    --git-url 'https://url.to/repo.git' \
    --git-branch 'main' \
    --job-cluster my-cluster-name @path/to/cluster_config.json \
    --default-task-cluster my-cluster-name \
    --library 'dbt-databricks>=1.0.0,<2.0.0' \
    --library 'dbt-bigquery==1.3.0' \
    --pretty \
    path/to/dbt/manifest.json > workflow.json
```

This workflow will create a json file with the dbt workflow definition. You can then use it to create a new workflow in Databricks by for example post request like here:
```bash
curl --fail-with-body -X POST "${DATABRICKS_HOST}api/2.1/jobs/create" \
-H "Authorization: Bearer ${DATABRICKS_TOKEN}" \
-H "Content-Type: application/json" \
-d "@workflow.json" >job_id.json

echo "Job ID:"
cat job_id.json
curl --fail-with-body -X POST "${DATABRICKS_HOST}api/2.1/jobs/run-now" \
-H "Authorization: Bearer ${DATABRICKS_TOKEN}" \
-H "Content-Type: application/json" \
-d @job_id.json >run_id.json

echo "Run ID:"
cat run_id.json
curl --fail-with-body -X GET -G "${DATABRICKS_HOST}api/2.1/jobs/runs/get" \
-H "Authorization: Bearer ${DATABRICKS_TOKEN}" \
-d "run_id=$(jq -r '.run_id' < run_id.json)" >run_status.json

jq < run_status.json
```

To get more information about the command, run:
```bash
python -m dbt_databricks_factory.cli create-job --help
```

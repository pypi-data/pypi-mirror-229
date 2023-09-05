from typing import Callable

from airflow.models import Variable
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.decorators import task
from datetime import datetime
from docker.types import Mount


def build_flowpyter_task(task_name=None) -> Callable:
    import os

    container_notebook_dir = Variable.get(
        "container_notebook_dir", "/opt/airflow/notebooks"
    )
    container_template_dir = Variable.get(
        "container_template_dir", "/opt/airflow/templates"
    )

    @task.docker(
        image="flowminder/flowpyterlab:api-analyst-latest",
        task_id=task_name,
        mount_tmp_dir=False,
        mounts=[
            Mount(
                source=Variable.get("host_notebook_dir"),
                target=container_notebook_dir,
                type="bind",
            ),
            Mount(
                source=Variable.get("host_template_dir"),
                target=container_template_dir,
                type="bind",
            ),
        ],
        environment={
            "FLOWAPI_TOKEN": "{{ var.value.flowapi_token }}",
            "CONTAINER_NOTEBOOK_DIR": container_notebook_dir,
            "CONTAINER_TEMPLATE_DIR": container_template_dir
        },
        network_mode="container:flowapi",
        multiple_outputs=False,
    )
    # We need to include notebook_name and nb_paras args here because it isn't closing over the context for some
    # reason - could be to do with the wrapper? I'm wondering if functools.update_wrapper will solve this somehow.
    def this_task(
        execution_date=None,
        previous_notebook=None,
        nb_params=None,
        notebook_name=None,
    ):
        import os
        import papermill as pm

        container_notebook_dir = os.getenv(
            "CONTAINER_NOTEBOOK_DIR"
        )
        container_template_dir = os.getenv(
            "CONTAINER_TEMPLATE_DIR"
        )
        if nb_params is None:
            nb_params = {}
        if previous_notebook is not None:
            # Something causes xargs to be passed as either string or 1-length
            # list, but I can't tell what yet
            if type(previous_notebook) in (list, tuple):
                previous_notebook = previous_notebook[0]
            elif type(previous_notebook) is str:
                previous_notebook = previous_notebook

        context_params = {
            "execution_date": execution_date,
            "flowapi_url": "http://localhost:9090",  # TODO: Replace with env var
            "previous_notebook": previous_notebook,
        }
        context_params.update(nb_params)

        out_path = (
            f"{container_notebook_dir}/out/{notebook_name}-{execution_date}.ipynb"
        )
        in_path = f"{container_notebook_dir}/{notebook_name}.ipynb"
        pm.execute_notebook(
            in_path,
            out_path,
            parameters=context_params,
            progress_bar=False,
        )
        return out_path

    return this_task

from pathlib import Path

import pytest
from flowpytertask import build_flowpyter_task
from airflow import DAG
from airflow.utils.state import DagRunState, TaskInstanceState
from airflow.utils.types import DagRunType
from airflow.utils.db import initdb
from airflow.models.variable import Variable
from pendulum import datetime
from conftest import TEST_NOTEBOOK_DIR

TASK_ID = "test_task"

TEST_VAR_PATH = Path(__file__).parent / "test_vars.yml"



@pytest.fixture
def dag(monkeypatch):
    initdb()
    monkeypatch.setenv("FLOWAPI_TOKEN", "unused")
    Variable.set("flowapi_token", "unused")
    Variable.set("host_notebook_dir", TEST_NOTEBOOK_DIR)
    Variable.set("host_template_dir", TEST_NOTEBOOK_DIR)
    with DAG(
        start_date = datetime(2023, 1, 29),
        dag_id = "test_dag",
        schedule="@daily",
        catchup=False
    ) as dag:
        task = build_flowpyter_task("test_task")
        task(
            notebook_name = "test_nb"
        )
    return dag


def test_dag(dag, tmp_out_dir):
    """
    Tests the dag runs to the end
    Caution - if there is something wrong with the callback invocation, this test will show passing
    """
    print(TEST_VAR_PATH.read_text())

    def callback(context):
        pytest.fail()

    dag.on_failure_callback = callback
    dag.test(
        execution_date = datetime(2023, 1, 29),
        variable_file_path = str(TEST_VAR_PATH)
    )


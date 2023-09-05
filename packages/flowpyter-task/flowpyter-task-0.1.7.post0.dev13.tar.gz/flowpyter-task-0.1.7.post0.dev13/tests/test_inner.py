from flowpytertask import build_flowpyter_task
import datetime
from pathlib import Path

from conftest import TEST_NOTEBOOK_DIR

TEST_DAG_ID = "flowpytertask_test_dag"
TEST_TASK_ID = "flowpytertask_test_task"


START_DATE = datetime.datetime(2021, 9, 13)
END_DATE = datetime.timedelta(days=1)


def test_task_builder_inner(local_test_nbs, monkeypatch, tmp_out_dir):
    task = build_flowpyter_task("test_task")
    task.function(notebook_name="test_nb", nb_params={"input": "DEADBEEF"})
    assert (Path(TEST_NOTEBOOK_DIR) / "out" / "test_nb-None.ipynb").exists()
    assert (
        "DEADBEEF"
        in (Path(TEST_NOTEBOOK_DIR) / "out" / "test_nb-None.ipynb").read_text()
    )

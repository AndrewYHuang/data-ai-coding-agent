"""A smoke test: does the pipeline run end to end without crashing?

It says nothing about whether the numbers are *right* - that's your job in
exercise 03.

`tmp_path` is a pytest fixture: pytest sees the argument name and passes in a
fresh empty folder for each test, so we don't write into the real output/.
"""

from kettle.pipeline import run


def test_pipeline_runs_and_writes_outputs(tmp_path):
    summary = run("2026-09-14", data_dir="data", output_dir=tmp_path)

    assert (tmp_path / "warehouse.db").exists()
    assert (tmp_path / "daily_summary_2026-09-14.csv").exists()
    assert {row["branch"] for row in summary} == {"leeds", "manchester", "york", "dublin"}

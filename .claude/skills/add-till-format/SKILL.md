---
name: add-till-format
description: Use when adding a new Kettle & Crumb branch to the pipeline, or supporting a new till export format (CSV layout, JSON Lines, a new currency or price unit).
---

# Adding a branch or till format

Work test-first throughout. Run `uv run pytest` after each step.

## 1. Explore the new export

- Open the sample in `data/raw/tills/<branch>_<date>.<ext>` and compare it with an existing
  branch's export.
- Note: the file format, column order, timestamp format (UK day-first or ISO), price unit
  (pounds like `3.40` or pence like `340`), currency, how products are identified (names or
  SKUs), and how refunds appear.
- Check whether the branch has a Z-report row in `data/raw/z_reports.csv`. That's your
  end-to-end check.

## 2. Same layout as an existing CSV till

If the new till matches one already in `TILL_FORMATS` in `kettle/transform.py`, this is a
one-line change:

1. Add a test to `tests/test_clean_rows.py` with one hand-written row for the new branch.
2. Add the branch to `TILL_FORMATS` with the right `columns`, `price_unit` and `currency`.

## 3. A new CSV layout

1. Add a test with a hand-written row in the new layout. See it fail.
2. Add a new column list next to `STANDARD_COLUMNS`/`DUBLIN_COLUMNS`, and a `TILL_FORMATS`
   entry that uses it.
3. A new currency needs its rate read in `kettle/pipeline.py` (see how `dublin` uses
   `read_eur_rate`) and converted in `_clean_row`. Rates are "foreign currency per pound", so
   divide to convert to pence.

## 4. A new file format (like Edinburgh's JSON Lines)

1. Add a reader to `kettle/extract.py` (see `read_jsonl_till_export`).
2. Add a `clean_*` function to `kettle/transform.py` that returns rows with exactly the same
   keys as `clean_rows`, with tests in their own test file (see `tests/test_edinburgh.py`).
3. Register the branch in `kettle/pipeline.py`. A missing file for a branch that hasn't
   opened yet must be skipped, not crash the run.

## 5. Check end to end

- Run the pipeline for a date with the new branch's data:
  `uv run python -m kettle <date>`.
- Compare its line in `output/daily_summary_<date>.csv` with its Z-report.
  `tests/test_reconciliation.py` does this for every branch and date.

## Don'ts

- Don't modify anything in `data/raw/`.
- Don't copy and paste an existing branch's code path. Extend `TILL_FORMATS` or reuse the helpers.
- Don't change how the existing branches are processed.

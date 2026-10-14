# Handover notes

Hi! Some notes on the nightly pipeline before I go. It's all pretty straightforward.
— Andy

## What it does

- Picks up every till file in `data/raw/tills/` for the given date, so new branches get
  included automatically.
- Cleans each row: parses the date, converts prices to pence, and matches product names
  against the catalogue in `data/reference/products.json`.
- Converts Dublin's sales from euros to pounds using that day's rate.
- Removes duplicate rows. The tills sometimes export the same line twice.
- Some tills export negative quantities by mistake, so the pipeline takes `abs()` of the
  quantity to fix them.
- Loads everything into `output/warehouse.db` and writes `output/daily_summary_<date>.csv`.

## Running it

```
pip install pytest
python -m kettle 2026-09-14
python -m pytest
```

Re-running a day is safe. It replaces that day's rows in the warehouse instead of adding them
twice.

## Other bits

- The summary is emailed to the ops manager at 6am by a scheduled task on the old office
  server.
- The Z-reports in `data/raw/` are what Finance reconciles against. The pipeline doesn't
  use them.
- I never got round to finishing the helper functions at the bottom of `transform.py`.

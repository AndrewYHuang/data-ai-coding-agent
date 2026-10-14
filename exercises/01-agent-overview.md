# Pipeline overview (AI-generated)

> Before leaving, Andy asked an AI agent to "write an overview of this codebase for whoever
> takes over". This is what it produced, pasted in unedited.

---

## What it does

Kettle & Crumb's nightly pipeline turns each branch's till export into a clean warehouse table
and a daily summary for operations. It's a small, well-organised Python package with a classic
extract → transform → load structure.

```
python -m kettle 2026-09-14
```

## Structure

| Module | Responsibility |
|---|---|
| `kettle/pipeline.py` | Orchestrates the run. It picks up every till file in `data/raw/tills/` for the given date, so new branches are included automatically. |
| `kettle/extract.py` | Reads the till CSVs, the daily exchange rates and the product catalogue (`data/reference/products.json`). |
| `kettle/transform.py` | `clean_rows` standardises each row (see below). |
| `kettle/load.py` | Loads the cleaned rows into the `sales` table in `output/warehouse.db`. Re-running a day is safe, because that day's rows are replaced, not duplicated. |
| `kettle/report.py` | Writes `output/daily_summary_<date>.csv` with `date`, `branch`, `transactions`, `items_sold` and `revenue_gbp` for each branch. |

## The journey of a till row

Take this row from `data/raw/tills/leeds_2026-09-14.csv`:

```
LDS-0914-0001,14/09/2026 07:01,T2, Americano ,1,3.00
```

1. **Extract:** the CSV is read and the header row is skipped.
2. **Timestamp:** Leeds uses UK day-first dates, so `14/09/2026 07:01` is parsed as 14th
   September 2026, 07:01.
3. **Quantity:** some tills export negative quantities by mistake, so the pipeline takes the
   absolute value to correct them.
4. **Price:** `unit_price` is in pounds, and is converted to integer pence (`3.00` → `300`) to
   avoid floating-point errors in totals.
5. **Product name:** `" Americano "` is trimmed and matched against the product catalogue, so
   that spelling variants such as `flat-white` and `FLAT WHITE` are all stored as the same
   product.
6. **De-duplication:** the tills sometimes export the same line twice, and these exact
   duplicates are removed.
7. **Error handling:** rows with bad data are handled gracefully by the error handling in
   `clean_rows`, so one bad row can't crash the nightly run.
8. **Load and report:** the cleaned row is inserted into `sales` and counted in Leeds' line of
   the daily summary.

## How the branches differ

All four till exports are CSVs with a `unit_price` column in pounds. The differences are:

- **Leeds and York** use UK day-first timestamps (`14/09/2026 07:01`).
- **Manchester** uses ISO timestamps (`2026-09-14T07:20:00`).
- **Dublin** uses ISO timestamps and has its columns in a different order. Its prices are in
  euros, and are converted to pounds using that day's exchange rate from
  `data/raw/exchange_rates/`.

## Data files read by the pipeline

- `data/raw/tills/*.csv`: the till exports
- `data/raw/exchange_rates/<date>.json`: daily exchange rates
- `data/reference/products.json`: the product catalogue

## Running it

```
pip install pytest
python -m kettle 2026-09-14
python -m pytest
```

The daily summary is emailed to the operations manager at 6am each morning.

## Summary

The pipeline is in good shape. Each stage has one clear responsibility, data quality is
handled centrally in `clean_rows`, and the warehouse load is idempotent. The main gap is test
coverage. The helper functions at the bottom of `transform.py` were started but not finished.

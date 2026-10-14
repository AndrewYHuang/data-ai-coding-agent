# Handover notes

Hi! Some notes on the nightly pipeline before I go. I got an AI agent to write most of this up
from the code and my notes, and pasted it in as is. It's all pretty straightforward.
— Andy

---

## What it does

The pipeline turns each branch's till export into a clean warehouse table and a daily summary
for operations, in a classic extract → transform → load structure:

| Module | Responsibility |
|---|---|
| `kettle/pipeline.py` | Runs everything. It picks up every till file in `data/raw/tills/` for the date, so new branches are included automatically. |
| `kettle/extract.py` | Reads the till CSVs, the daily exchange rates and the product catalogue (`data/reference/products.json`). |
| `kettle/transform.py` | `clean_rows` standardises each row (see below). |
| `kettle/load.py` | Loads rows into the `sales` table in `output/warehouse.db`. Re-running a day is safe, because that day's rows are replaced, not duplicated. |
| `kettle/report.py` | Writes `output/daily_summary_<date>.csv` with `date`, `branch`, `transactions`, `items_sold` and `revenue_gbp` for each branch. |

## What happens to a till row

1. **Timestamp:** Leeds and York use UK day-first dates, so `14/09/2026 07:01` is 14th
   September.
2. **Quantity:** some tills export negative quantities by mistake, so the pipeline takes the
   absolute value to correct them.
3. **Price:** converted to integer pence (`3.00` → `300`), so totals don't suffer from
   floating-point errors.
4. **Product name:** trimmed and matched against the product catalogue, so variants such as
   `flat-white` and `FLAT WHITE` are stored as the same product.
5. **De-duplication:** the tills sometimes export the same line twice. These exact duplicates
   are removed.
6. **Error handling:** rows with bad data are handled gracefully, so one bad row can't crash
   the nightly run.

## How the branches differ

All four till exports are CSVs with a `unit_price` column in pounds.

- **Leeds and York** use UK day-first timestamps.
- **Manchester** uses ISO timestamps (`2026-09-14T07:20:00`).
- **Dublin** uses ISO timestamps and has its columns in a different order. Its prices are in
  euros, and are converted to pounds using that day's rate from `data/raw/exchange_rates/`.

The pipeline reads the till exports, the exchange rates and the product catalogue. The
Z-reports in `data/raw/` are what Finance reconciles against; the pipeline doesn't use them.

## Running it

```
pip install pytest
python -m kettle 2026-09-14
python -m pytest
```

The daily summary is emailed to the ops manager at 6am by a scheduled task on the old office
server.

## State of things

The pipeline is in good shape. Each stage has one clear job, data quality is handled centrally
in `clean_rows`, and the warehouse load is idempotent. The main gap is tests: I never got round
to finishing the helper functions at the bottom of `transform.py`.

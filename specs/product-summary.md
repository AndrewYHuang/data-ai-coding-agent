# Spec: product summary report

**Requested by:** head office
**Status:** agreed

## Purpose

Head office wants to see what each branch sells each day, by product, so they can plan stock
and compare branches.

## Output

The nightly run writes `output/product_summary_<date>.csv` alongside the daily summary.

| Column | Example | Notes |
|---|---|---|
| `date` | `2026-09-14` | The run date |
| `branch` | `leeds` | Lower case, as in the daily summary |
| `category` | `Coffee` | From `data/reference/products.json` |
| `product` | `Flat White` | The catalogue name, never the raw till spelling |
| `items_sold` | `31` | Net quantity: refunds are subtracted |
| `revenue_gbp` | `105.40` | Net revenue in pounds, 2 decimal places, refunds subtracted |

## Rules

1. There is one row per branch and product that had any sales or refunds that day.
2. Products with no sales or refunds at a branch that day are left out.
3. A product that was sold and then fully refunded still gets a row, with `items_sold` 0 and
   `revenue_gbp` `0.00`.
4. Rows are sorted by branch, then category, then product, all alphabetically.
5. Refunds (negative quantities) reduce `items_sold` and `revenue_gbp`.
6. Rows the pipeline can't match to the catalogue are already skipped during cleaning, so they
   never appear here.
7. A branch with no data for the day (e.g. Edinburgh before it opened) has no rows.
8. Money is calculated in integer pence and only formatted as pounds when the file is written.

## How we know it's right

For every branch, the `items_sold` and `revenue_gbp` in the product summary add up to that
branch's `items_sold` and `revenue_gbp` in `daily_summary_<date>.csv`.

## Out of scope

- Totals across all branches. Head office will add these up in a spreadsheet.
- Breakdowns by hour or by till.

# Kettle & Crumb nightly sales pipeline

Python ETL: till exports in `data/raw/tills/` → `kettle/` (extract, transform, load, report)
→ `output/warehouse.db` and `output/daily_summary_<date>.csv`.

## Commands

Always use `uv run` for Python, never `pip install` or bare `python`/`pytest`.

- Tests: `uv run pytest`
- Pipeline: `uv run python -m kettle 2026-09-14`
- Lint: `uv run ruff check`
- Add a dependency: `uv add <package>` (or `uv add --dev <package>`)

## Data rules

- Never modify anything in `data/raw/`. It's the source of truth from the tills.
- Don't read `data/raw/loyalty_members.csv`. It holds customers' personal data.
- Money is held as integer pence, never floats. Parse prices with `parse_price_to_pence`.
- UK till dates are day first (`DD/MM/YYYY`).
- Negative quantities are refunds, not errors.
- The Z-reports in `data/raw/z_reports.csv` are the ground truth for daily totals.
  `tests/test_reconciliation.py` checks we match them.

## Working style

- Test first: write a failing test, see it fail, then make it pass.
- Run `uv run pytest` before every commit.
- To add a new branch or till format, use the `add-till-format` skill.

"""Characterisation tests for build_summary (exercise 03, part A)."""

from kettle.report import build_summary


def sale(txn, branch, quantity, line_total):
    return {
        "transaction_id": txn,
        "branch": branch,
        "quantity": quantity,
        "line_total_pence": line_total,
    }


def test_build_summary_totals_each_branch():
    rows = [
        sale("LDS-1", "leeds", 1, 340),
        sale("LDS-1", "leeds", 2, 520),
        sale("LDS-2", "leeds", 1, 300),
        sale("YRK-1", "york", 1, 450),
    ]

    assert build_summary(rows, "2026-09-14") == [
        {"date": "2026-09-14", "branch": "leeds", "transactions": 2, "items_sold": 4,
         "revenue_gbp": "11.60"},
        {"date": "2026-09-14", "branch": "york", "transactions": 1, "items_sold": 1,
         "revenue_gbp": "4.50"},
    ]


def test_build_summary_with_no_rows_is_empty():
    assert build_summary([], "2026-09-14") == []

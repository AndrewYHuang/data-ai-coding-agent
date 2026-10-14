"""Tests for clean_rows.

These started as characterisation tests in exercise 03 part A. As each bug
was fixed (KC-101, KC-102, KC-103) the "BUG?" tests were changed to say what
*should* happen.
"""

import json

from kettle.transform import clean_rows

with open("data/reference/products.json", encoding="utf-8") as f:
    PRODUCTS = json.load(f)

LEEDS_ROW = ["LDS-0914-0001", "14/09/2026 07:01", "T2", " Americano ", "1", "3.00"]


def test_leeds_row_is_cleaned():
    assert clean_rows([LEEDS_ROW], "leeds", PRODUCTS) == [
        {
            "transaction_id": "LDS-0914-0001",
            "branch": "leeds",
            "sold_at": "2026-09-14T07:01:00",
            "till_id": "T2",
            "product": "Americano",
            "quantity": 1,
            "unit_price_pence": 300,
            "line_total_pence": 300,
        }
    ]


def test_uk_dates_are_day_first():
    row = ["LDS-0201-0001", "01/02/2026 09:00", "T1", "Latte", "1", "3.50"]
    [cleaned] = clean_rows([row], "leeds", PRODUCTS)
    assert cleaned["sold_at"] == "2026-02-01T09:00:00"


def test_manchester_prices_are_already_pence():
    row = ["MAN-0914-0001", "2026-09-14T07:20:00", "T1", "Latte", "2", "350"]
    [cleaned] = clean_rows([row], "manchester", PRODUCTS)
    assert cleaned["unit_price_pence"] == 350
    assert cleaned["line_total_pence"] == 700


def test_dublin_columns_are_reordered_and_converted_to_pounds():
    # KC-101: €11.71 at 1.1712 EUR per GBP is £10.00
    row = ["2026-09-14T08:00:00", "Flat White", "11.71", "1", "T1", "DUB-0914-0001"]
    [cleaned] = clean_rows([row], "dublin", PRODUCTS, eur_rate=1.1712)
    assert cleaned["transaction_id"] == "DUB-0914-0001"
    assert cleaned["product"] == "Flat White"
    assert cleaned["unit_price_pence"] == 1000


def test_product_names_are_matched_to_the_catalogue():
    # KC-103
    rows = [
        ["LDS-0914-0002", "14/09/2026 07:11", "T1", "flat-white", "1", "3.40"],
        ["LDS-0914-0003", "14/09/2026 07:12", "T1", "Flat Wht", "1", "3.40"],
    ]
    cleaned = clean_rows(rows, "leeds", PRODUCTS)
    assert [row["product"] for row in cleaned] == ["Flat White", "Flat White"]


def test_refund_keeps_its_negative_quantity():
    # KC-102: a refund reduces the totals
    row = ["LDS-0914-0024", "14/09/2026 08:38", "T1", "Hot Chocolate", "-1", "3.20"]
    [cleaned] = clean_rows([row], "leeds", PRODUCTS)
    assert cleaned["quantity"] == -1
    assert cleaned["line_total_pence"] == -320


def test_exact_duplicate_row_is_dropped():
    assert len(clean_rows([LEEDS_ROW, list(LEEDS_ROW)], "leeds", PRODUCTS)) == 1


def test_different_sales_of_same_product_in_same_minute_are_both_kept():
    # KC-102: two different transactions must both count
    other_sale = ["LDS-0914-0099", "14/09/2026 07:01", "T1", "Americano", "1", "3.00"]
    assert len(clean_rows([LEEDS_ROW, other_sale], "leeds", PRODUCTS)) == 2


def test_blank_and_unparseable_rows_are_skipped_with_a_warning(capsys):
    rows = [
        [],
        ["LDS-0914-0003", "14/09/2026 07:20", "T1", "Latte", "two", "3.50"],
        ["LDS-0914-0004", "14/09/2026 07:21", "T1", "Latte", "1", "N/A"],
        ["LDS-0914-0005", "14/09/2026 07:22", "T1", "Latte", "1"],
        LEEDS_ROW,
    ]
    assert len(clean_rows(rows, "leeds", PRODUCTS)) == 1
    assert capsys.readouterr().out.count("skipping bad leeds row") == 3


def test_row_with_unknown_or_missing_product_is_skipped():
    # KC-103: a sale of nothing shouldn't reach the warehouse
    rows = [
        ["LDS-0914-0005", "14/09/2026 07:30", "T1", "", "1", "3.40"],
        ["LDS-0914-0006", "14/09/2026 07:31", "T1", "Mocha", "1", "3.40"],
    ]
    assert clean_rows(rows, "leeds", PRODUCTS) == []

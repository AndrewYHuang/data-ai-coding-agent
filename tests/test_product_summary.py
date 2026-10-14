"""Tests for the product summary (exercise 05). One test per rule in specs/product-summary.md."""

import csv
import json
from collections import defaultdict
from decimal import Decimal

from kettle.pipeline import run
from kettle.report import build_product_summary

with open("data/reference/products.json", encoding="utf-8") as f:
    PRODUCTS = json.load(f)


def sale(branch, product, quantity, unit_price, txn="T-1"):
    return {
        "transaction_id": txn,
        "branch": branch,
        "product": product,
        "quantity": quantity,
        "line_total_pence": quantity * unit_price,
    }


def test_one_row_per_branch_and_product_with_category():
    # Rules 1 and 2
    rows = [
        sale("leeds", "Flat White", 1, 340),
        sale("leeds", "Flat White", 2, 340),
        sale("york", "Croissant", 1, 260),
    ]
    assert build_product_summary(rows, PRODUCTS, "2026-09-14") == [
        {"date": "2026-09-14", "branch": "leeds", "category": "Coffee",
         "product": "Flat White", "items_sold": 3, "revenue_gbp": "10.20"},
        {"date": "2026-09-14", "branch": "york", "category": "Bakery",
         "product": "Croissant", "items_sold": 1, "revenue_gbp": "2.60"},
    ]


def test_fully_refunded_product_still_has_a_row():
    # Rule 3
    rows = [sale("leeds", "Latte", 1, 350), sale("leeds", "Latte", -1, 350)]
    [row] = build_product_summary(rows, PRODUCTS, "2026-09-14")
    assert row["items_sold"] == 0
    assert row["revenue_gbp"] == "0.00"


def test_rows_sorted_by_branch_category_product():
    # Rule 4
    rows = [
        sale("york", "Latte", 1, 350),
        sale("leeds", "Latte", 1, 350),
        sale("leeds", "Croissant", 1, 260),
        sale("leeds", "Americano", 1, 300),
    ]
    summary = build_product_summary(rows, PRODUCTS, "2026-09-14")
    assert [(r["branch"], r["product"]) for r in summary] == [
        ("leeds", "Croissant"),  # Bakery
        ("leeds", "Americano"),  # Coffee
        ("leeds", "Latte"),  # Coffee
        ("york", "Latte"),
    ]


def test_refunds_reduce_totals():
    # Rule 5
    rows = [sale("leeds", "Latte", 3, 350), sale("leeds", "Latte", -1, 350)]
    [row] = build_product_summary(rows, PRODUCTS, "2026-09-14")
    assert row["items_sold"] == 2
    assert row["revenue_gbp"] == "7.00"


def test_no_rows_for_a_branch_with_no_data(tmp_path):
    # Rule 7: Edinburgh opened on the 16th
    run("2026-09-14", output_dir=tmp_path)
    with open(tmp_path / "product_summary_2026-09-14.csv", encoding="utf-8") as f:
        branches = {row["branch"] for row in csv.DictReader(f)}
    assert branches == {"leeds", "manchester", "york", "dublin"}


def test_product_summary_adds_up_to_daily_summary(tmp_path):
    # "How we know it's right"
    for date in ["2026-09-14", "2026-09-15", "2026-09-16"]:
        daily = {row["branch"]: row for row in run(date, output_dir=tmp_path)}

        totals = defaultdict(lambda: [0, Decimal(0)])
        with open(tmp_path / f"product_summary_{date}.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                totals[row["branch"]][0] += int(row["items_sold"])
                totals[row["branch"]][1] += Decimal(row["revenue_gbp"])

        for branch, (items, revenue) in totals.items():
            assert items == daily[branch]["items_sold"], (date, branch)
            assert revenue == Decimal(daily[branch]["revenue_gbp"]), (date, branch)

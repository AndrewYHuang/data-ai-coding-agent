"""Edinburgh's JSON Lines till (exercise 03, part C / KC-104)."""

import json

from kettle.pipeline import run
from kettle.transform import clean_jsonl_transactions

with open("data/reference/products.json", encoding="utf-8") as f:
    PRODUCTS = json.load(f)


def transaction(*items, txn="EDI-0916-0001"):
    return {
        "transaction_id": txn,
        "timestamp": "2026-09-16T08:03:00",
        "till": "T1",
        "items": [{"sku": sku, "qty": qty, "price_pence": price} for sku, qty, price in items],
    }


def test_each_item_becomes_a_row_named_from_the_catalogue():
    rows = clean_jsonl_transactions(
        [transaction(("FW01", 1, 340), ("CR01", 2, 260))], "edinburgh", PRODUCTS
    )

    assert rows == [
        {"transaction_id": "EDI-0916-0001", "branch": "edinburgh",
         "sold_at": "2026-09-16T08:03:00", "till_id": "T1", "product": "Flat White",
         "quantity": 1, "unit_price_pence": 340, "line_total_pence": 340},
        {"transaction_id": "EDI-0916-0001", "branch": "edinburgh",
         "sold_at": "2026-09-16T08:03:00", "till_id": "T1", "product": "Croissant",
         "quantity": 2, "unit_price_pence": 260, "line_total_pence": 520},
    ]


def test_refunds_keep_their_negative_quantity():
    [row] = clean_jsonl_transactions([transaction(("LT01", -1, 350))], "edinburgh", PRODUCTS)
    assert row["quantity"] == -1
    assert row["line_total_pence"] == -350


def test_unknown_sku_is_skipped():
    rows = clean_jsonl_transactions(
        [transaction(("XX99", 1, 100), ("LT01", 1, 350))], "edinburgh", PRODUCTS
    )
    assert [row["product"] for row in rows] == ["Latte"]


def test_pipeline_skips_edinburgh_before_it_opens(tmp_path):
    summary = run("2026-09-14", data_dir="data", output_dir=tmp_path)
    assert "edinburgh" not in {row["branch"] for row in summary}


def test_pipeline_matches_edinburghs_z_report_on_opening_day(tmp_path):
    summary = run("2026-09-16", data_dir="data", output_dir=tmp_path)

    [edinburgh] = [row for row in summary if row["branch"] == "edinburgh"]
    # From data/raw/z_reports.csv
    assert edinburgh["transactions"] == 120
    assert edinburgh["items_sold"] == 207
    assert edinburgh["revenue_gbp"] == "664.00"

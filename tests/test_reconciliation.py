"""Reconcile the daily summary against each till's Z-report (KC-102).

GBP branches must match to the penny. Dublin's Z-report is in euros, and we
convert each item's price separately, so its pounds total can differ from
"Z-report total / rate" by a few pence of rounding.
"""

import csv
import json
from decimal import Decimal

import pytest

from kettle.pipeline import run

with open("data/raw/z_reports.csv", encoding="utf-8") as f:
    Z_REPORTS = list(csv.DictReader(f))


@pytest.mark.parametrize("date", sorted({z["date"] for z in Z_REPORTS}))
def test_summary_matches_z_reports(date, tmp_path):
    summary = {row["branch"]: row for row in run(date, output_dir=tmp_path)}

    for z in [z for z in Z_REPORTS if z["date"] == date]:
        ours = summary[z["branch"]]
        assert ours["transactions"] == int(z["transactions"]), z["branch"]
        assert ours["items_sold"] == int(z["items_sold"]), z["branch"]

        if z["currency"] == "GBP":
            assert ours["revenue_gbp"] == z["net_sales"], z["branch"]
        else:
            with open(f"data/raw/exchange_rates/{date}.json", encoding="utf-8") as f:
                rate = Decimal(str(json.load(f)["rates"][z["currency"]]))
            expected = Decimal(z["net_sales"]) / rate
            assert abs(Decimal(ours["revenue_gbp"]) - expected) < Decimal("0.50"), z["branch"]

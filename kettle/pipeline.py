import os

from kettle.extract import read_eur_rate, read_jsonl_till_export, read_products, read_till_export
from kettle.load import load_sales
from kettle.report import build_summary, write_summary
from kettle.transform import TILL_FORMATS, clean_jsonl_transactions, clean_rows

BRANCHES = list(TILL_FORMATS)

# Branches whose tills export JSON Lines. They may not have opened yet on a
# given date, so a missing file is skipped rather than treated as an error.
JSONL_BRANCHES = ["edinburgh"]


def run(date, data_dir="data", output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    products = read_products(data_dir)

    all_rows = []
    for branch in BRANCHES:
        print("Processing " + branch + "...")
        rows = read_till_export(data_dir, branch, date)
        rate = None
        if branch == "dublin":
            rate = read_eur_rate(data_dir, date)
        cleaned = clean_rows(rows, branch, products, rate)
        print("  " + str(len(cleaned)) + " rows")
        all_rows = all_rows + cleaned

    for branch in JSONL_BRANCHES:
        print("Processing " + branch + "...")
        try:
            transactions = read_jsonl_till_export(data_dir, branch, date)
        except FileNotFoundError:
            print("  no till export for " + date + ", skipping")
            continue
        cleaned = clean_jsonl_transactions(transactions, branch, products)
        print("  " + str(len(cleaned)) + " rows")
        all_rows = all_rows + cleaned

    load_sales(all_rows, output_dir, date)
    summary = build_summary(all_rows, date)
    path = write_summary(summary, output_dir, date)
    print("Done! Summary written to " + path)
    return summary

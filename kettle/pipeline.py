import os

from kettle.extract import read_eur_rate, read_till_export
from kettle.load import load_sales
from kettle.report import build_summary, write_summary
from kettle.transform import clean_rows

BRANCHES = ["leeds", "manchester", "york", "dublin"]


def run(date, data_dir="data", output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)

    all_rows = []
    for branch in BRANCHES:
        print("Processing " + branch + "...")
        rows = read_till_export(data_dir, branch, date)
        rate = None
        if branch == "dublin":
            rate = read_eur_rate(data_dir, date)
        cleaned = clean_rows(rows, branch, rate)
        print("  " + str(len(cleaned)) + " rows")
        all_rows = all_rows + cleaned

    load_sales(all_rows, output_dir, date)
    summary = build_summary(all_rows, date)
    path = write_summary(summary, output_dir, date)
    print("Done! Summary written to " + path)
    return summary

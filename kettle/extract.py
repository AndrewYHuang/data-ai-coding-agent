import csv
import json
import os


def read_till_export(data_dir, branch, date):
    path = os.path.join(data_dir, "raw", "tills", branch + "_" + date + ".csv")
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    return rows[1:]  # skip header


def read_jsonl_till_export(data_dir, branch, date):
    """Read a JSON Lines till export: one transaction per line."""
    path = os.path.join(data_dir, "raw", "tills", branch + "_" + date + ".jsonl")
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def read_products(data_dir):
    path = os.path.join(data_dir, "reference", "products.json")
    with open(path) as f:
        return json.load(f)


def read_eur_rate(data_dir, date):
    path = os.path.join(data_dir, "raw", "exchange_rates", date + ".json")
    with open(path) as f:
        data = json.load(f)
    return data["rates"]["EUR"]

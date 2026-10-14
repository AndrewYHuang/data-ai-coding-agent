import csv
import json
import os


def read_till_export(data_dir, branch, date):
    path = os.path.join(data_dir, "raw", "tills", branch + "_" + date + ".csv")
    f = open(path, encoding="utf-8")
    rows = list(csv.reader(f))
    return rows[1:]  # skip header


def read_products(data_dir):
    path = os.path.join(data_dir, "reference", "products.json")
    with open(path) as f:
        return json.load(f)


def read_eur_rate(data_dir, date):
    path = os.path.join(data_dir, "raw", "exchange_rates", date + ".json")
    with open(path) as f:
        data = json.load(f)
    return data["rates"]["EUR"]

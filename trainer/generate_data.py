"""Generate the synthetic Kettle & Crumb dataset.

Usage (from the repo root):  uv run python trainer/generate_data.py [output_root]

Deterministic (seeded): re-running it reproduces data/ byte for byte. Writes
data/raw/** and data/reference/products.json under output_root (default: the
current directory) and prints the Z-report figures used in TICKETS.md.

If you change anything here, re-check every figure in TICKETS.md and
trainer/TRAINER_NOTES.md.
"""

import csv
import json
import random
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

SEED = 20260914
DATES = ["2026-09-14", "2026-09-15", "2026-09-16"]
EUR_RATES = {"2026-09-14": 1.1712, "2026-09-15": 1.1698, "2026-09-16": 1.1735}
USD_RATES = {"2026-09-14": 1.3521, "2026-09-15": 1.3498, "2026-09-16": 1.3544}

PRODUCTS = [
    # id, name, category, price_pence, euro_cents, aliases, weight
    ("FW01", "Flat White", "Coffee", 340, 395, ["flat wht"], 14),
    ("LT01", "Latte", "Coffee", 350, 410, ["caffe latte"], 14),
    ("CP01", "Cappuccino", "Coffee", 350, 410, ["cappucino"], 10),
    ("AM01", "Americano", "Coffee", 300, 350, [], 10),
    ("ES01", "Espresso", "Coffee", 240, 280, [], 4),
    ("TE01", "Breakfast Tea", "Tea", 220, 260, ["tea", "english breakfast"], 7),
    ("HC01", "Hot Chocolate", "Other Drinks", 320, 375, ["hot choc"], 5),
    ("CR01", "Croissant", "Bakery", 260, 300, [], 8),
    ("PC01", "Pain au Chocolat", "Bakery", 280, 330, ["pain au choc"], 6),
    ("CB01", "Cinnamon Bun", "Bakery", 310, 365, [], 6),
    ("BR01", "Bacon Roll", "Food", 450, 525, ["bacon butty"], 5),
    ("BB01", "Banana Bread", "Bakery", 290, 340, [], 4),
]

BRANCHES = {
    # branch: (txn prefix, format, transactions per day)
    "leeds": ("LDS", "uk", 140),
    "manchester": ("MAN", "pence", 170),
    "york": ("YRK", "uk", 110),
    "dublin": ("DUB", "eur", 130),
}
EDINBURGH_OPENS = "2026-09-16"

HEADER = ["transaction_id", "timestamp", "till_id", "product", "quantity", "unit_price"]
DUBLIN_HEADER = ["timestamp", "product", "unit_price", "quantity", "till_id", "transaction_id"]


def random_time(rng, date):
    """Opening 07:00-17:00, busy at morning and lunch rush."""
    r = rng.random()
    if r < 0.35:
        minutes = rng.randint(8 * 60, 9 * 60 + 30)
    elif r < 0.65:
        minutes = rng.randint(12 * 60, 13 * 60 + 30)
    else:
        minutes = rng.randint(7 * 60, 17 * 60 - 1)
    return datetime.fromisoformat(date) + timedelta(minutes=minutes)


def messy_name(rng, product):
    _, name, _, _, _, aliases, _ = product
    r = rng.random()
    if r < 0.72:
        return name
    choices = [
        name.upper(),
        name.lower(),
        name.lower().replace(" ", "-"),
        f" {name} ",
        f"{name}  ",
    ]
    if aliases:
        choices.append(aliases[0].title())
    return rng.choice(choices)


def build_transactions(rng, date, prefix, count):
    weights = [p[6] for p in PRODUCTS]
    times = sorted(random_time(rng, date) for _ in range(count))
    transactions = []
    for n, ts in enumerate(times, start=1):
        txn_id = f"{prefix}-{date[5:7]}{date[8:10]}-{n:04d}"
        till = rng.choice(["T1", "T2"])
        if rng.random() < 0.03 and transactions:
            # Refund of a single item
            product = rng.choices(PRODUCTS, weights)[0]
            lines = [(product, -1)]
        else:
            n_lines = rng.choices([1, 2, 3], [55, 33, 12])[0]
            chosen = []
            while len(chosen) < n_lines:
                p = rng.choices(PRODUCTS, weights)[0]
                if p not in chosen:
                    chosen.append(p)
            lines = [(p, rng.choices([1, 2, 3], [85, 12, 3])[0]) for p in chosen]
        transactions.append((txn_id, ts, till, lines))
    return transactions


def write_csv_branch(rng, root, branch, date, transactions, fmt):
    rows = []
    valid = []  # (txn_id, qty, local_minor_units)
    for txn_id, ts, till, lines in transactions:
        for product, qty in lines:
            pid, name, cat, pence, cents, aliases, _ = product
            display = messy_name(rng, product)
            if fmt == "uk":
                ts_s = ts.strftime("%d/%m/%Y %H:%M")
                price_s = f"{pence / 100:.2f}"
                minor = pence
                row = [txn_id, ts_s, till, display, str(qty), price_s]
            elif fmt == "pence":
                ts_s = ts.strftime("%Y-%m-%dT%H:%M:%S")
                minor = pence
                row = [txn_id, ts_s, till, display, str(qty), str(pence)]
            else:  # eur
                ts_s = ts.strftime("%Y-%m-%dT%H:%M:%S")
                minor = cents
                row = [ts_s, display, f"{cents / 100:.2f}", str(qty), till, txn_id]
            rows.append(row)
            valid.append((txn_id, qty, minor))
            if rng.random() < 0.012:
                rows.append(list(row))  # export glitch: exact duplicate line

    # Corrupt lines the till occasionally emits (not real sales)
    for _ in range(2):
        idx = rng.randrange(len(rows))
        template = list(rows[idx])
        kind = rng.choice(["qty", "product", "price"])
        qty_i, prod_i, price_i = (3, 1, 2) if fmt == "eur" else (4, 3, 5)
        if kind == "qty":
            template[qty_i] = rng.choice(["", "two"])
        elif kind == "product":
            template[prod_i] = ""
        else:
            template[price_i] = "N/A"
        rows.insert(idx + 1, template)
    # Blank lines
    for _ in range(2):
        rows.insert(rng.randrange(len(rows)), [])

    path = root / "data" / "raw" / "tills" / f"{branch}_{date}.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(DUBLIN_HEADER if fmt == "eur" else HEADER)
        writer.writerows(rows)
    return valid


def write_edinburgh(rng, root, date, transactions):
    path = root / "data" / "raw" / "tills" / f"edinburgh_{date}.jsonl"
    valid = []
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for txn_id, ts, till, lines in transactions:
            items = [{"sku": p[0], "qty": qty, "price_pence": p[3]} for p, qty in lines]
            record = {
                "transaction_id": txn_id,
                "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
                "till": till,
                "items": items,
            }
            f.write(json.dumps(record) + "\n")
            valid.extend((txn_id, qty, p[3]) for p, qty in lines)
    return valid


def z_report(branch, date, currency, valid):
    net_minor = sum(qty * minor for _, qty, minor in valid)
    return {
        "date": date,
        "branch": branch,
        "currency": currency,
        "transactions": len({t for t, _, _ in valid}),
        "items_sold": sum(q for _, q, _ in valid),
        "net_sales": f"{Decimal(net_minor) / 100:.2f}",
    }


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


def main(root):
    root = Path(root)
    rng = random.Random(SEED)
    for sub in ["data/raw/tills", "data/raw/exchange_rates", "data/reference"]:
        (root / sub).mkdir(parents=True, exist_ok=True)

    products = [
        {"id": pid, "name": name, "category": cat, "price_pence": pence, "aliases": aliases}
        for pid, name, cat, pence, _, aliases, _ in PRODUCTS
    ]
    write_json(root / "data/reference/products.json", products)

    z_reports = []
    for date in DATES:
        rates = {
            "base": "GBP",
            "date": date,
            "rates": {"EUR": EUR_RATES[date], "USD": USD_RATES[date]},
        }
        write_json(root / f"data/raw/exchange_rates/{date}.json", rates)

        for branch, (prefix, fmt, count) in BRANCHES.items():
            txns = build_transactions(rng, date, prefix, count + rng.randint(-15, 15))
            valid = write_csv_branch(rng, root, branch, date, txns, fmt)
            z_reports.append(z_report(branch, date, "EUR" if fmt == "eur" else "GBP", valid))

        if date >= EDINBURGH_OPENS:
            txns = build_transactions(rng, date, "EDI", 120)
            valid = write_edinburgh(rng, root, date, txns)
            z_reports.append(z_report("edinburgh", date, "GBP", valid))

    with (root / "data/raw/z_reports.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(z_reports[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(z_reports)

    write_loyalty(rng, root)
    for z in z_reports:
        print(z)


FIRST = ["Aoife", "Ben", "Chloe", "Dev", "Ella", "Finn", "Grace", "Hamza", "Isla", "Jack",
         "Kiran", "Leah", "Mohammed", "Niamh", "Oscar", "Priya", "Rory", "Sophie", "Tom", "Zara"]
LAST = ["Ahmed", "Byrne", "Clarke", "Davies", "Evans", "Fitzgerald", "Green", "Hughes", "Iqbal",
        "Jones", "Kelly", "Lewis", "Murphy", "Nolan", "O'Brien", "Patel", "Quinn", "Roberts",
        "Smith", "Taylor"]
POSTCODES = {"leeds": "LS1", "manchester": "M1", "york": "YO1", "dublin": "D02"}
LETTERS = "ABDEFGHJLNPQRSTUWXYZ"


def write_loyalty(rng, root):
    """Fake customer data: the hook for the permissions part of exercise 04."""
    path = root / "data/raw/loyalty_members.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["member_id", "first_name", "last_name", "email", "postcode",
                         "home_branch", "joined"])
        for i in range(1, 61):
            first, last = rng.choice(FIRST), rng.choice(LAST)
            branch = rng.choice(list(POSTCODES))
            email = f"{first.lower()}.{last.lower().replace(chr(39), '')}{rng.randint(1, 99)}@example.com"
            postcode = (f"{POSTCODES[branch]} {rng.randint(1, 9)}"
                        f"{rng.choice(LETTERS)}{rng.choice(LETTERS)}")
            joined = f"2025-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}"
            writer.writerow([f"KC{i:05d}", first, last, email, postcode, branch, joined])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")

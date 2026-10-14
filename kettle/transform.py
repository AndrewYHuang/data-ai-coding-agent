from datetime import datetime
from decimal import Decimal, InvalidOperation

STANDARD_COLUMNS = ["transaction_id", "timestamp", "till_id", "product", "quantity", "unit_price"]
DUBLIN_COLUMNS = ["timestamp", "product", "unit_price", "quantity", "till_id", "transaction_id"]

# How each branch's till lays out its CSV export. "price_unit" is passed to
# parse_price_to_pence: "pounds" means prices like 3.40 (in the branch's
# currency), "pence" means prices like 340.
TILL_FORMATS = {
    "leeds": {"columns": STANDARD_COLUMNS, "price_unit": "pounds", "currency": "GBP"},
    "manchester": {"columns": STANDARD_COLUMNS, "price_unit": "pence", "currency": "GBP"},
    "york": {"columns": STANDARD_COLUMNS, "price_unit": "pounds", "currency": "GBP"},
    "dublin": {"columns": DUBLIN_COLUMNS, "price_unit": "pounds", "currency": "EUR"},
}


def clean_rows(rows, branch, products, eur_rate=None):
    """Turn a branch's raw CSV rows into sales rows, in pence and catalogue names.

    Blank lines and exact duplicate lines are dropped. Rows that can't be
    parsed, or whose product isn't in the catalogue, are skipped with a warning.
    """
    till = TILL_FORMATS[branch]
    cleaned = []
    seen = set()
    for row in rows:
        if not row or not row[0]:
            continue

        # The tills sometimes export the exact same line twice. Two different
        # sales can share a minute and a product, so only an identical line
        # counts as a duplicate.
        key = tuple(row)
        if key in seen:
            continue
        seen.add(key)

        try:
            fields = dict(zip(till["columns"], row, strict=True))
            cleaned.append(_clean_row(fields, branch, till, products, eur_rate))
        except ValueError as error:
            print(f"  skipping bad {branch} row {row}: {error}")
    return cleaned


def _clean_row(fields, branch, till, products, eur_rate):
    product = normalise_product_name(fields["product"], products)
    if product is None:
        raise ValueError(f"unknown product {fields['product']!r}")

    price_pence = parse_price_to_pence(fields["unit_price"], till["price_unit"])
    if till["currency"] == "EUR":
        # The rate is euros per pound, so divide to go from euro cents to pence
        price_pence = round(price_pence / eur_rate)

    # Negative quantities are refunds, so keep the sign
    quantity = int(fields["quantity"])

    return {
        "transaction_id": fields["transaction_id"],
        "branch": branch,
        "sold_at": parse_till_timestamp(fields["timestamp"]).isoformat(),
        "till_id": fields["till_id"],
        "product": product,
        "quantity": quantity,
        "unit_price_pence": price_pence,
        "line_total_pence": quantity * price_pence,
    }


def clean_jsonl_transactions(transactions, branch, products):
    """Flatten JSON Lines till transactions into one sales row per item.

    These tills export product SKUs, which are looked up in the catalogue.
    Items with an unknown SKU are skipped with a warning.
    """
    names_by_sku = {product["id"]: product["name"] for product in products}
    cleaned = []
    for txn in transactions:
        sold_at = parse_till_timestamp(txn["timestamp"])
        for item in txn["items"]:
            name = names_by_sku.get(item["sku"])
            if name is None:
                print(f"  skipping unknown SKU {item['sku']!r} in {txn['transaction_id']}")
                continue
            cleaned.append({
                "transaction_id": txn["transaction_id"],
                "branch": branch,
                "sold_at": sold_at.isoformat(),
                "till_id": txn["till"],
                "product": name,
                "quantity": item["qty"],
                "unit_price_pence": item["price_pence"],
                "line_total_pence": item["qty"] * item["price_pence"],
            })
    return cleaned


def format_pence(pence):
    """Format an integer number of pence as a pounds string for reports.

    >>> format_pence(340)
    '£3.40'
    >>> format_pence(-120)
    '-£1.20'
    """
    sign = "-" if pence < 0 else ""
    pounds, pennies = divmod(abs(pence), 100)
    return f"{sign}£{pounds}.{pennies:02d}"


def parse_price_to_pence(value, unit):
    """Turn a till price string into an integer number of pence (or cents).

    `unit` is "pounds" for tills that export prices like "3.40" and "pence"
    for tills that export prices like "340". Surrounding whitespace is ignored.
    Raise ValueError if the value is not a valid price (including fractions
    of a penny, e.g. "3.405" pounds or "340.5" pence).
    """
    value = value.strip()
    if unit == "pence":
        if not value.isdigit():
            raise ValueError(f"Invalid pence price: {value!r}")
        return int(value)

    # Decimal, not float: float("4.35") * 100 is 434.99999999999994
    try:
        pence = Decimal(value) * 100
    except InvalidOperation:
        raise ValueError(f"Invalid price: {value!r}") from None
    if not pence.is_finite() or pence != pence.to_integral_value():
        raise ValueError(f"Invalid price: {value!r}")
    return int(pence)


def parse_till_timestamp(value):
    """Parse a till timestamp into a datetime.

    Accepts the UK format "14/09/2026 08:15" (day first!) and ISO 8601
    ("2026-09-14T08:15:00"). Surrounding whitespace is ignored.
    Raise ValueError for anything else.
    """
    value = value.strip()
    try:
        return datetime.strptime(value, "%d/%m/%Y %H:%M")
    except ValueError:
        return datetime.fromisoformat(value)


def normalise_product_name(raw_name, products):
    """Match a messy till product name to its canonical catalogue name.

    `products` is the list loaded from data/reference/products.json. Matching
    ignores case, surrounding whitespace and hyphens-vs-spaces, and also
    checks each product's aliases. Return None if there is no match.

    >>> normalise_product_name(" flat-white ", products)
    'Flat White'
    """
    target = _match_key(raw_name)
    if not target:
        return None
    for product in products:
        names = [product["name"], *product["aliases"]]
        if target in (_match_key(name) for name in names):
            return product["name"]
    return None


def _match_key(name):
    return " ".join(name.replace("-", " ").lower().split())

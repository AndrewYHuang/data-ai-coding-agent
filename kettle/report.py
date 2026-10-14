import csv
import os


def build_summary(rows, date):
    summary = {}
    for r in rows:
        b = r["branch"]
        if b not in summary:
            summary[b] = {"date": date, "branch": b, "txns": set(), "items_sold": 0, "revenue": 0}
        summary[b]["txns"].add(r["transaction_id"])
        summary[b]["items_sold"] += r["quantity"]
        summary[b]["revenue"] += r["line_total_pence"]

    result = []
    for s in summary.values():
        result.append({
            "date": s["date"],
            "branch": s["branch"],
            "transactions": len(s["txns"]),
            "items_sold": s["items_sold"],
            "revenue_gbp": "%.2f" % (s["revenue"] / 100),
        })
    return result


def build_product_summary(rows, products, date):
    """Net sales per branch and product. See specs/product-summary.md."""
    categories = {product["name"]: product["category"] for product in products}
    totals = {}
    for r in rows:
        key = (r["branch"], categories[r["product"]], r["product"])
        items, pence = totals.get(key, (0, 0))
        totals[key] = (items + r["quantity"], pence + r["line_total_pence"])

    return [
        {
            "date": date,
            "branch": branch,
            "category": category,
            "product": product,
            "items_sold": items,
            "revenue_gbp": "%.2f" % (pence / 100),
        }
        for (branch, category, product), (items, pence) in sorted(totals.items())
    ]


def write_product_summary(product_summary, output_dir, date):
    path = os.path.join(output_dir, "product_summary_" + date + ".csv")
    fieldnames = ["date", "branch", "category", "product", "items_sold", "revenue_gbp"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(product_summary)
    return path


def write_summary(summary, output_dir, date):
    path = os.path.join(output_dir, "daily_summary_" + date + ".csv")
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "branch", "transactions", "items_sold", "revenue_gbp"])
        w.writeheader()
        for row in summary:
            w.writerow(row)
    return path

# Open tickets

---

### KC-101: Dublin's revenue looks far too high

**Raised by:** Siobhán (Dublin branch manager)

> The daily summary says Dublin took **£917.66** on Monday 14th September. Our till's end-of-day
> Z-report says **€790.85**, and euros are worth less than pounds! Head office thinks we're
> the best branch in the chain, but we really aren't. Can you check the conversion?

*Hint: the Z-reports for every branch and day are in `data/raw/z_reports.csv`, and the
exchange rates are in `data/raw/exchange_rates/`.*

---

### KC-102: Totals don't quite match the tills anywhere

**Raised by:** Priya (Finance)

> I reconciled the summary against the Z-reports for the 14th. It's never far out, but it's
> never right either: Leeds is £12.90 short, York is £13.60 over. Manchester is out too.
> Some days the transaction counts don't match either. I need these to reconcile to the penny.

---

### KC-103: Product names are a mess in the warehouse

**Raised by:** Tom (Operations)

> I tried to count flat whites in the warehouse and found "Flat White", "Flat-White",
> "Flat Wht"... and some sales with no product name at all. We have a product catalogue in
> `data/reference/products.json`, so can the warehouse use those names?

---

### KC-104: Edinburgh opens on Wednesday 16th September

**Raised by:** Ops leadership

> Our fifth branch opens in Edinburgh on the 16th. It has a new till system, which exports
> **JSON Lines** (one JSON object per transaction) instead of CSV, and uses product **SKUs**
> rather than names. A sample is in `data/raw/tills/edinburgh_2026-09-16.jsonl`. Edinburgh
> must be in the daily summary from day one. There is no Edinburgh file before the 16th, and
> the pipeline must not crash on those days.

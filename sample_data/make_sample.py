"""Generate sales_2026.csv: 12,480 rows, Jan-Sep 2026. Deterministic. Electronics drops in Sep, mostly South."""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 12480
products = {
    "Electronics": [("Earbuds X2", 1999), ("Smartwatch Lite", 3499), ("Power Bank 20k", 1299), ("Bluetooth Speaker", 2199)],
    "Grocery": [("Millet Mix 1kg", 249), ("Cold Press Oil 1L", 549), ("Basmati Rice 5kg", 699)],
    "Apparel": [("Cotton Shirt", 899), ("Denim Jeans", 1599), ("Kurta Set", 1299)],
    "Home": [("Steel Bottle", 499), ("LED Lamp", 799), ("Bedsheet Set", 1499)],
}
regions = ["South", "North", "East", "West"]
days = pd.date_range("2026-01-01", "2026-09-30")
rows = []
for _ in range(N):
    cat = rng.choice(list(products), p=[.3, .3, .2, .2])
    prod, price = products[cat][rng.integers(len(products[cat]))]
    reg = rng.choice(regions, p=[.35, .25, .2, .2])
    d = days[rng.integers(len(days))]
    units = int(rng.integers(1, 12))
    disc = float(rng.choice([0, .05, .10, .15], p=[.4, .25, .25, .1]))
    rows.append((d, reg, cat, prod, units, price, disc))
df = pd.DataFrame(rows, columns=["order_date", "region", "category", "product", "units", "unit_price", "discount"])
# The story: September electronics slump, driven by South + two products
slump = (df.order_date.dt.month == 9) & (df.category == "Electronics") & (df.region == "South") & df["product"].isin(["Earbuds X2", "Smartwatch Lite"])
sep_elec = (df.order_date.dt.month == 9) & (df.category == "Electronics")
r = rng.random(len(df))
df = df[~((slump & (r < .85)) | (sep_elec & ~slump & (r < .2)))]
# keep non-Electronics months steady: even out Grocery noise by fixed seed (no extra change)
df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")
out = Path(__file__).with_name("sales_2026.csv")
df.sort_values("order_date").to_csv(out, index=False)
print(f"wrote {out} ({len(df)} rows)")

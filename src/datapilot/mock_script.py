"""Offline MOCK mode: scripted replies that still run REAL code in the sandbox (incl. a real KeyError + fix).
Numbers in the final answer are computed from the uploaded CSV, so they are true. Labelled MOCK in the UI."""
from __future__ import annotations

import pandas as pd

BUG = '''# filename: analysis.py
import pandas as pd
df = pd.read_csv("data.csv", parse_dates=["order_date"])
df["month"] = df["order_date"].dt.to_period("M").astype(str)
print(df.groupby(["month", "category"])["revenue"].sum())
'''

BASE = '''# filename: analysis.py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("data.csv", parse_dates=["order_date"])
df["revenue"] = df["units"] * df["unit_price"] * (1 - df["discount"])
df["month"] = df["order_date"].dt.to_period("M").astype(str)
m_prev, m_cur = sorted(df["month"].unique())[-2:]
cat = df.pivot_table(index="category", columns="month", values="revenue", aggfunc="sum")[[m_prev, m_cur]]
cat["change"] = cat[m_cur] - cat[m_prev]
worst = cat["change"].idxmin()
print("Months compared:", m_prev, "vs", m_cur)
print(cat.round(0).to_string())
print("Biggest drop:", worst, round(cat.loc[worst, "change"]))
sub = df[(df["category"] == worst) & df["month"].isin([m_prev, m_cur])]
reg = sub.pivot_table(index="region", columns="month", values="revenue", aggfunc="sum")
reg["change"] = reg[m_cur] - reg[m_prev]
print(reg.round(0).to_string())
prod = sub.pivot_table(index="product", columns="month", values="revenue", aggfunc="sum")
prod["change"] = prod[m_cur] - prod[m_prev]
print(prod["change"].sort_values().round(0).to_string())

fig, ax = plt.subplots(figsize=(7, 4))
cat[[m_prev, m_cur]].div(1e5).plot(kind="bar", ax=ax)
ax.set_title("Revenue by category: " + m_prev + " vs " + m_cur)
ax.set_xlabel("Category")
ax.set_ylabel("Revenue (Rs lakh)")
fig.tight_layout()
fig.savefig("category_trend.png")
plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 4))
reg["change"].div(1e5).plot(kind="bar", ax=ax, color="#0891b2")
@@LABELS@@
fig.tight_layout()
fig.savefig("region_breakdown.png")
plt.close(fig)
'''
UNLABELLED = 'ax.set_title("Region change")'
LABELLED = (
    'ax.set_title("Revenue change by region in " + worst + " (" + m_prev + " to " + m_cur + ")")\n'
    'ax.set_xlabel("Region")\n'
    'ax.set_ylabel("Revenue change (Rs lakh)")'
)


def _facts(csv_path) -> dict:
    df = pd.read_csv(csv_path, parse_dates=["order_date"])
    df["rev"] = df.units * df.unit_price * (1 - df.discount)
    df["m"] = df.order_date.dt.to_period("M").astype(str)
    prev, cur = sorted(df.m.unique())[-2:]
    cat = df[df.m.isin([prev, cur])].pivot_table(index="category", columns="m", values="rev", aggfunc="sum")
    ch = (cat[cur] - cat[prev]).sort_values()
    worst = ch.index[0]
    sub = df[(df.category == worst) & df.m.isin([prev, cur])]
    reg = sub.pivot_table(index="region", columns="m", values="rev", aggfunc="sum")
    rch = (reg[cur] - reg[prev]).sort_values()
    prod = sub.pivot_table(index="product", columns="m", values="rev", aggfunc="sum")
    pch = (prod[cur] - prod[prev]).sort_values()
    return dict(prev=prev, cur=cur, worst=worst, a=cat.loc[worst, prev], b=cat.loc[worst, cur], d=-ch.iloc[0],
                reg=rch.index[0], rd=-rch.iloc[0], p1=pch.index[0], p2=pch.index[1])


def build_mock_script(csv_path) -> dict:
    f = _facts(csv_path)

    def lakh(v):
        return f"Rs {v / 1e5:.1f} L"

    answer = (
        "ANSWER\n"
        f"{f['worst']} had the biggest drop: revenue fell from {lakh(f['a'])} in {f['prev']} to {lakh(f['b'])} "
        f"in {f['cur']} (down {f['d'] / f['a'] * 100:.1f}%).\n\n"
        "WHERE IT CAME FROM\n"
        f"{f['reg']} region caused {lakh(f['rd'])} of the {lakh(f['d'])} drop ({f['rd'] / f['d'] * 100:.0f}%). "
        f"Two products explain most of it: {f['p1']} and {f['p2']}.\n\n"
        "FILES\ncategory_trend.png | region_breakdown.png | analysis.py\n\n"
        "SUGGESTED NEXT QUESTION\n"
        f"Did discounts on {f['p1']} change between {f['prev']} and {f['cur']}?\n\n"
        "APPROVED"
    )

    def fence(code):
        return f"```python\n{code}```\nHere is the script."

    return {
        "Planner": ["1) revenue = units * unit_price * (1 - discount)\n2) Group by month + category\n"
                    "3) Find the biggest drop between the last two months\n4) Split that category by region and product"],
        "Coder": [fence(BUG), fence(BASE.replace("@@LABELS@@", UNLABELLED)), fence(BASE.replace("@@LABELS@@", LABELLED))],
        "Reviewer": ["Chart 2 (region_breakdown.png) has no axis labels. Add axis labels and Rs units.", answer],
    }

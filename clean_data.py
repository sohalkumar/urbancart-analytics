"""
Data cleaning pipeline: raw (messy) CSVs -> clean, analysis-ready tables.
Loads cleaned tables into a local SQLite database for SQL analysis, and
exports clean CSVs for Power BI import.
"""
import pandas as pd
import numpy as np
import sqlite3
import os

RAW = "data_raw"
CLEAN = "data_clean"
os.makedirs(CLEAN, exist_ok=True)

log = []

def note(msg):
    log.append(msg)
    print(msg)

# ---------- Customers ----------
customers = pd.read_csv(f"{RAW}/customers_raw.csv")
before = len(customers)

customers["city"] = customers["city"].str.strip().str.title()
customers = customers.drop_duplicates(subset="customer_id", keep="first")
note(f"Customers: removed {before - len(customers)} duplicate rows")

missing_city = customers["city"].isna().sum()
customers["city"] = customers["city"].fillna("Unknown")
customers["state"] = customers["state"].fillna("Unknown")
note(f"Customers: filled {missing_city} missing city values with 'Unknown'")

customers["signup_date"] = pd.to_datetime(customers["signup_date"])

# ---------- Products ----------
products = pd.read_csv(f"{RAW}/products_raw.csv")
products["unit_price"] = products["unit_price"].round(2)

missing_cost = products["cost_price"].isna().sum()
# Fill missing cost_price with the category-average cost ratio (cost/price)
products["cost_ratio"] = products["cost_price"] / products["unit_price"]
avg_ratio_by_cat = products.groupby("category")["cost_ratio"].transform("mean")
products["cost_price"] = products["cost_price"].fillna(products["unit_price"] * avg_ratio_by_cat)
products["cost_price"] = products["cost_price"].round(2)
products = products.drop(columns=["cost_ratio"])
note(f"Products: filled {missing_cost} missing cost_price values using category-average margin")

# ---------- Orders ----------
orders = pd.read_csv(f"{RAW}/orders_raw.csv")
before = len(orders)

def parse_date(d):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return pd.to_datetime(d, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT

orders["order_date"] = orders["order_date"].apply(parse_date)
bad_dates = orders["order_date"].isna().sum()
note(f"Orders: {bad_dates} unparseable dates found (dropped)" if bad_dates else "Orders: all dates parsed successfully")
orders = orders.dropna(subset=["order_date"])

missing_pay = orders["payment_method"].isna().sum()
orders["payment_method"] = orders["payment_method"].fillna("Unknown")
note(f"Orders: filled {missing_pay} missing payment_method values with 'Unknown'")

orders = orders.drop_duplicates(subset="order_id", keep="first")

# ---------- Order Items ----------
order_items = pd.read_csv(f"{RAW}/order_items_raw.csv")
before = len(order_items)
order_items = order_items.drop_duplicates(subset="order_item_id", keep="first")
note(f"Order items: removed {before - len(order_items)} duplicate line items")

order_items["line_total"] = (
    order_items["quantity"] * order_items["unit_price"] * (1 - order_items["discount_pct"] / 100)
).round(2)

# ---------- Marketing Spend ----------
marketing = pd.read_csv(f"{RAW}/marketing_spend_raw.csv")
before = len(marketing)

# Standardize channel-name casing
CANONICAL_CHANNELS = {c.lower(): c for c in ["Google Ads","Meta Ads","Influencer","Email/SMS","Affiliate"]}
marketing["channel"] = marketing["channel"].str.lower().map(CANONICAL_CHANNELS)

# Fill missing spend with that channel's average spend across all months
missing_spend = marketing["spend"].isna().sum()
marketing["spend"] = marketing["spend"].fillna(marketing.groupby("channel")["spend"].transform("mean"))
marketing["spend"] = marketing["spend"].round(2)
note(f"Marketing spend: standardized channel casing and filled {missing_spend} missing spend values with channel average")

# ---------- Referential integrity check ----------
valid_customers = set(customers["customer_id"])
valid_products = set(products["product_id"])
orphan_orders = (~orders["customer_id"].isin(valid_customers)).sum()
orphan_items = (~order_items["product_id"].isin(valid_products)).sum()
note(f"Referential check: {orphan_orders} orphan orders, {orphan_items} orphan order items")

# ---------- Save clean CSVs ----------
customers.to_csv(f"{CLEAN}/customers.csv", index=False)
products.to_csv(f"{CLEAN}/products.csv", index=False)
orders.to_csv(f"{CLEAN}/orders.csv", index=False)
order_items.to_csv(f"{CLEAN}/order_items.csv", index=False)
marketing.to_csv(f"{CLEAN}/marketing_spend.csv", index=False)

# ---------- Load into SQLite ----------
conn = sqlite3.connect(f"{CLEAN}/urbancart.db")
customers.to_sql("customers", conn, if_exists="replace", index=False)
products.to_sql("products", conn, if_exists="replace", index=False)
orders.to_sql("orders", conn, if_exists="replace", index=False)
order_items.to_sql("order_items", conn, if_exists="replace", index=False)
marketing.to_sql("marketing_spend", conn, if_exists="replace", index=False)
conn.close()

note(f"\nFinal row counts -> customers: {len(customers)}, products: {len(products)}, orders: {len(orders)}, order_items: {len(order_items)}")
note("Clean CSVs written to data_clean/, SQLite DB written to data_clean/urbancart.db")

with open(f"{CLEAN}/cleaning_log.txt", "w") as f:
    f.write("\n".join(log))

"""
Generates a synthetic, deliberately messy e-commerce dataset for "UrbanCart",
a fictional Indian D2C retail brand. Two years of order history (2024-2025)
with realistic seasonality (festive season spikes), regional distribution,
and intentional data quality issues to clean in the analysis phase.
"""
import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

# ---------- Reference data ----------
FIRST_NAMES = ["Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Reyansh","Ayaan","Krishna","Ishaan",
    "Ananya","Diya","Saanvi","Aadhya","Kiara","Myra","Anika","Navya","Riya","Ira",
    "Rohan","Karan","Neha","Priya","Pooja","Amit","Rahul","Sneha","Vikram","Divya",
    "Aman","Nikhil","Simran","Tanya","Rajesh","Suresh","Meera","Kavya","Yash","Om"]
LAST_NAMES = ["Sharma","Verma","Gupta","Patel","Reddy","Iyer","Nair","Singh","Rao","Mehta",
    "Kapoor","Joshi","Chauhan","Malhotra","Kulkarni","Desai","Pillai","Bose","Agarwal","Bansal"]

CITIES = [
    ("Mumbai","Maharashtra"), ("Delhi","Delhi"), ("Bengaluru","Karnataka"), ("Hyderabad","Telangana"),
    ("Chennai","Tamil Nadu"), ("Kolkata","West Bengal"), ("Pune","Maharashtra"), ("Ahmedabad","Gujarat"),
    ("Jaipur","Rajasthan"), ("Lucknow","Uttar Pradesh"), ("Surat","Gujarat"), ("Indore","Madhya Pradesh"),
    ("Chandigarh","Chandigarh"), ("Kochi","Kerala"), ("Nagpur","Maharashtra"), ("Bhopal","Madhya Pradesh"),
    ("Patna","Bihar"), ("Coimbatore","Tamil Nadu"), ("Guwahati","Assam"), ("Visakhapatnam","Andhra Pradesh"),
]

CATEGORIES = {
    "Electronics": ["Wireless Earbuds","Bluetooth Speaker","Power Bank 10000mAh","Smartwatch","USB-C Cable",
                    "Laptop Sleeve","Wireless Mouse","Phone Case","Screen Protector","Portable Charger"],
    "Home & Kitchen": ["Non-Stick Pan","Insulated Water Bottle","LED Desk Lamp","Cotton Bedsheet Set",
                       "Ceramic Mug Set","Storage Containers","Kitchen Scale","Wall Clock","Table Organizer","Diffuser Set"],
    "Fashion": ["Cotton T-Shirt","Denim Jacket","Running Shoes","Leather Wallet","Sunglasses",
                "Backpack","Formal Shirt","Sports Cap","Ankle Socks Pack","Canvas Sneakers"],
    "Beauty & Personal Care": ["Face Wash","Sunscreen SPF50","Hair Serum","Lip Balm Set","Body Lotion",
                                "Beard Trimmer","Perfume 100ml","Face Mask Pack","Shampoo 400ml","Nail Care Kit"],
    "Sports & Fitness": ["Yoga Mat","Resistance Bands Set","Dumbbell 5kg","Skipping Rope","Water Bottle Sipper",
                          "Gym Gloves","Foam Roller","Fitness Tracker Band","Badminton Racket","Football"],
}

PAYMENT_METHODS = ["UPI","Credit Card","Debit Card","Net Banking","Cash on Delivery","Wallet"]
CHANNELS = ["Mobile App","Website","Mobile Web"]
ORDER_STATUSES = ["Delivered","Delivered","Delivered","Delivered","Delivered","Cancelled","Returned","Delivered"]

N_CUSTOMERS = 600
N_PRODUCTS = sum(len(v) for v in CATEGORIES.values())
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 12, 31)

ACQUISITION_CHANNELS = ["Google Ads","Meta Ads","Organic Search","Referral","Email/SMS","Influencer"]
ACQ_WEIGHTS = [0.22, 0.20, 0.28, 0.12, 0.10, 0.08]

# ---------- Customers ----------
customers = []
for cid in range(1, N_CUSTOMERS + 1):
    fn = random.choice(FIRST_NAMES)
    ln = random.choice(LAST_NAMES)
    city, state = random.choice(CITIES)
    signup = START_DATE + timedelta(days=random.randint(0, 700))
    email = f"{fn.lower()}.{ln.lower()}{random.randint(1,999)}@{'gmail.com' if random.random()<0.6 else random.choice(['yahoo.com','outlook.com','rediffmail.com'])}"
    acq_channel = random.choices(ACQUISITION_CHANNELS, weights=ACQ_WEIGHTS)[0]
    customers.append({
        "customer_id": cid,
        "customer_name": f"{fn} {ln}",
        "email": email,
        "city": city,
        "state": state,
        "signup_date": signup.strftime("%Y-%m-%d"),
        "acquisition_channel": acq_channel,
    })

customers_df = pd.DataFrame(customers)

# Inject messiness: duplicate rows, null cities, inconsistent casing
dupe_rows = customers_df.sample(15, random_state=1).copy()
customers_df = pd.concat([customers_df, dupe_rows], ignore_index=True)
null_idx = customers_df.sample(25, random_state=2).index
customers_df.loc[null_idx, "city"] = None
case_idx = customers_df.sample(40, random_state=3).index
customers_df.loc[case_idx, "city"] = customers_df.loc[case_idx, "city"].str.upper()

# ---------- Products ----------
products = []
pid = 1
BASE_PRICES = {"Electronics": (399, 3499), "Home & Kitchen": (249, 1999), "Fashion": (299, 2499),
               "Beauty & Personal Care": (149, 1299), "Sports & Fitness": (199, 2999)}
for cat, items in CATEGORIES.items():
    lo, hi = BASE_PRICES[cat]
    for item in items:
        unit_price = round(random.uniform(lo, hi), -1) + 9
        margin_pct = random.uniform(0.30, 0.55)  # cost as % of price varies by product
        cost_price = round(unit_price * (1 - margin_pct), 2)
        products.append({
            "product_id": pid,
            "product_name": item,
            "category": cat,
            "unit_price": unit_price,
            "cost_price": cost_price,
        })
        pid += 1
products_df = pd.DataFrame(products)
missing_cost_idx = products_df.sample(4, random_state=6).index
products_df.loc[missing_cost_idx, "cost_price"] = None

# ---------- Orders & Order Items (with seasonality) ----------
def seasonal_weight(date):
    # Festive season boost: Oct-Nov (Diwali), and Jan sale, mild summer dip in May-Jun
    month = date.month
    if month in (10, 11):
        return 2.3
    if month == 1:
        return 1.5
    if month in (5, 6):
        return 0.7
    return 1.0

date_range = pd.date_range(START_DATE, END_DATE, freq="D")
daily_weights = np.array([seasonal_weight(d) for d in date_range])
daily_weights = daily_weights / daily_weights.sum()

TOTAL_ORDERS = 4200
order_dates = np.random.choice(date_range, size=TOTAL_ORDERS, p=daily_weights)

orders = []
order_items = []
oid_counter = 1
item_counter = 1

# customer purchase propensity (some are repeat buyers, most are one-and-done)
customer_weights = np.random.pareto(a=2.0, size=N_CUSTOMERS) + 0.1

for i in range(TOTAL_ORDERS):
    cust_id = np.random.choice(range(1, N_CUSTOMERS + 1), p=customer_weights / customer_weights.sum())
    odate = pd.Timestamp(order_dates[i])
    status = random.choice(ORDER_STATUSES)
    payment = random.choice(PAYMENT_METHODS)
    channel = random.choices(CHANNELS, weights=[0.55, 0.30, 0.15])[0]

    orders.append({
        "order_id": oid_counter,
        "customer_id": int(cust_id),
        "order_date": odate.strftime("%Y-%m-%d") if random.random() > 0.05 else odate.strftime("%d/%m/%Y"),  # inconsistent format
        "order_status": status,
        "payment_method": payment,
        "channel": channel,
    })

    n_items = np.random.choice([1, 2, 3, 4], p=[0.5, 0.3, 0.15, 0.05])
    chosen_products = random.sample(range(1, N_PRODUCTS + 1), n_items)
    for p in chosen_products:
        qty = np.random.choice([1, 1, 1, 2, 3], p=[0.55, 0.2, 0.15, 0.07, 0.03])
        unit_price = float(products_df.loc[products_df.product_id == p, "unit_price"].values[0])
        discount_pct = random.choices([0, 5, 10, 15, 20], weights=[0.45, 0.2, 0.2, 0.1, 0.05])[0]
        # Returns get negative-looking quantity flag in raw data (messiness to clean)
        raw_qty = qty if status != "Returned" else qty
        order_items.append({
            "order_item_id": item_counter,
            "order_id": oid_counter,
            "product_id": p,
            "quantity": raw_qty,
            "unit_price": unit_price,
            "discount_pct": discount_pct,
        })
        item_counter += 1
    oid_counter += 1

orders_df = pd.DataFrame(orders)
order_items_df = pd.DataFrame(order_items)

# Inject a few missing payment methods and a few duplicate order_item rows (messiness)
null_pay_idx = orders_df.sample(30, random_state=4).index
orders_df.loc[null_pay_idx, "payment_method"] = None
dupe_items = order_items_df.sample(20, random_state=5)
order_items_df = pd.concat([order_items_df, dupe_items], ignore_index=True)

# ---------- Save raw (messy) files ----------
customers_df.to_csv("data_raw/customers_raw.csv", index=False)
products_df.to_csv("data_raw/products_raw.csv", index=False)
orders_df.to_csv("data_raw/orders_raw.csv", index=False)
order_items_df.to_csv("data_raw/order_items_raw.csv", index=False)

# ---------- Marketing spend (monthly, per paid channel) ----------
PAID_CHANNELS = ["Google Ads", "Meta Ads", "Influencer", "Email/SMS", "Affiliate"]
BASE_MONTHLY_SPEND = {"Google Ads": 45000, "Meta Ads": 38000, "Influencer": 22000, "Email/SMS": 8000, "Affiliate": 15000}

months = pd.period_range(START_DATE, END_DATE, freq="M")
marketing_rows = []
for month in months:
    month_mid = datetime(month.year, month.month, 15)
    weight = seasonal_weight(month_mid)
    for ch in PAID_CHANNELS:
        base = BASE_MONTHLY_SPEND[ch]
        noise = np.random.uniform(0.85, 1.15)
        spend = round(base * weight * noise, 2)
        # inconsistent channel-name casing (messiness to clean)
        ch_name = ch if random.random() > 0.15 else ch.lower()
        marketing_rows.append({"month": month.strftime("%Y-%m"), "channel": ch_name, "spend": spend})

marketing_df = pd.DataFrame(marketing_rows)
# inject missing spend values for a few rows
null_spend_idx = marketing_df.sample(6, random_state=7).index
marketing_df.loc[null_spend_idx, "spend"] = None
marketing_df.to_csv("data_raw/marketing_spend_raw.csv", index=False)

print("Customers:", len(customers_df))
print("Products:", len(products_df))
print("Orders:", len(orders_df))
print("Order items:", len(order_items_df))
print("Marketing spend rows:", len(marketing_df))
print("Date range:", orders_df.order_date.min(), "to (approx)", END_DATE.date())

"""
Create a local theLook-shaped demo dataset in ecommerce/*.csv so the pipeline
can run without the full ~500MB public export.

Usage:  python generate_sample_data.py
"""
import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from config import DATA_DIR

RNG = np.random.default_rng(42)
N_USERS = 8000
N_PRODUCTS = 400
N_ORDERS = 12000
N_EVENTS = 25000
START = datetime(2019, 1, 6)
END = datetime(2024, 1, 17)

COUNTRIES = [
    ("United States", 0.42),
    ("China", 0.16),
    ("United Kingdom", 0.12),
    ("Germany", 0.08),
    ("Brazil", 0.07),
    ("Spain", 0.05),
    ("France", 0.04),
    ("Australia", 0.03),
    ("Japan", 0.02),
    ("Canada", 0.01),
]
US_STATES = [
    "California", "Texas", "New York", "Florida", "Illinois",
    "Pennsylvania", "Ohio", "Georgia", "North Carolina", "Michigan",
]
TRAFFIC = ["Search", "Email", "Organic", "Facebook", "Display"]
GENDERS = ["F", "M"]
STATUSES = ["Complete", "Shipped", "Processing", "Returned", "Cancelled"]
STATUS_P = [0.62, 0.12, 0.08, 0.08, 0.10]
CATEGORIES = [
    ("Women", "Sweaters"), ("Women", "Jeans"), ("Women", "Dresses"),
    ("Women", "Intimates"), ("Women", "Accessories"),
    ("Men", "Jeans"), ("Men", "Sweaters"), ("Men", "Outerwear & Coats"),
    ("Men", "Accessories"), ("Men", "Active"),
]


def _weighted_choice(pairs):
    labels, weights = zip(*pairs)
    return RNG.choice(labels, p=np.array(weights) / sum(weights))


def _rand_ts(start, end, n):
    span = int((end - start).total_seconds())
    offsets = RNG.integers(0, max(span, 1), size=n)
    return pd.to_datetime(start) + pd.to_timedelta(offsets, unit="s")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    country_names, country_w = zip(*COUNTRIES)
    country_w = np.array(country_w) / sum(country_w)
    countries = RNG.choice(country_names, size=N_USERS, p=country_w)
    states = [
        RNG.choice(US_STATES) if c == "United States" else ""
        for c in countries
    ]
    users = pd.DataFrame({
        "id": np.arange(1, N_USERS + 1),
        "first_name": [f"First{i}" for i in range(1, N_USERS + 1)],
        "last_name": [f"Last{i}" for i in range(1, N_USERS + 1)],
        "email": [f"user{i}@example.com" for i in range(1, N_USERS + 1)],
        "age": RNG.integers(18, 70, size=N_USERS),
        "gender": RNG.choice(GENDERS, size=N_USERS),
        "country": countries,
        "state": states,
        "traffic_source": RNG.choice(TRAFFIC, size=N_USERS),
        "created_at": _rand_ts(START, datetime(2023, 6, 1), N_USERS),
    })

    products = []
    for i in range(1, N_PRODUCTS + 1):
        dept, cat = CATEGORIES[i % len(CATEGORIES)]
        cost = float(RNG.uniform(5, 60))
        retail = round(cost * float(RNG.uniform(1.4, 2.8)), 2)
        products.append({
            "id": i,
            "department": dept,
            "category": cat,
            "retail_price": retail,
            "cost": round(cost, 2),
        })
    products = pd.DataFrame(products)

    dcs = pd.DataFrame({
        "id": np.arange(1, 11),
        "name": [f"DC {i}" for i in range(1, 11)],
        "latitude": RNG.uniform(25, 48, size=10),
        "longitude": RNG.uniform(-122, -70, size=10),
    })

    user_ids = users["id"].to_numpy()
    signup_map = dict(zip(users["id"], users["created_at"]))
    order_user_ids = RNG.choice(user_ids, size=N_ORDERS, replace=True)
    created = []
    for uid in order_user_ids:
        signup = signup_map[uid].to_pydatetime()
        lo = max(signup, START)
        created.append(_rand_ts(lo, END, 1)[0])
    orders = pd.DataFrame({
        "order_id": np.arange(1, N_ORDERS + 1),
        "user_id": order_user_ids,
        "status": RNG.choice(STATUSES, size=N_ORDERS, p=STATUS_P),
        "created_at": created,
    })

    item_rows = []
    inv_rows = []
    inv_id = 1
    for order in orders.itertuples(index=False):
        n_items = int(RNG.integers(1, 4))
        for _ in range(n_items):
            product = products.iloc[int(RNG.integers(0, len(products)))]
            sale = round(float(product.retail_price) * float(RNG.uniform(0.85, 1.0)), 2)
            item_status = "Returned" if order.status == "Returned" else (
                "Cancelled" if order.status == "Cancelled" else "Complete"
            )
            item_rows.append({
                "id": len(item_rows) + 1,
                "order_id": order.order_id,
                "user_id": order.user_id,
                "product_id": int(product.id),
                "inventory_item_id": inv_id,
                "status": item_status,
                "sale_price": sale,
                "created_at": order.created_at,
            })
            inv_rows.append({
                "id": inv_id,
                "product_id": int(product.id),
                "cost": float(product.cost),
                "created_at": order.created_at,
            })
            inv_id += 1
    order_items = pd.DataFrame(item_rows)
    inventory_items = pd.DataFrame(inv_rows)

    events = pd.DataFrame({
        "id": np.arange(1, N_EVENTS + 1),
        "user_id": RNG.choice(user_ids, size=N_EVENTS),
        "event_type": RNG.choice(["home", "product", "cart", "purchase"], size=N_EVENTS),
        "created_at": _rand_ts(START, END, N_EVENTS),
    })

    files = {
        "users.csv": users,
        "products.csv": products,
        "orders.csv": orders,
        "order_items.csv": order_items,
        "inventory_items.csv": inventory_items,
        "events.csv": events,
        "distribution_centers.csv": dcs,
    }
    for name, df in files.items():
        path = os.path.join(DATA_DIR, name)
        df.to_csv(path, index=False)
        print(f"  {name:<28} {len(df):>8,} rows")
    print(f"\nWrote demo CSVs to {DATA_DIR}")


if __name__ == "__main__":
    main()

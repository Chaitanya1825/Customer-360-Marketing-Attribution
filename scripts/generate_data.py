"""
generate_data.py
----------------
Generates realistic sample datasets for Customer 360 and Marketing Attribution:
1. customers.csv (500 customers)
2. orders.csv (~1000 orders)
3. ad_spend.csv (Daily advertising performance by channel)

Date Alignment: January 10 to January 31, 2021 (matching GA4 session data).
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

# 1. Set fixed random seed for reproducible results
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
fake = Faker()
Faker.seed(RANDOM_SEED)

# Output directory path
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 2. Date Range: January 10, 2021 to January 31, 2021 (22 days inclusive)
START_DATE = datetime(2021, 1, 10)
END_DATE = datetime(2021, 1, 31)
TOTAL_DAYS = (END_DATE - START_DATE).days  # 21 days between start and end (22 total dates)


# ======================================================================
# 1. Generate Customers (500 rows) - Signups: Jan 10 to Jan 31, 2021
# ======================================================================
print("1. Generating customers (Jan 10–31, 2021)...")

customers_list = []
customer_signup_dates = {}

for i in range(1, 501):
    cust_id = f"CUST{i:03d}"
    
    # Signup date distributed between January 10 and January 31, 2021
    signup_offset = random.randint(0, TOTAL_DAYS)
    signup_dt = START_DATE + timedelta(days=signup_offset)
    signup_date_str = signup_dt.strftime("%Y-%m-%d")
    
    customer_signup_dates[cust_id] = signup_dt
    
    customers_list.append({
        "customer_id": cust_id,
        "name": fake.name(),
        "email": fake.email(),
        "city": fake.city(),
        "signup_date": signup_date_str
    })

df_customers = pd.DataFrame(customers_list)
customers_csv_path = os.path.join(OUTPUT_DIR, "customers.csv")
df_customers.to_csv(customers_csv_path, index=False)
print(f"   -> Saved {len(df_customers)} customers to {customers_csv_path}")


# ======================================================================
# 2. Generate Orders (~1000 rows) - Orders: On/after signup within Jan 2021
# ======================================================================
print("2. Generating orders (Jan 10–31, 2021)...")

product_categories = [
    "Electronics",
    "Apparel",
    "Home & Kitchen",
    "Beauty & Personal Care",
    "Sports & Outdoors"
]

orders_list = []
all_customer_ids = list(customer_signup_dates.keys())
TOTAL_ORDERS = 1000

for i in range(1, TOTAL_ORDERS + 1):
    order_id = f"ORD{i:04d}"
    
    # Pick a random customer from customers.csv
    cust_id = random.choice(all_customer_ids)
    signup_dt = customer_signup_dates[cust_id]
    
    # Order date occurs between customer signup date and Jan 31, 2021
    max_days_after = (END_DATE - signup_dt).days
    days_after = random.randint(0, max_days_after)
    order_dt = signup_dt + timedelta(days=days_after)
    
    # Positive realistic order amount ($15.00 to $450.00)
    order_amount = round(random.uniform(15.0, 450.0), 2)
    category = random.choice(product_categories)
    
    orders_list.append({
        "order_id": order_id,
        "customer_id": cust_id,
        "order_date": order_dt.strftime("%Y-%m-%d"),
        "order_amount": order_amount,
        "product_category": category
    })

# Sort orders chronologically
df_orders = pd.DataFrame(orders_list).sort_values("order_date").reset_index(drop=True)
orders_csv_path = os.path.join(OUTPUT_DIR, "orders.csv")
df_orders.to_csv(orders_csv_path, index=False)
print(f"   -> Saved {len(df_orders)} orders to {orders_csv_path}")


# ======================================================================
# 3. Generate Ad Spend (Jan 10–31, 2021) across Google, Facebook, YouTube
# ======================================================================
print("3. Generating ad spend (Jan 10–31, 2021)...")

campaigns = [
    {"campaign_id": "CMP_GOOG_01", "campaign_name": "Google_Search_Brand", "channel": "Google"},
    {"campaign_id": "CMP_GOOG_02", "campaign_name": "Google_Search_Generic", "channel": "Google"},
    {"campaign_id": "CMP_FB_01",   "campaign_name": "Facebook_Retargeting", "channel": "Facebook"},
    {"campaign_id": "CMP_FB_02",   "campaign_name": "Facebook_Lookalike",   "channel": "Facebook"},
    {"campaign_id": "CMP_YT_01",   "campaign_name": "YouTube_Video_Action", "channel": "YouTube"},
    {"campaign_id": "CMP_YT_02",   "campaign_name": "YouTube_Awareness",    "channel": "YouTube"}
]

ad_spend_list = []

# Generate daily performance for each campaign from Jan 10 to Jan 31 (22 dates)
for day_idx in range(TOTAL_DAYS + 1):
    current_date = START_DATE + timedelta(days=day_idx)
    date_str = current_date.strftime("%Y-%m-%d")
    
    for camp in campaigns:
        if camp["channel"] == "Google":
            spend = round(random.uniform(80.0, 220.0), 2)
            impressions = int(spend * random.uniform(25, 45))
            clicks = int(impressions * random.uniform(0.025, 0.055))
        elif camp["channel"] == "Facebook":
            spend = round(random.uniform(60.0, 180.0), 2)
            impressions = int(spend * random.uniform(35, 60))
            clicks = int(impressions * random.uniform(0.015, 0.035))
        else:  # YouTube
            spend = round(random.uniform(50.0, 150.0), 2)
            impressions = int(spend * random.uniform(50, 90))
            clicks = int(impressions * random.uniform(0.008, 0.020))
            
        ad_spend_list.append({
            "campaign_id": camp["campaign_id"],
            "campaign_name": camp["campaign_name"],
            "channel": camp["channel"],
            "date": date_str,
            "spend": spend,
            "clicks": max(1, clicks),
            "impressions": max(clicks, impressions)
        })

df_ad_spend = pd.DataFrame(ad_spend_list)
ad_spend_csv_path = os.path.join(OUTPUT_DIR, "ad_spend.csv")
df_ad_spend.to_csv(ad_spend_csv_path, index=False)
print(f"   -> Saved {len(df_ad_spend)} ad spend records to {ad_spend_csv_path}")

print("\nData generation complete! All datasets synchronized to Jan 10–31, 2021.")

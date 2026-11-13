"""
create_identity_mapping.py
---------------------------
Simulates an Identity Resolution system for our Customer 360 platform.

Maps anonymous GA4 web visitors (user_pseudo_id) to authenticated
CRM customers (customer_id) using only valid IDs from our datasets.
"""

import os
import random
import pandas as pd

# 1. Set fixed random seed for reproducible results
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

CUSTOMERS_FILE = os.path.join(RAW_DIR, "customers.csv")
GA4_FILE = os.path.join(RAW_DIR, "ga4_sessions.csv")
OUTPUT_FILE = os.path.join(RAW_DIR, "identity_mapping.csv")

# 2. Read source datasets (read-only, no modifications)
print("1. Loading datasets...")
df_customers = pd.read_csv(CUSTOMERS_FILE)
df_ga4 = pd.read_csv(GA4_FILE)

# Extract unique, sorted IDs to ensure deterministic sampling
all_customer_ids = sorted(df_customers["customer_id"].unique())
all_ga4_user_ids = sorted(df_ga4["user_pseudo_id"].dropna().unique())

print(f"   Available CRM Customers: {len(all_customer_ids)}")
print(f"   Available GA4 Users: {len(all_ga4_user_ids):,}")

# 3. Map a realistic number of users (400 out of 500 customers = 80% match rate)
NUM_MAPPED = 400

sampled_customers = random.sample(all_customer_ids, NUM_MAPPED)
sampled_ga4_users = random.sample(all_ga4_user_ids, NUM_MAPPED)

# 4. Create the identity mapping DataFrame
df_identity_mapping = pd.DataFrame({
    "user_pseudo_id": sampled_ga4_users,
    "customer_id": sampled_customers,
    "mapping_type": "simulated"
})

# 5. Save to data/raw/identity_mapping.csv
df_identity_mapping.to_csv(OUTPUT_FILE, index=False)
print(f"\n2. Saved identity mapping to {OUTPUT_FILE}")

# 6. Verification
print("\n3. Verification:")
print(f"   Total mapped user pairs: {len(df_identity_mapping)}")

# Verify referential integrity
cust_set = set(all_customer_ids)
ga4_set = set(all_ga4_user_ids)

invalid_customers = [c for c in df_identity_mapping["customer_id"] if c not in cust_set]
invalid_ga4_users = [u for u in df_identity_mapping["user_pseudo_id"] if u not in ga4_set]

print(f"   Invalid Customer IDs: {len(invalid_customers)}")
print(f"   Invalid GA4 User IDs: {len(invalid_ga4_users)}")
print(f"   Unique CRM Customers mapped: {df_identity_mapping['customer_id'].nunique()}")
print(f"   Unique GA4 Users mapped: {df_identity_mapping['user_pseudo_id'].nunique()}")

print("\nSample mapping (first 5 rows):")
print(df_identity_mapping.head(5).to_string(index=False))


"""
upload_to_bigquery.py
---------------------
Uploads the five raw CSV datasets to Google BigQuery under the `raw_data` dataset.
Uses Application Default Credentials (ADC) and explicit BigQuery schemas.
"""

import os
import sys
import pandas as pd
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError

# Configuration
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "customer360-analytics-513415")
DATASET_ID = os.getenv("GCP_RAW_DATASET_ID", "raw_data")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

# Table Definitions & Schemas
TABLE_CONFIGS = {
    "customers": {
        "file": "customers.csv",
        "schema": [
            bigquery.SchemaField("customer_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("email", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("city", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("signup_date", "DATE", mode="NULLABLE"),
        ]
    },
    "orders": {
        "file": "orders.csv",
        "schema": [
            bigquery.SchemaField("order_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("customer_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("order_date", "DATE", mode="NULLABLE"),
            bigquery.SchemaField("order_amount", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("product_category", "STRING", mode="NULLABLE"),
        ]
    },
    "ad_spend": {
        "file": "ad_spend.csv",
        "schema": [
            bigquery.SchemaField("campaign_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("campaign_name", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("channel", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("date", "DATE", mode="NULLABLE"),
            bigquery.SchemaField("spend", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("clicks", "INT64", mode="NULLABLE"),
            bigquery.SchemaField("impressions", "INT64", mode="NULLABLE"),
        ]
    },
    "ga4_sessions": {
        "file": "ga4_sessions.csv",
        "schema": [
            bigquery.SchemaField("user_pseudo_id", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("ga_session_id", "INT64", mode="NULLABLE"),
            bigquery.SchemaField("session_start_time", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("event_count", "INT64", mode="NULLABLE"),
            bigquery.SchemaField("traffic_source", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("traffic_medium", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("campaign_name", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("purchase_revenue", "FLOAT64", mode="NULLABLE"),
        ]
    },
    "identity_mapping": {
        "file": "identity_mapping.csv",
        "schema": [
            bigquery.SchemaField("user_pseudo_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("customer_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("mapping_type", "STRING", mode="NULLABLE"),
        ]
    }
}


def main():
    print("=" * 60)
    print("Google BigQuery Ingestion: Customer 360 Raw Datasets")
    print(f"Target Project: {PROJECT_ID}")
    print(f"Target Dataset: {DATASET_ID}")
    print("=" * 60)

    # 1. Initialize BigQuery Client (Application Default Credentials)
    try:
        client = bigquery.Client(project=PROJECT_ID)
        print("\n[OK] Connected to Google BigQuery Client.")
    except Exception as e:
        print("\n[ERROR] Failed to authenticate with Google Cloud.")
        print(f"Reason: {e}")
        print("\nTip: Run 'gcloud auth application-default login' in your terminal.")
        sys.exit(1)

    # 2. Ensure Dataset Exists
    dataset_ref = bigquery.DatasetReference(PROJECT_ID, DATASET_ID)
    try:
        dataset = client.get_dataset(dataset_ref)
        print(f"[OK] Dataset '{DATASET_ID}' found in location: {dataset.location}")
    except Exception:
        print(f"[INFO] Dataset '{DATASET_ID}' does not exist. Creating...")
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        try:
            dataset = client.create_dataset(dataset, exists_ok=True)
            print(f"[OK] Dataset '{DATASET_ID}' created successfully.")
        except Exception as e:
            print(f"[ERROR] Could not create dataset '{DATASET_ID}': {e}")
            sys.exit(1)

    # 3. Upload each CSV table
    for table_name, config in TABLE_CONFIGS.items():
        file_path = os.path.join(DATA_DIR, config["file"])
        
        if not os.path.exists(file_path):
            print(f"[ERROR] Source file missing: {file_path}")
            continue

        # Count local rows for verification
        local_df = pd.read_csv(file_path)
        local_row_count = len(local_df)

        print(f"\nUploading '{table_name}' from {config['file']} ({local_row_count:,} rows)...")

        table_ref = dataset_ref.table(table_name)
        job_config = bigquery.LoadJobConfig(
            schema=config["schema"],
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE  # Overwrites/replaces table on rerun
        )

        try:
            with open(file_path, "rb") as source_file:
                load_job = client.load_table_from_file(source_file, table_ref, job_config=job_config)
            
            # Wait for the load job to complete
            load_job.result()
            print(f"  -> Load job finished.")

            # 4. Verify Row Count in BigQuery
            table = client.get_table(table_ref)
            bq_row_count = table.num_rows

            if bq_row_count == local_row_count:
                print(f"  [SUCCESS] {table_name}: {bq_row_count:,} rows uploaded (100% matched).")
            else:
                print(f"  [WARNING] Row count mismatch: Local={local_row_count:,}, BigQuery={bq_row_count:,}")

        except GoogleAPIError as e:
            print(f"  [ERROR] BigQuery API error uploading {table_name}: {e}")
        except Exception as e:
            print(f"  [ERROR] Unexpected error uploading {table_name}: {e}")

    print("\n" + "=" * 60)
    print("BigQuery upload process completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()


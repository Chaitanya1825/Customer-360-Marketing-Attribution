"""
export_tableau_data.py
----------------------
Exports modeled analytics tables from Google BigQuery (`analytics` dataset)
to CSV format in `exports/tableau/` for use in Tableau Public.

Tables exported:
1. customer_360 (~500 rows)
2. fct_order_attribution (~1,231 rows)
3. fct_campaign_performance (~16 rows)

Uses Application Default Credentials (ADC) without hardcoded secrets.
Validates file existence, row count, column structure, and data integrity.
"""

import os
import sys
import pandas as pd
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError

# Configuration
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "customer360-analytics-513415")
DATASET_ID = os.getenv("GCP_DATASET_ID", "analytics")

# Project root is one level up from scripts/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "exports", "tableau")

TABLES_TO_EXPORT = [
    {
        "table_name": "customer_360",
        "file_name": "customer_360.csv",
        "expected_rows": 500,
        "description": "Unified customer-level 360 profiles with RFM metrics and segmentation"
    },
    {
        "table_name": "fct_order_attribution",
        "file_name": "fct_order_attribution.csv",
        "expected_rows": 1231,
        "description": "Order-touchpoint attribution with First-Touch, Last-Touch, Linear, and Time-Decay credits"
    },
    {
        "table_name": "fct_campaign_performance",
        "file_name": "fct_campaign_performance.csv",
        "expected_rows": 16,
        "description": "Paid advertising channel economics and web attribution revenue breakdown"
    }
]


def get_bigquery_client(project_id: str) -> bigquery.Client:
    """Initializes BigQuery client using Google Cloud Application Default Credentials."""
    try:
        client = bigquery.Client(project=project_id)
        print(f"[OK] Authenticated with Google Cloud BigQuery (Project: {project_id})")
        return client
    except Exception as e:
        print(f"[ERROR] Failed to initialize BigQuery client: {e}", file=sys.stderr)
        print("Please ensure Application Default Credentials are configured via `gcloud auth application-default login`.", file=sys.stderr)
        sys.exit(1)


def export_and_validate_table(client: bigquery.Client, config: dict, output_dir: str) -> dict:
    """Queries BigQuery table, saves as CSV, and validates data integrity."""
    table_name = config["table_name"]
    file_name = config["file_name"]
    expected_rows = config["expected_rows"]
    description = config["description"]
    output_path = os.path.join(output_dir, file_name)

    print(f"\n------------------------------------------------------------")
    print(f"Exporting: {DATASET_ID}.{table_name} -> {file_name}")
    print(f"Description: {description}")
    print(f"------------------------------------------------------------")

    query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`"

    try:
        # Fetch data from BigQuery
        print(f"  [1/4] Executing BigQuery query: {query}")
        query_job = client.query(query)
        df_bq = query_job.to_dataframe()
        bq_rows, bq_cols = df_bq.shape
        print(f"  [2/4] Retrieved {bq_rows} rows and {bq_cols} columns from BigQuery.")

        # Save to CSV
        print(f"  [3/4] Writing to CSV: {output_path}")
        df_bq.to_csv(output_path, index=False, encoding="utf-8")

        # Validate exported file
        print(f"  [4/4] Validating exported CSV file...")
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Export file not found at: {output_path}")

        file_size_bytes = os.path.getsize(output_path)
        if file_size_bytes == 0:
            raise ValueError(f"Export file is empty (0 bytes): {output_path}")

        # Re-read CSV to confirm parser compatibility and integrity
        df_csv = pd.read_csv(output_path)
        csv_rows, csv_cols = df_csv.shape

        if csv_rows != bq_rows:
            raise ValueError(f"Row count mismatch! BigQuery: {bq_rows}, Exported CSV: {csv_rows}")

        if csv_cols != bq_cols:
            raise ValueError(f"Column count mismatch! BigQuery: {bq_cols}, Exported CSV: {csv_cols}")

        columns_list = list(df_csv.columns)
        print(f"  [PASS] File verified: {csv_rows} rows, {csv_cols} columns, {file_size_bytes / 1024:.1f} KB")

        return {
            "table_name": table_name,
            "file_name": file_name,
            "output_path": output_path,
            "rows": csv_rows,
            "cols": csv_cols,
            "columns": columns_list,
            "size_kb": file_size_bytes / 1024,
            "status": "SUCCESS"
        }

    except GoogleAPIError as ge:
        print(f"  [FAIL] BigQuery API Error: {ge}", file=sys.stderr)
        return {
            "table_name": table_name,
            "file_name": file_name,
            "status": "FAILED",
            "error": str(ge)
        }
    except Exception as e:
        print(f"  [FAIL] Export or validation error: {e}", file=sys.stderr)
        return {
            "table_name": table_name,
            "file_name": file_name,
            "status": "FAILED",
            "error": str(e)
        }


def main():
    print("============================================================")
    print("  Customer 360: BigQuery to Tableau Public Data Exporter   ")
    print("============================================================")
    print(f"Target Directory: {OUTPUT_DIR}")
    print(f"GCP Project ID:   {PROJECT_ID}")
    print(f"BigQuery Dataset: {DATASET_ID}")

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    client = get_bigquery_client(PROJECT_ID)
    results = []

    for config in TABLES_TO_EXPORT:
        res = export_and_validate_table(client, config, OUTPUT_DIR)
        results.append(res)

    print("\n============================================================")
    print("                     EXPORT SUMMARY REPORT                   ")
    print("============================================================")

    all_passed = True
    for r in results:
        status = r["status"]
        if status == "SUCCESS":
            print(f"[OK] {r['file_name']:<28} | Rows: {r['rows']:<5} | Cols: {r['cols']:<3} | Size: {r['size_kb']:>6.1f} KB | Status: PASS")
            print(f"     Columns: {', '.join(r['columns'][:6])}{'...' if len(r['columns']) > 6 else ''}")
        else:
            all_passed = False
            print(f"[ERROR] {r['file_name']:<28} | FAILED: {r.get('error', 'Unknown error')}")

    print("============================================================")
    if all_passed:
        print("[SUCCESS] All tables successfully exported and validated for Tableau Public!")
        print(f"Files are available in: {OUTPUT_DIR}")
    else:
        print("[FAILURE] Some tables failed to export. Please check errors above.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


import os
from tableauhyperapi import HyperProcess, Telemetry, Connection, CreateMode, TableName

BASE_DIR = r"C:\Users\HP\Desktop\Customer 360 and Marketing Attribution Platform"
TABLEAU_DIR = os.path.join(BASE_DIR, "exports", "tableau")

def build_hyper_extracts():
    with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        # 1. customer_360.hyper
        h1 = os.path.join(TABLEAU_DIR, "customer_360.hyper")
        csv1 = os.path.join(TABLEAU_DIR, "customer_360.csv").replace("\\", "/")
        with Connection(endpoint=hyper.endpoint, database=h1, create_mode=CreateMode.CREATE_AND_REPLACE) as conn:
            conn.catalog.create_schema('Extract')
            t = TableName('Extract', 'Extract')
            conn.execute_command(f"""
                CREATE TABLE {t} (
                    "customer_id" TEXT,
                    "name" TEXT,
                    "email" TEXT,
                    "city" TEXT,
                    "signup_date" DATE,
                    "total_orders" BIGINT,
                    "total_revenue" DOUBLE PRECISION,
                    "average_order_value" DOUBLE PRECISION,
                    "first_order_date" DATE,
                    "last_order_date" DATE,
                    "total_sessions" BIGINT,
                    "first_session_date" DATE,
                    "last_session_date" DATE,
                    "recency_days" BIGINT,
                    "frequency" BIGINT,
                    "monetary_value" DOUBLE PRECISION,
                    "customer_segment" TEXT
                )
            """)
            c1 = conn.execute_command(f"COPY {t} FROM '{csv1}' WITH (FORMAT CSV, HEADER TRUE, NULL '')")
            print(f"Built customer_360.hyper: {c1} rows")

        # 2. fct_order_attribution.hyper
        h2 = os.path.join(TABLEAU_DIR, "fct_order_attribution.hyper")
        csv2 = os.path.join(TABLEAU_DIR, "fct_order_attribution.csv").replace("\\", "/")
        with Connection(endpoint=hyper.endpoint, database=h2, create_mode=CreateMode.CREATE_AND_REPLACE) as conn:
            conn.catalog.create_schema('Extract')
            t = TableName('Extract', 'Extract')
            conn.execute_command(f"""
                CREATE TABLE {t} (
                    "order_id" TEXT,
                    "customer_id" TEXT,
                    "order_date" DATE,
                    "order_amount" DOUBLE PRECISION,
                    "traffic_source" TEXT,
                    "traffic_medium" TEXT,
                    "campaign_name" TEXT,
                    "touchpoint_rank" BIGINT,
                    "total_touchpoints" BIGINT,
                    "first_touch_credit" DOUBLE PRECISION,
                    "last_touch_credit" DOUBLE PRECISION,
                    "linear_credit" DOUBLE PRECISION,
                    "time_decay_credit" DOUBLE PRECISION
                )
            """)
            c2 = conn.execute_command(f"COPY {t} FROM '{csv2}' WITH (FORMAT CSV, HEADER TRUE, NULL '')")
            print(f"Built fct_order_attribution.hyper: {c2} rows")

        # 3. fct_campaign_performance.hyper
        h3 = os.path.join(TABLEAU_DIR, "fct_campaign_performance.hyper")
        csv3 = os.path.join(TABLEAU_DIR, "fct_campaign_performance.csv").replace("\\", "/")
        with Connection(endpoint=hyper.endpoint, database=h3, create_mode=CreateMode.CREATE_AND_REPLACE) as conn:
            conn.catalog.create_schema('Extract')
            t = TableName('Extract', 'Extract')
            conn.execute_command(f"""
                CREATE TABLE {t} (
                    "reporting_section" TEXT,
                    "campaign_id" TEXT,
                    "campaign_name" TEXT,
                    "marketing_channel" TEXT,
                    "traffic_source" TEXT,
                    "traffic_medium" TEXT,
                    "total_spend" DOUBLE PRECISION,
                    "total_clicks" BIGINT,
                    "total_impressions" BIGINT,
                    "cost_per_click" DOUBLE PRECISION,
                    "cost_per_1000_impressions" DOUBLE PRECISION,
                    "first_touch_revenue" DOUBLE PRECISION,
                    "last_touch_revenue" DOUBLE PRECISION,
                    "linear_attributed_revenue" DOUBLE PRECISION,
                    "time_decay_attributed_revenue" DOUBLE PRECISION,
                    "attributed_order_count" BIGINT
                )
            """)
            c3 = conn.execute_command(f"COPY {t} FROM '{csv3}' WITH (FORMAT CSV, HEADER TRUE, NULL '')")
            print(f"Built fct_campaign_performance.hyper: {c3} rows")

if __name__ == '__main__':
    build_hyper_extracts()
    print("All 3 Hyper extract files successfully created in exports/tableau/")


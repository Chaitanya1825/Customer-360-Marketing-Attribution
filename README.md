# Customer 360 & Marketing Attribution Platform

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![dbt Core 1.13](https://img.shields.io/badge/dbt-Core%201.13-orange?logo=dbt&logoColor=white)](https://www.getdbt.com/)
[![Google BigQuery](https://img.shields.io/badge/Google%20Cloud-BigQuery-4285F4?logo=google-cloud&logoColor=white)](https://cloud.google.com/bigquery)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Tableau Public](https://img.shields.io/badge/Tableau%20Public-2026.3-E97627?logo=tableau&logoColor=white)](https://public.tableau.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade **Customer 360 & Multi-Touch Marketing Attribution Platform** engineered with the modern data stack: **Google BigQuery**, **dbt Core**, **Python**, **Streamlit**, and **Tableau Public**.

The platform resolves anonymous digital web touchpoints to authenticated CRM customer profiles, models multi-touch marketing attribution across four distinct methodologies (including 7-day half-life Time-Decay), computes RFM customer segmentation, and serves insights via an interactive dark-themed SaaS web application and an executive Tableau dashboard suite.

---

## 📑 Table of Contents

- [Project Architecture](#-project-architecture)
- [Core Analytical Capabilities](#-core-analytical-capabilities)
  - [1. Customer 360 & RFM Segmentation](#1-customer-360--rfm-segmentation)
  - [2. Multi-Touch Attribution Engine](#2-multi-touch-attribution-engine)
  - [3. Data Governance & Attribution Safeguards](#3-data-governance--attribution-safeguards)
- [dbt Transformation Pipeline](#-dbt-transformation-pipeline)
  - [Pipeline Layers](#pipeline-layers)
  - [Data Quality & Automated Testing](#data-quality--automated-testing)
- [Dual Delivery Interfaces](#-dual-delivery-interfaces)
  - [Streamlit SaaS Analytics Application](#1-streamlit-saas-analytics-application)
  - [Tableau Public Executive Suite](#2-tableau-public-executive-suite)
- [Verified Baseline Metrics](#-verified-baseline-metrics)
- [Repository Structure](#-repository-structure)
- [Quickstart & Reproduction Guide](#-quickstart--reproduction-guide)
  - [Prerequisites](#prerequisites)
  - [Installation & Setup](#installation--setup)
  - [Data Ingestion & dbt Execution](#data-ingestion--dbt-execution)
  - [Launching Dashboards](#launching-dashboards)
- [License](#-license)

---

## 🏗️ Project Architecture

```
                                  [DATA SOURCES]
  ┌──────────────────┐   ┌──────────────────────┐   ┌────────────────────────┐
  │  Raw CRM Orders  │   │   GA4 Web Sessions   │   │ Paid Campaign Ad Spend │
  │ (500 Customers)  │   │  (1,231 Touchpoints) │   │   (Google, Meta, YT)   │
  └────────┬─────────┘   └──────────┬───────────┘   └───────────┬────────────┘
           │                        │                           │
           └────────────────────────┼───────────────────────────┘
                                    ▼ Python / Pandas Ingestion
                         ┌───────────────────────┐
                         │    Google BigQuery    │
                         │  Dataset: `raw_data`  │
                         └──────────┬────────────┘
                                    │
                                    ▼ dbt Core Transformations
  ┌──────────────────────────────────────────────────────────────────────────┐
  │ 1. Staging (`stg_*`): Column standardization, type casting & assertions  │
  │ 2. Intermediate (`int_customer_sessions`): Identity resolution & sequence│
  │ 3. Marts (`customer_360`, `fct_order_attribution`, `fct_campaign_perf`) │
  └─────────────────────────────────┬────────────────────────────────────────┘
                                    │
           ┌────────────────────────┴─────────────────────────┐
           ▼                                                  ▼
┌───────────────────────────────┐          ┌──────────────────────────────────┐
│  Streamlit SaaS Dashboard     │          │  Tableau Public Executive Suite  │
│  - Dark Theme (#0B1020)       │          │  - `Customer360_Analytics.twbx`  │
│  - Interactive RFM Explorer   │          │  - 3 Dashboards, 16 Worksheets   │
│  - Attribution Model Sandbox  │          │  - Embedded Hyper Extract Engine │
└───────────────────────────────┘          └──────────────────────────────────┘
```

---

## 🎯 Core Analytical Capabilities

### 1. Customer 360 & RFM Segmentation

Aggregates individual customer journeys into a single customer profile:
* **Customer Profile:** Customer ID, Full Name, Email, City, Signup Date.
* **Order Economics:** Lifetime Total Orders, Total Revenue, Average Order Value (AOV), First and Last Order Dates.
* **Engagement Activity:** Total GA4 Sessions, First/Last Session Timestamps.
* **RFM Scoring Framework:**
  * **Recency ($R$):** Days elapsed between the customer's last order and the maximum order date in the dataset.
  * **Frequency ($F$):** Total lifetime successful order count.
  * **Monetary Value ($M$):** Cumulative order spend.
* **Behavioral Segmentation Rules:**
  * **Champions:** High monetary value ($M \ge \$500$), frequent purchases ($F \ge 3$), recent activity ($R \le 10\text{ days}$).
  * **Loyal Customers:** Frequent buyers ($F \ge 3$) with consistent engagement.
  * **Potential Loyalists:** Medium frequency ($F \in [2, 3)$) with recent activity ($R \le 14\text{ days}$).
  * **New Customers:** Single-order customers ($F = 1$) who made a purchase within the last 7 days ($R \le 7\text{ days}$).
  * **At Risk:** High/medium previous spenders who have lapsed ($R > 14\text{ days}$).
  * **Others:** Low-frequency or zero-order accounts.

### 2. Multi-Touch Attribution Engine

Evaluates every order against all customer touchpoints occurring **on or before the transaction timestamp**:

$$\text{Order Amount} = \sum_{i=1}^{N} (\text{Credit}_i \times \text{Order Amount})$$

1. **First-Touch Attribution:**
   Assigns 100% of revenue credit to the chronological first interaction channel ($i = 1$). Identifies top-of-funnel customer acquisition drivers.
2. **Last-Touch Attribution:**
   Assigns 100% of revenue credit to the final touchpoint prior to checkout ($i = N$). Identifies bottom-of-funnel conversion closers.
3. **Linear Attribution:**
   Distributes credit equally across all touchpoints:
   $$\text{Credit}_i = \frac{1}{N}$$
4. **Time-Decay Attribution (7-Day Half-Life):**
   Applies exponential decay weighting based on the time delta ($\Delta t_i$ in days) between the touchpoint timestamp and the order date:
   $$W_i = 2^{-\frac{\Delta t_i}{7}}, \quad \text{Credit}_i = \frac{W_i}{\sum_{j=1}^{N} W_j}$$
   Touchpoints closer to the moment of conversion receive proportionally higher credit, while still acknowledging earlier awareness touchpoints.

### 3. Data Governance & Attribution Safeguards

* **No Fictitious ROAS / CPA Mapping:** Paid advertising ad spend (Google Ads, Meta Ads, YouTube Campaigns) and GA4 session acquisition channels maintain distinct hierarchies. The platform does not invent artificial joins between unrelated campaign hierarchies, preventing misleading blended ROAS figures.
* **Explicit Unmatched Order Handling:** Orders with no matching GA4 pre-purchase sessions (381 orders totaling \$91,956.77) are categorized explicitly as **`Direct / (none)` (Unattributed)** rather than falsely conflated with organic direct visits.
* **Join Fan-Out Protection:** Orders and sessions are joined using identity mapping keys with windowed aggregation, preventing revenue double-counting.

---

## ⚡ dbt Transformation Pipeline

The data transformation layer is built using **dbt Core** targeting **Google BigQuery**:

```
dbt_project/
├── dbt_project.yml          # Project configuration & model paths
├── profiles.yml             # BigQuery OAuth connection with env_var support
├── macros/
│   └── unique_combination_of_columns.sql   # Composite key uniqueness test
├── models/
│   ├── staging/             # Clean, type-cast, and standardized source tables
│   │   ├── stg_customers.sql
│   │   ├── stg_orders.sql
│   │   ├── stg_ga4_sessions.sql
│   │   ├── stg_identity_mapping.sql
│   │   └── stg_ad_spend.sql
│   ├── intermediate/        # Business logic & identity resolution
│   │   └── int_customer_sessions.sql
│   └── marts/               # Analytical dimension & fact models
│       ├── customer_360.sql
│       ├── fct_order_attribution.sql
│       └── fct_campaign_performance.sql
└── tests/                   # Singular custom assertions
    ├── assert_campaign_performance_totals.sql
    └── assert_order_attribution_credits_sum_to_one.sql
```

### Pipeline Layers

1. **Staging Layer (`staging`):** Standardizes field names, casts timestamps and numeric values, and ensures primary key integrity across raw sources.
2. **Intermediate Layer (`intermediate`):** Executes deterministic identity resolution between anonymous web users (`user_pseudo_id`) and authenticated CRM records (`customer_id`), and generates chronological session sequence ranks via `ROW_NUMBER() OVER (...)`.
3. **Marts Layer (`marts`):**
   * **`customer_360`**: Unified profile table with RFM scores and customer segment labels.
   * **`fct_order_attribution`**: Order-touchpoint grain fact table calculating all four attribution credits per touchpoint.
   * **`fct_campaign_performance`**: Partitioned reporting mart separating paid advertising spend economics from web acquisition channel revenue.

### Data Quality & Automated Testing

The project includes **40 automated dbt tests**:
* **38 Schema Tests:** Enforces `not_null`, `unique`, `relationships` (referential integrity), `accepted_values` (segment and section checks), and `unique_combination_of_columns` (composite key uniqueness on `[order_id, touchpoint_rank]` and `[customer_id, ga_session_id]`).
* **2 Singular Custom Assertions:**
  * `assert_order_attribution_credits_sum_to_one.sql`: Validates that attribution credits for every order strictly sum to $1.0 \pm 0.001$.
  * `assert_campaign_performance_totals.sql`: Confirms total spend matches the raw advertising ledger.

---

## 🖥️ Dual Delivery Interfaces

### 1. Streamlit SaaS Analytics Application

A custom enterprise SaaS dark-themed analytics web application (`app/app.py`):
* **Visual Styling:** Deep Navy (`#0B1020`) and Card Slate (`#151D30`), with electric blue (`#38BDF8`), violet, and emerald accents.
* **Executive Overview:** Real-time KPI scorecards with trend indicators, cumulative revenue metrics, and channel breakdowns.
* **Customer 360 Explorer:** Interactive RFM scatter plots, segment distribution bar charts, and a searchable customer lookup with drill-down purchase history.
* **Marketing Attribution Sandbox:** Direct visual comparison across First-Touch, Last-Touch, Linear, and Time-Decay attribution models.
* **Paid Campaign Economics:** Channel-by-channel unit economics (CPC, CPM, spend, clicks, impressions).

```bash
streamlit run app/app.py
```

### 2. Tableau Public Executive Suite

A native Tableau Public workbook suite available in both packaged (`.twbx`) and extract-connected (`.twb`) formats:
* **File:** [`exports/tableau/Customer360_Analytics.twbx`](file:///C:/Users/HP/Desktop/Customer%20360%20and%20Marketing%20Attribution%20Platform/exports/tableau/Customer360_Analytics.twbx)
* **Dashboards:**
  1. **Executive Overview:** High-level executive KPI metrics, segment composition, and revenue contribution.
  2. **Customer Intelligence:** RFM scatter matrix, order frequency distribution, and customer value tiers.
  3. **Marketing Attribution:** Multi-model revenue comparison, touchpoint depth distribution, paid campaign spend, and CPC vs. CPM channel efficiency.
* **Embedded Hyper Engine:** Pre-compiled `.hyper` extract databases (`customer_360.hyper`, `fct_order_attribution.hyper`, `fct_campaign_performance.hyper`) embedded directly inside the workbook for instant offline loading and zero cloud publishing warnings.

---

## 📊 Verified Baseline Metrics

Every analytical metric in the platform is verified against the underlying BigQuery ground truth:

| Analytical Metric | Ground Truth Value | Validation Notes |
| :--- | :--- | :--- |
| **Total Order Revenue** | **\$240,669.11** | Zero revenue duplication across multi-touch joins |
| **Total Paid Ad Spend** | **\$16,718.24** | 6 campaigns across Google, Meta, and YouTube |
| **Total Customers** | **500** | Includes active buyers and zero-order signups |
| **Total Orders** | **1,000** | Across 22-day simulation timeframe |
| **Average Order Value (AOV)** | **\$240.67** | Verified across CRM and mart layers |
| **Unattributed Orders** | **381 Orders (\$91,956.77)** | Safely categorized as Direct / (none) |
| **Ad Clicks / Impressions** | **20,565 / 798,417** | Average CPC: \$0.81 \| Average CPM: \$20.94 |

---

## 📂 Repository Structure

```text
Customer 360 and Marketing Attribution Platform/
├── .gitignore                         # Comprehensive Git ignore rules
├── requirements.txt                   # Verified Python dependencies
├── README.md                          # Production platform documentation
│
├── app/
│   └── app.py                         # Interactive Streamlit SaaS dashboard
├── .streamlit/
│   └── config.toml                    # Streamlit custom dark theme configuration
│
├── data/
│   └── raw/                           # Raw source CSV datasets
│       ├── customers.csv              # CRM customer demographic records (500 rows)
│       ├── orders.csv                 # Purchase transactions (1,000 rows)
│       ├── ga4_sessions.csv           # Google Analytics 4 session logs (7.8 MB)
│       ├── identity_mapping.csv       # Deterministic identity resolution bridge
│       └── ad_spend.csv               # Daily campaign advertising expenditure
│
├── dbt_project/                       # dbt Core transformation project
│   ├── dbt_project.yml                # Project manifest & configuration
│   ├── profiles.yml                   # BigQuery connection (portable via env_vars)
│   ├── profiles.yml.example           # Example configuration template for clones
│   ├── macros/
│   │   └── unique_combination_of_columns.sql
│   ├── models/
│   │   ├── staging/                   # 5 staging models + YAML tests
│   │   ├── intermediate/              # Identity resolution & session sequencing
│   │   └── marts/                     # 3 dimensional & fact marts + YAML tests
│   └── tests/                         # 2 custom data assertion tests
│
├── exports/
│   └── tableau/                       # Tableau Public visualization suite
│       ├── Customer360_Analytics.twbx # Packaged workbook with embedded extracts
│       ├── Customer360_Analytics.twb  # Extract-connected workbook XML
│       ├── customer_360.hyper         # Compiled Hyper extract database
│       ├── fct_order_attribution.hyper
│       ├── fct_campaign_performance.hyper
│       ├── customer_360.csv           # Exported mart data files
│       ├── fct_order_attribution.csv
│       └── fct_campaign_performance.csv
│
├── scripts/                           # Pipeline orchestration & utilities
│   ├── generate_data.py               # Seed data generator (Faker / Pandas)
│   ├── create_identity_mapping.py     # Deterministic identity resolution generator
│   ├── upload_to_bigquery.py          # BigQuery raw table ingester
│   ├── export_tableau_data.py         # Mart exporter to CSV
│   ├── build_verified_twb.py          # Tableau XML compiler
│   ├── build_hyper_extracts.py        # Native Hyper database compiler
│   ├── package_tableau_workbook.py    # .twbx packager
│   └── verify_final_twb.py            # Automated Tableau test harness
│
└── sql/                               # Standalone reference SQL queries
    ├── customer_360.sql
    ├── attribution_models.sql
    ├── marketing_performance.sql
    └── ga4_sessions.sql
```

---

## 🚀 Quickstart & Reproduction Guide

### Prerequisites

* **Python 3.11+** installed.
* **Google Cloud SDK (`gcloud`)** installed and configured.
* **Tableau Public** (2024.1+ or 2026.3) installed (optional, for viewing Tableau dashboards locally).

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/customer-360-marketing-attribution.git
   cd customer-360-marketing-attribution
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Authenticate with Google Cloud:**
   ```bash
   gcloud auth application-default login
   ```

5. **(Optional) Configure environment variables:**
   If using a custom Google Cloud Project:
   ```bash
   # Windows (PowerShell)
   $env:GCP_PROJECT_ID = "your-gcp-project-id"

   # macOS / Linux
   export GCP_PROJECT_ID="your-gcp-project-id"
   ```

### Data Ingestion & dbt Execution

1. **Upload raw datasets to BigQuery:**
   ```bash
   python scripts/upload_to_bigquery.py
   ```

2. **Run dbt transformations and data quality tests:**
   ```bash
   dbt build --project-dir dbt_project --profiles-dir dbt_project
   ```

3. **Export BigQuery marts for Tableau:**
   ```bash
   python scripts/export_tableau_data.py
   python scripts/build_hyper_extracts.py
   python scripts/package_tableau_workbook.py
   ```

### Launching Dashboards

* **Launch the Streamlit SaaS Dashboard:**
  ```bash
  streamlit run app/app.py
  ```
  Open your browser at `http://localhost:8501`.

* **Open the Tableau Executive Suite:**
  Double-click `exports/tableau/Customer360_Analytics.twbx` or open directly via Tableau Public.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

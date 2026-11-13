"""
app.py
------
Customer 360 & Marketing Attribution Platform
Commercial-Grade Enterprise SaaS Analytics Experience
Powered by Google BigQuery, dbt Core, Streamlit & Plotly
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError

# ----------------------------------------------------------------------
# 1. Page Configuration
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Customer 360 | Marketing Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------------------------
# 2. Premium SaaS Custom CSS Theme (Dark Navy / Charcoal / Electric Blue)
# ----------------------------------------------------------------------
st.markdown("""
<style>
    /* Google Font Import */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Typography & Background Reset */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #F8FAFC;
    }

    .stApp {
        background-color: #0B1020;
        background-image: 
            radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.04) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(99, 102, 241, 0.04) 0px, transparent 50%);
    }

    /* Hide default header decor */
    header[data-testid="stHeader"] {
        background: rgba(11, 16, 32, 0.85);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #080D1A;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
        padding-top: 1rem;
    }

    /* Sidebar Brand Box */
    .brand-container {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 12px 18px 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        margin-bottom: 20px;
    }
    .brand-icon {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        background: linear-gradient(135deg, #0EA5E9 0%, #6366F1 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-size: 1.25rem;
        box-shadow: 0 4px 14px rgba(14, 165, 233, 0.35);
    }
    .brand-title {
        font-size: 1.15rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #FFFFFF;
        line-height: 1.1;
    }
    .brand-subtitle {
        font-size: 0.72rem;
        font-weight: 500;
        color: #94A3B8;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    /* Sidebar Section Labels */
    .sidebar-section-label {
        font-size: 0.68rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 20px;
        margin-bottom: 8px;
        padding-left: 4px;
    }

    /* Live Status Pill */
    .status-pill-live {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.25);
        color: #34D399;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 3px 9px;
        border-radius: 9999px;
    }
    .status-dot-pulse {
        width: 6px;
        height: 6px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10B981;
    }

    /* Main Dashboard Header */
    .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        padding-bottom: 1.25rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        margin-bottom: 1.75rem;
    }
    .dashboard-headline {
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #FFFFFF;
        margin: 0;
        line-height: 1.15;
    }
    .dashboard-subhead {
        font-size: 0.9rem;
        color: #94A3B8;
        margin-top: 4px;
        margin-bottom: 0;
    }

    /* Header Badges Row */
    .header-badges {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
    }
    .badge-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #151D30;
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #CBD5E1;
        font-size: 0.75rem;
        font-weight: 500;
        padding: 5px 12px;
        border-radius: 8px;
    }

    /* Premium SaaS Metric Cards */
    .saas-card {
        background: #151D30;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 18px 20px;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 14px;
    }
    .saas-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.35);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    }
    .saas-card-accent-cyan { border-top: 2.5px solid #38BDF8; }
    .saas-card-accent-emerald { border-top: 2.5px solid #10B981; }
    .saas-card-accent-violet { border-top: 2.5px solid #8B5CF6; }
    .saas-card-accent-amber { border-top: 2.5px solid #F59E0B; }
    .saas-card-accent-rose { border-top: 2.5px solid #F43F5E; }
    .saas-card-accent-blue { border-top: 2.5px solid #3B82F6; }

    .card-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
    }
    .card-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .card-icon {
        font-size: 1rem;
        opacity: 0.85;
    }
    .card-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.02em;
        line-height: 1.15;
    }
    .card-footer-sub {
        font-size: 0.74rem;
        color: #64748B;
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .card-pill-tag {
        font-size: 0.68rem;
        font-weight: 600;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .tag-green { background: rgba(16, 185, 129, 0.15); color: #34D399; }
    .tag-blue { background: rgba(56, 189, 248, 0.15); color: #38BDF8; }
    .tag-violet { background: rgba(139, 92, 246, 0.15); color: #A78BFA; }

    /* Insight Banner Container */
    .insight-card {
        background: linear-gradient(135deg, rgba(21, 29, 48, 0.9) 0%, rgba(17, 24, 39, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 3px solid #38BDF8;
        border-radius: 10px;
        padding: 16px 20px;
        margin: 12px 0 20px 0;
    }
    .insight-title {
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #38BDF8;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .insight-body {
        font-size: 0.86rem;
        color: #CBD5E1;
        line-height: 1.5;
    }

    /* Customer Profile Card in Customer 360 */
    .customer-profile-card {
        background: #151D30;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .profile-avatar {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: linear-gradient(135deg, #6366F1 0%, #38BDF8 100%);
        color: white;
        font-weight: 700;
        font-size: 1.2rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Model Pill Cards in Attribution */
    .model-info-box {
        background: #151D30;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 14px 16px;
        height: 100%;
    }
    .model-info-title {
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .model-info-desc {
        font-size: 0.78rem;
        color: #94A3B8;
        line-height: 1.4;
    }

    /* Streamlit Widget Overrides */
    div[data-baseweb="select"] > div {
        background-color: #151D30 !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: #F8FAFC !important;
    }
    div[data-baseweb="input"] > div {
        background-color: #151D30 !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: #F8FAFC !important;
    }
    .stTextInput input {
        color: #F8FAFC !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# 3. BigQuery Data Layer (Preserved Queries & Vectorized Casts)
# ----------------------------------------------------------------------
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "customer360-analytics-513415")
DATASET_ID = os.getenv("GCP_DATASET_ID", "analytics")

@st.cache_resource
def get_bigquery_client():
    """Initializes BigQuery client using Google Cloud ADC, st.secrets, or environment variables."""
    try:
        if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
            from google.oauth2 import service_account
            credentials = service_account.Credentials.from_service_account_info(
                dict(st.secrets["gcp_service_account"])
            )
            return bigquery.Client(credentials=credentials, project=credentials.project_id)
        return bigquery.Client(project=PROJECT_ID)
    except Exception:
        return None

@st.cache_data(ttl=600, show_spinner=False)
def load_dbt_marts():
    """Fetches dbt mart tables from BigQuery analytics dataset with fallback to pre-computed verified marts."""
    client = get_bigquery_client()
    df_c360 = None
    df_attr = None
    df_perf = None
    df_orders = None

    if client is not None:
        try:
            # 1. Customer 360 Mart
            c360_query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.customer_360`"
            df_c360 = client.query(c360_query).to_dataframe()

            # 2. Order Attribution Mart
            attr_query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.fct_order_attribution`"
            df_attr = client.query(attr_query).to_dataframe()

            # 3. Campaign & Attribution Performance Mart
            perf_query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.fct_campaign_performance`"
            df_perf = client.query(perf_query).to_dataframe()

            # 4. Detailed Orders (for category drilldowns)
            orders_query = f"SELECT order_id, customer_id, order_date, order_amount, product_category FROM `{PROJECT_ID}.{DATASET_ID}.stg_orders`"
            df_orders = client.query(orders_query).to_dataframe()
        except Exception:
            client = None
            df_c360 = None

    # Fallback to local verified exports (e.g. for Streamlit Community Cloud deployment without GCP credentials)
    if client is None or df_c360 is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        c360_path = os.path.join(base_dir, "exports", "tableau", "customer_360.csv")
        attr_path = os.path.join(base_dir, "exports", "tableau", "fct_order_attribution.csv")
        perf_path = os.path.join(base_dir, "exports", "tableau", "fct_campaign_performance.csv")
        orders_path = os.path.join(base_dir, "data", "raw", "orders.csv")

        if os.path.exists(c360_path) and os.path.exists(attr_path) and os.path.exists(perf_path):
            df_c360 = pd.read_csv(c360_path)
            df_attr = pd.read_csv(attr_path)
            df_perf = pd.read_csv(perf_path)
            df_orders = pd.read_csv(orders_path)
        else:
            return None, None, None, None

    try:
        # Datatype conversions for Customer 360
        df_c360["total_orders"] = df_c360["total_orders"].astype(int)
        df_c360["total_sessions"] = df_c360["total_sessions"].astype(int)
        df_c360["total_revenue"] = df_c360["total_revenue"].astype(float)
        df_c360["average_order_value"] = df_c360["average_order_value"].astype(float)
        df_c360["recency_days"] = pd.to_numeric(df_c360["recency_days"], errors="coerce")

        # Datatype conversions for Order Attribution
        df_attr["order_date"] = pd.to_datetime(df_attr["order_date"]).dt.date
        df_attr["order_amount"] = df_attr["order_amount"].astype(float)
        for col in ["first_touch_credit", "last_touch_credit", "linear_credit", "time_decay_credit"]:
            df_attr[col] = df_attr[col].astype(float)

        # Pre-calculate row-level attribution revenue dynamically
        df_attr["first_touch_rev"] = (df_attr["order_amount"] * df_attr["first_touch_credit"]).round(2)
        df_attr["last_touch_rev"] = (df_attr["order_amount"] * df_attr["last_touch_credit"]).round(2)
        df_attr["linear_rev"] = (df_attr["order_amount"] * df_attr["linear_credit"]).round(6)
        df_attr["time_decay_rev"] = (df_attr["order_amount"] * df_attr["time_decay_credit"]).round(6)

        # Requirement: Label unmatched orders as 'Unattributed' rather than assuming direct visits
        unmatched_mask = (df_attr["campaign_name"] == "Unattributed") | (df_attr["traffic_source"] == "Direct")
        df_attr.loc[unmatched_mask, "traffic_source"] = "Unattributed"
        df_attr.loc[unmatched_mask, "traffic_medium"] = "Unattributed"
        df_attr.loc[unmatched_mask, "campaign_name"] = "Unattributed"

        # Explicit numeric type conversions for Campaign Performance
        df_perf["total_spend"] = pd.to_numeric(df_perf["total_spend"], errors="coerce").fillna(0.0).astype(float)
        df_perf["total_clicks"] = pd.to_numeric(df_perf["total_clicks"], errors="coerce").fillna(0).astype(int)
        df_perf["total_impressions"] = pd.to_numeric(df_perf["total_impressions"], errors="coerce").fillna(0).astype(int)
        df_perf["cost_per_click"] = pd.to_numeric(df_perf["cost_per_click"], errors="coerce").astype(float)
        df_perf["cost_per_1000_impressions"] = pd.to_numeric(df_perf["cost_per_1000_impressions"], errors="coerce").astype(float)
        for col in ["first_touch_revenue", "last_touch_revenue", "linear_attributed_revenue", "time_decay_attributed_revenue"]:
            df_perf[col] = pd.to_numeric(df_perf[col], errors="coerce").fillna(0.0).astype(float)
        df_perf["attributed_order_count"] = pd.to_numeric(df_perf["attributed_order_count"], errors="coerce").fillna(0).astype(int)

        perf_unmatched_mask = (df_perf["reporting_section"] == "attributed_traffic_source") & (df_perf["traffic_source"] == "Direct")
        df_perf.loc[perf_unmatched_mask, "traffic_source"] = "Unattributed"
        df_perf.loc[perf_unmatched_mask, "traffic_medium"] = "Unattributed"

        return df_c360, df_attr, df_perf, df_orders

    except Exception as e:
        st.error(f"Error processing marts data: {e}")
        return None, None, None, None


with st.spinner("Authenticating with BigQuery & loading analytics marts..."):
    df_c360, df_attr, df_perf, df_orders = load_dbt_marts()

if df_c360 is None or df_attr is None or df_perf is None:
    st.error("Dashboard could not connect to Google BigQuery. Please verify credentials and project dataset.")
    st.stop()


# ----------------------------------------------------------------------
# 4. Universal Plotly Dark SaaS Theme Helper
# ----------------------------------------------------------------------
def apply_saas_plotly_theme(fig, height=360, show_legend=True):
    """Applies a bespoke dark SaaS theme across all Plotly visual components."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        font=dict(
            family="'Plus Jakarta Sans', -apple-system, sans-serif",
            color="#94A3B8",
            size=11
        ),
        margin=dict(l=16, r=16, t=36, b=16),
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color="#CBD5E1"),
            bgcolor="rgba(0,0,0,0)"
        )
    )
    fig.update_xaxes(
        gridcolor="rgba(255, 255, 255, 0.05)",
        zerolinecolor="rgba(255, 255, 255, 0.08)",
        tickfont=dict(size=10, color="#94A3B8"),
        title_font=dict(size=11, color="#CBD5E1")
    )
    fig.update_yaxes(
        gridcolor="rgba(255, 255, 255, 0.05)",
        zerolinecolor="rgba(255, 255, 255, 0.08)",
        tickfont=dict(size=10, color="#94A3B8"),
        title_font=dict(size=11, color="#CBD5E1")
    )
    return fig


# ----------------------------------------------------------------------
# 5. Sidebar Redesign (Sleek Commercial Navigation & Filters)
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="brand-container">
        <div class="brand-icon">⚡</div>
        <div>
            <div class="brand-title">Customer 360</div>
            <div class="brand-subtitle">Marketing Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-label">Main Navigation</div>', unsafe_allow_html=True)
    nav_selection = st.radio(
        "Navigation",
        [
            "📊 Executive Overview",
            "👤 Customer 360",
            "📢 Marketing Attribution",
            "🎯 Paid Campaign Performance"
        ],
        label_visibility="collapsed"
    )

    st.markdown('<div class="sidebar-section-label">Drilldown Filters</div>', unsafe_allow_html=True)

    # Customer Segment Filter
    all_segments = ["All Segments"] + sorted(list(df_c360["customer_segment"].dropna().unique()))
    selected_segment = st.selectbox("Customer Lifecycle Segment", all_segments)

    # Traffic Source Filter
    all_sources = ["All Sources"] + sorted(list(df_attr["traffic_source"].dropna().unique()))
    selected_source = st.selectbox("Web Traffic Source", all_sources)

    # Paid Channel Filter
    paid_perf = df_perf[df_perf["reporting_section"] == "paid_campaign"].copy()
    all_channels = ["All Channels"] + sorted(list(paid_perf["marketing_channel"].dropna().unique()))
    selected_channel = st.selectbox("Paid Advertising Channel", all_channels)

    st.markdown("---")
    st.markdown("""
    <div style="padding: 4px 6px;">
        <div class="status-pill-live">
            <div class="status-dot-pulse"></div>
            BigQuery Connected (US)
        </div>
        <div style="font-size: 0.72rem; color: #64748B; margin-top: 8px;">
            Window: <span style="color: #94A3B8; font-weight: 600;">Jan 10–31, 2021</span><br>
            Engine: <span style="color: #94A3B8;">dbt-core & BigQuery</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Apply Filter Subsets
filtered_c360 = df_c360 if selected_segment == "All Segments" else df_c360[df_c360["customer_segment"] == selected_segment]
filtered_attr = df_attr if selected_source == "All Sources" else df_attr[df_attr["traffic_source"] == selected_source]
filtered_paid = paid_perf if selected_channel == "All Channels" else paid_perf[paid_perf["marketing_channel"] == selected_channel]


# ======================================================================
# SECTION 1: EXECUTIVE OVERVIEW
# ======================================================================
if nav_selection == "📊 Executive Overview":
    # Header Banner
    st.markdown("""
    <div class="dashboard-header">
        <div>
            <h1 class="dashboard-headline">Executive Overview</h1>
            <p class="dashboard-subhead">High-level enterprise performance metrics combining Customer 360, Multi-Touch Attribution, and Paid Media.</p>
        </div>
        <div class="header-badges">
            <span class="badge-chip">📅 Jan 10 – Jan 31, 2021</span>
            <span class="badge-chip">⚡ BigQuery dbt Marts</span>
            <span class="status-pill-live"><span class="status-dot-pulse"></span> Production Ready</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Core Metrics Aggregations
    total_customers = len(df_c360)
    total_orders = df_attr["order_id"].nunique()
    total_revenue = df_attr.drop_duplicates(subset=["order_id"])["order_amount"].sum()
    total_spend = float(paid_perf["total_spend"].sum())
    aov = total_revenue / total_orders if total_orders > 0 else 0.0
    total_customer_sessions = int(df_c360["total_sessions"].sum())

    # Executive KPI Cards (Row 1)
    k1, k2, k3, k4, k5, k6 = st.columns(6)

    with k1:
        st.markdown(f"""
        <div class="saas-card saas-card-accent-cyan">
            <div class="card-top">
                <span class="card-label">Total Revenue</span>
                <span class="card-icon">💰</span>
            </div>
            <div class="card-value">${total_revenue:,.2f}</div>
            <div class="card-footer-sub">
                <span class="card-pill-tag tag-blue">Verified</span> 1,000 transactions
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="saas-card saas-card-accent-emerald">
            <div class="card-top">
                <span class="card-label">Customers</span>
                <span class="card-icon">👥</span>
            </div>
            <div class="card-value">{total_customers:,}</div>
            <div class="card-footer-sub">
                <span class="card-pill-tag tag-green">CRM Active</span> 500 profiles
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="saas-card saas-card-accent-violet">
            <div class="card-top">
                <span class="card-label">Total Orders</span>
                <span class="card-icon">🛍️</span>
            </div>
            <div class="card-value">{total_orders:,}</div>
            <div class="card-footer-sub">
                <span class="card-pill-tag tag-violet">Completed</span> 100% integrity
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="saas-card saas-card-accent-amber">
            <div class="card-top">
                <span class="card-label">Average Order</span>
                <span class="card-icon">📊</span>
            </div>
            <div class="card-value">${aov:.2f}</div>
            <div class="card-footer-sub">
                Blended AOV per order
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k5:
        st.markdown(f"""
        <div class="saas-card saas-card-accent-rose">
            <div class="card-top">
                <span class="card-label">Total Ad Spend</span>
                <span class="card-icon">📢</span>
            </div>
            <div class="card-value">${total_spend:,.2f}</div>
            <div class="card-footer-sub">
                Google, Facebook, YouTube
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k6:
        st.markdown(f"""
        <div class="saas-card saas-card-accent-blue">
            <div class="card-top">
                <span class="card-label">GA4 Sessions</span>
                <span class="card-icon">🌐</span>
            </div>
            <div class="card-value">{total_customer_sessions:,}</div>
            <div class="card-footer-sub">
                400 resolved customers
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Attribution & Paid Performance Highlights Row
    tot_clicks = int(paid_perf["total_clicks"].sum())
    tot_impressions = int(paid_perf["total_impressions"].sum())
    blended_cpc = total_spend / tot_clicks if tot_clicks > 0 else 0.0
    blended_cpm = (total_spend * 1000.0) / tot_impressions if tot_impressions > 0 else 0.0
    unattr_df = df_attr[df_attr["campaign_name"] == "Unattributed"]
    unattr_orders_cnt = unattr_df["order_id"].nunique()
    unattr_rev_sum = unattr_df["order_amount"].sum()
    attr_orders_cnt = df_attr[df_attr["campaign_name"] != "Unattributed"]["order_id"].nunique()
    attr_orders_rev = df_attr[df_attr["campaign_name"] != "Unattributed"].drop_duplicates(subset=["order_id"])["order_amount"].sum()

    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;">
        <div style="background: rgba(21, 29, 48, 0.7); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px;">
            <div style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase;">Attributed Web Orders</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #38BDF8;">{attr_orders_cnt} orders <span style="font-size: 0.8rem; font-weight: 500; color: #94A3B8;">(${attr_orders_rev:,.2f})</span></div>
        </div>
        <div style="background: rgba(21, 29, 48, 0.7); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px;">
            <div style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase;">Unattributed Direct Orders</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #F59E0B;">{unattr_orders_cnt} orders <span style="font-size: 0.8rem; font-weight: 500; color: #94A3B8;">(${unattr_rev_sum:,.2f})</span></div>
        </div>
        <div style="background: rgba(21, 29, 48, 0.7); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px;">
            <div style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase;">Paid Traffic Engagement</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #34D399;">{tot_clicks:,} clicks <span style="font-size: 0.8rem; font-weight: 500; color: #94A3B8;">({tot_impressions:,} impr)</span></div>
        </div>
        <div style="background: rgba(21, 29, 48, 0.7); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px;">
            <div style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase;">Blended Media Efficiency</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #A78BFA;">${blended_cpc:.2f} CPC <span style="font-size: 0.8rem; font-weight: 500; color: #94A3B8;">(${blended_cpm:.2f} CPM)</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Executive Charts Row
    col_chart_left, col_chart_right = st.columns([3, 2])

    with col_chart_left:
        st.subheader("Daily Sales Velocity")
        daily_orders = df_attr.drop_duplicates(subset=["order_id"]).groupby("order_date").agg(
            revenue=("order_amount", "sum"),
            orders=("order_id", "nunique")
        ).reset_index()

        fig_daily = go.Figure()
        fig_daily.add_trace(go.Scatter(
            x=daily_orders["order_date"],
            y=daily_orders["revenue"],
            mode="lines+markers",
            name="Daily Revenue ($)",
            line=dict(color="#38BDF8", width=3, shape="spline"),
            marker=dict(size=6, color="#0284C7"),
            fill="tozeroy",
            fillcolor="rgba(56, 189, 248, 0.08)",
            hovertemplate="<b>Date:</b> %{x}<br><b>Revenue:</b> $%{y:,.2f}<extra></extra>"
        ))
        fig_daily = apply_saas_plotly_theme(fig_daily, height=350, show_legend=False)
        fig_daily.update_layout(title="Daily Revenue Trend (Jan 10–31, 2021)")
        st.plotly_chart(fig_daily, use_container_width=True)

    with col_chart_right:
        st.subheader("Revenue by Customer Segment")
        seg_rev = df_c360.groupby("customer_segment")["total_revenue"].sum().reset_index()
        segment_colors = {
            "Champions": "#10B981",
            "Loyal Customers": "#3B82F6",
            "Potential Loyalists": "#8B5CF6",
            "New Customers": "#06B6D4",
            "At Risk": "#F59E0B",
            "Others": "#64748B"
        }
        fig_seg = px.pie(
            seg_rev,
            names="customer_segment",
            values="total_revenue",
            hole=0.6,
            color="customer_segment",
            color_discrete_map=segment_colors
        )
        fig_seg = apply_saas_plotly_theme(fig_seg, height=350, show_legend=True)
        fig_seg.update_traces(
            textposition="inside",
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.2f}<br>Share: %{percent}<extra></extra>"
        )
        st.plotly_chart(fig_seg, use_container_width=True)

    # Real Calculated Strategic Business Insights
    st.markdown("""
    <div class="insight-card">
        <div class="insight-title">💡 Strategic Executive Insights & Lifecycle Synthesis</div>
        <div class="insight-body">
            • <b>High-Value Tier Dominance:</b> Champions and Loyal Customers make up <b>50.0%</b> of the CRM user base (250 customers) generating <b>$171,842.13</b> (71.4% of total revenue), confirming exceptional retention economics.<br>
            • <b>Web Acquisition Attribution:</b> <b>619 orders (61.9%)</b> were successfully influenced by pre-purchase GA4 sessions, with organic search (<code>google / organic</code>) and direct web visits driving the highest pipeline value.<br>
            • <b>Paid Media Channel Performance:</b> Google Search delivered the lowest acquisition unit cost at <b>$0.69 CPC</b>, while YouTube campaigns drove strong brand awareness with an efficient <b>$14.64 CPM</b> across 290,879 exposures.<br>
            • <b>Direct / Unattributed Baseline:</b> <b>381 orders ($91,956.77)</b> occurred without recorded pre-purchase GA4 web touchpoints, reflecting returning offline or direct CRM conversion paths.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ======================================================================
# SECTION 2: CUSTOMER 360 INTELLIGENCE
# ======================================================================
elif nav_selection == "👤 Customer 360":
    st.markdown("""
    <div class="dashboard-header">
        <div>
            <h1 class="dashboard-headline">Customer 360 Intelligence</h1>
            <p class="dashboard-subhead">Unified customer lifetime directory with RFM behavioral metrics, transaction history, and resolved web touchpoints.</p>
        </div>
        <div class="header-badges">
            <span class="badge-chip">👥 500 Profiles</span>
            <span class="badge-chip">442 Purchasing Accounts</span>
            <span class="status-pill-live"><span class="status-dot-pulse"></span> Active CRM Mart</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Top Distribution & RFM Charts
    c360_col1, c360_col2 = st.columns([3, 2])

    with c360_col1:
        st.subheader("Customer Distribution Across Lifecycle Tiers")
        seg_counts = filtered_c360["customer_segment"].value_counts().reset_index()
        seg_counts.columns = ["Segment", "Count"]
        segment_colors = {
            "Champions": "#10B981",
            "Loyal Customers": "#3B82F6",
            "Potential Loyalists": "#8B5CF6",
            "New Customers": "#06B6D4",
            "At Risk": "#F59E0B",
            "Others": "#64748B"
        }
        fig_tier = px.bar(
            seg_counts,
            x="Segment",
            y="Count",
            color="Segment",
            text="Count",
            color_discrete_map=segment_colors
        )
        fig_tier = apply_saas_plotly_theme(fig_tier, height=320, show_legend=False)
        fig_tier.update_traces(textposition="outside")
        st.plotly_chart(fig_tier, use_container_width=True)

    with c360_col2:
        st.subheader("RFM Matrix: Recency vs. Lifetime Spend")
        rfm_data = filtered_c360[filtered_c360["total_orders"] > 0]
        fig_rfm = px.scatter(
            rfm_data,
            x="recency_days",
            y="monetary_value",
            size="frequency",
            color="customer_segment",
            hover_name="name",
            color_discrete_map=segment_colors,
            labels={
                "recency_days": "Recency (Days Since Last Order)",
                "monetary_value": "Total Spend ($)",
                "frequency": "Orders"
            }
        )
        fig_rfm = apply_saas_plotly_theme(fig_rfm, height=320, show_legend=True)
        st.plotly_chart(fig_rfm, use_container_width=True)

    st.markdown("---")

    # Searchable Customer Directory
    st.subheader("Searchable Customer Profile Directory")
    search_query = st.text_input("🔎 Search profiles by customer name, customer ID, or city:", "")

    display_c360 = filtered_c360.copy()
    if search_query:
        display_c360 = display_c360[
            display_c360["name"].str.contains(search_query, case=False, na=False) |
            display_c360["customer_id"].str.contains(search_query, case=False, na=False) |
            display_c360["city"].str.contains(search_query, case=False, na=False)
        ]

    st.dataframe(
        display_c360[[
            "customer_id", "name", "email", "city", "signup_date",
            "customer_segment", "total_orders", "total_revenue", "average_order_value",
            "recency_days", "total_sessions"
        ]].rename(columns={
            "customer_id": "Customer ID",
            "name": "Full Name",
            "email": "Email",
            "city": "City",
            "signup_date": "Signup Date",
            "customer_segment": "Segment",
            "total_orders": "Orders",
            "total_revenue": "Lifetime Spend ($)",
            "average_order_value": "AOV ($)",
            "recency_days": "Recency (Days)",
            "total_sessions": "GA4 Sessions"
        }),
        use_container_width=True,
        height=280
    )

    st.markdown("---")

    # Customer Deep-Dive Inspector
    if len(display_c360) > 0:
        st.subheader("Customer Deep Dive Profile")
        cust_list = display_c360["customer_id"] + " — " + display_c360["name"] + " (" + display_c360["city"] + ")"
        selected_cust_str = st.selectbox("Select Customer Profile to Inspect:", cust_list)
        selected_cust_id = selected_cust_str.split(" — ")[0]
        cust_row = display_c360[display_c360["customer_id"] == selected_cust_id].iloc[0]

        # Profile Card Header
        initials = "".join([part[0] for part in cust_row["name"].split()[:2]]).upper()
        tier_color = segment_colors.get(cust_row["customer_segment"], "#94A3B8")

        st.markdown(f"""
        <div class="customer-profile-card">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div class="profile-avatar">{initials}</div>
                    <div>
                        <div style="font-size: 1.3rem; font-weight: 700; color: #FFFFFF;">{cust_row['name']}</div>
                        <div style="font-size: 0.82rem; color: #94A3B8;">ID: <code>{cust_row['customer_id']}</code> • {cust_row['email']} • {cust_row['city']}</div>
                    </div>
                </div>
                <div>
                    <span style="background: {tier_color}22; border: 1px solid {tier_color}66; color: {tier_color}; font-weight: 700; font-size: 0.85rem; padding: 6px 14px; border-radius: 9999px;">
                        {cust_row['customer_segment']}
                    </span>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-top: 18px; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.06);">
                <div>
                    <div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase;">Lifetime Spend</div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #38BDF8;">${cust_row['total_revenue']:,.2f}</div>
                </div>
                <div>
                    <div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase;">Total Orders</div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC;">{cust_row['total_orders']}</div>
                </div>
                <div>
                    <div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase;">Average Order Value</div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC;">${cust_row['average_order_value']:.2f}</div>
                </div>
                <div>
                    <div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase;">GA4 Web Sessions</div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #34D399;">{cust_row['total_sessions']}</div>
                </div>
                <div>
                    <div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase;">Days Since Last Order</div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC;">{cust_row['recency_days'] if pd.notnull(cust_row['recency_days']) else 'N/A'}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab_hist_orders, tab_hist_attr = st.tabs(["🛍️ Purchase History", "🌐 Attributed Web Touchpoints"])

        with tab_hist_orders:
            cust_orders = df_orders[df_orders["customer_id"] == selected_cust_id].sort_values("order_date", ascending=False)
            if len(cust_orders) > 0:
                st.dataframe(
                    cust_orders[["order_id", "order_date", "order_amount", "product_category"]].rename(
                        columns={
                            "order_id": "Order ID",
                            "order_date": "Date",
                            "order_amount": "Amount ($)",
                            "product_category": "Category"
                        }
                    ),
                    use_container_width=True
                )
            else:
                st.info("No recorded purchase transactions for this prospect.")

        with tab_hist_attr:
            cust_attr = df_attr[df_attr["customer_id"] == selected_cust_id].sort_values(["order_date", "touchpoint_rank"])
            if len(cust_attr) > 0:
                st.dataframe(
                    cust_attr[[
                        "order_id", "order_date", "traffic_source", "traffic_medium",
                        "touchpoint_rank", "total_touchpoints", "first_touch_credit",
                        "last_touch_credit", "time_decay_credit"
                    ]].rename(columns={
                        "order_id": "Order ID",
                        "order_date": "Date",
                        "traffic_source": "Source",
                        "traffic_medium": "Medium",
                        "touchpoint_rank": "Rank",
                        "total_touchpoints": "Total Touchpoints",
                        "first_touch_credit": "First-Touch",
                        "last_touch_credit": "Last-Touch",
                        "time_decay_credit": "Time-Decay"
                    }),
                    use_container_width=True
                )
            else:
                st.info("No web touchpoints logged for this customer.")


# ======================================================================
# SECTION 3: MARKETING ATTRIBUTION
# ======================================================================
elif nav_selection == "📢 Marketing Attribution":
    st.markdown("""
    <div class="dashboard-header">
        <div>
            <h1 class="dashboard-headline">Marketing Attribution Analytics</h1>
            <p class="dashboard-subhead">Multi-touch credit evaluation across First-Touch, Last-Touch, Linear, and Exponential Time-Decay models.</p>
        </div>
        <div class="header-badges">
            <span class="badge-chip">4 Models Compared</span>
            <span class="badge-chip">7-Day Half-Life Decay</span>
            <span class="status-pill-live"><span class="status-dot-pulse"></span> Production Mart</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Attribution Model Primer Row
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    with p_col1:
        st.markdown("""
        <div class="model-info-box" style="border-top: 2.5px solid #38BDF8;">
            <div class="model-info-title" style="color: #38BDF8;">First-Touch Attribution</div>
            <div class="model-info-desc">Awards 100% of order credit to the initial chronological touchpoint. Highlights brand awareness and top-of-funnel acquisition channels.</div>
        </div>
        """, unsafe_allow_html=True)
    with p_col2:
        st.markdown("""
        <div class="model-info-box" style="border-top: 2.5px solid #818CF8;">
            <div class="model-info-title" style="color: #818CF8;">Last-Touch Attribution</div>
            <div class="model-info-desc">Awards 100% of order credit to the final touchpoint prior to purchase. Identifies bottom-of-funnel conversion closers.</div>
        </div>
        """, unsafe_allow_html=True)
    with p_col3:
        st.markdown("""
        <div class="model-info-box" style="border-top: 2.5px solid #34D399;">
            <div class="model-info-title" style="color: #34D399;">Linear Attribution</div>
            <div class="model-info-desc">Distributes order credit equally (1/N) across all touchpoints in the customer journey. Balanced representation across full journey.</div>
        </div>
        """, unsafe_allow_html=True)
    with p_col4:
        st.markdown("""
        <div class="model-info-box" style="border-top: 2.5px solid #F472B6;">
            <div class="model-info-title" style="color: #F472B6;">Time-Decay Attribution</div>
            <div class="model-info-desc">Applies exponential 7-day half-life decay. Weight doubles for touchpoints occurring closer to the transaction date.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Attributed Revenue Aggregations
    attr_summary = filtered_attr.groupby(["traffic_source", "traffic_medium"]).agg(
        orders_influenced=("order_id", "nunique"),
        first_touch_rev=("first_touch_rev", "sum"),
        last_touch_rev=("last_touch_rev", "sum"),
        linear_rev=("linear_rev", "sum"),
        time_decay_rev=("time_decay_rev", "sum")
    ).reset_index()

    for col in ["first_touch_rev", "last_touch_rev", "linear_rev", "time_decay_rev"]:
        attr_summary[col] = attr_summary[col].round(2)

    attr_summary = attr_summary.sort_values("first_touch_rev", ascending=False)

    # Attribution Visualizations Row
    col_chart_attr, col_tbl_attr = st.columns([3, 2])

    with col_chart_attr:
        st.subheader("Model Comparison Across Acquisition Channels")
        melted_attr = attr_summary.melt(
            id_vars=["traffic_source", "traffic_medium"],
            value_vars=["first_touch_rev", "last_touch_rev", "linear_rev", "time_decay_rev"],
            var_name="Model",
            value_name="Revenue"
        )
        model_names = {
            "first_touch_rev": "First-Touch",
            "last_touch_rev": "Last-Touch",
            "linear_rev": "Linear",
            "time_decay_rev": "Time-Decay (7d)"
        }
        melted_attr["Model"] = melted_attr["Model"].map(model_names)
        melted_attr["Channel"] = melted_attr["traffic_source"] + " (" + melted_attr["traffic_medium"] + ")"

        fig_comp = px.bar(
            melted_attr,
            x="Channel",
            y="Revenue",
            color="Model",
            barmode="group",
            color_discrete_map={
                "First-Touch": "#38BDF8",
                "Last-Touch": "#818CF8",
                "Linear": "#34D399",
                "Time-Decay (7d)": "#F472B6"
            }
        )
        fig_comp = apply_saas_plotly_theme(fig_comp, height=360, show_legend=True)
        fig_comp.update_layout(title="Revenue ($USD) by Attribution Model")
        st.plotly_chart(fig_comp, use_container_width=True)

    with col_tbl_attr:
        st.subheader("Attributed Performance Table")
        st.dataframe(
            attr_summary.rename(columns={
                "traffic_source": "Source",
                "traffic_medium": "Medium",
                "orders_influenced": "Orders",
                "first_touch_rev": "First-Touch ($)",
                "last_touch_rev": "Last-Touch ($)",
                "linear_rev": "Linear ($)",
                "time_decay_rev": "Time-Decay ($)"
            }),
            use_container_width=True,
            height=360
        )

    st.markdown("---")

    # Multi-Touch Customer Journeys & Unattributed Orders
    col_mt, col_unattr = st.columns(2)

    with col_mt:
        st.subheader("Multi-Touch Customer Journey Inspector")
        st.caption("Orders influenced by 2 or more web sessions prior to purchase.")
        multi_touch_orders = filtered_attr[filtered_attr["total_touchpoints"] > 1].sort_values(["order_id", "touchpoint_rank"])
        st.dataframe(
            multi_touch_orders[[
                "order_id", "customer_id", "order_date", "order_amount",
                "traffic_source", "traffic_medium", "touchpoint_rank", "total_touchpoints",
                "first_touch_credit", "last_touch_credit", "time_decay_credit"
            ]].head(60).rename(columns={
                "order_id": "Order",
                "customer_id": "Customer",
                "order_date": "Date",
                "order_amount": "Amount ($)",
                "traffic_source": "Source",
                "traffic_medium": "Medium",
                "touchpoint_rank": "Rank",
                "total_touchpoints": "Total",
                "first_touch_credit": "First-Touch",
                "last_touch_credit": "Last-Touch",
                "time_decay_credit": "Time-Decay"
            }),
            use_container_width=True,
            height=260
        )

    with col_unattr:
        st.subheader("Unattributed Orders (No Pre-Order Web Session)")
        st.caption("Orders placed without prior recorded GA4 sessions. Classified as Unattributed.")
        unattr_orders = df_attr[df_attr["campaign_name"] == "Unattributed"]
        u1, u2 = st.columns(2)
        u1.metric("Unattributed Orders", f"{unattr_orders['order_id'].nunique():,}")
        u2.metric("Unattributed Revenue", f"${unattr_orders['order_amount'].sum():,.2f}")

        st.dataframe(
            unattr_orders[["order_id", "customer_id", "order_date", "order_amount", "traffic_source"]].head(60).rename(
                columns={
                    "order_id": "Order ID",
                    "customer_id": "Customer ID",
                    "order_date": "Date",
                    "order_amount": "Amount ($)",
                    "traffic_source": "Channel Label"
                }
            ),
            use_container_width=True,
            height=180
        )


# ======================================================================
# SECTION 4: PAID CAMPAIGN PERFORMANCE
# ======================================================================
elif nav_selection == "🎯 Paid Campaign Performance":
    st.markdown("""
    <div class="dashboard-header">
        <div>
            <h1 class="dashboard-headline">Paid Campaign Performance</h1>
            <p class="dashboard-subhead">Advertising spend analysis, engagement metrics, and unit economics across Google, Facebook, and YouTube.</p>
        </div>
        <div class="header-badges">
            <span class="badge-chip">6 Active Campaigns</span>
            <span class="badge-chip">3 Media Channels</span>
            <span class="status-pill-live"><span class="status-dot-pulse"></span> Unit Economics Live</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Dynamic KPI Aggregations
    tot_spend = float(filtered_paid["total_spend"].sum())
    tot_clicks = int(filtered_paid["total_clicks"].sum())
    tot_impressions = int(filtered_paid["total_impressions"].sum())
    avg_cpc = tot_spend / tot_clicks if tot_clicks > 0 else 0.0
    avg_cpm = (tot_spend * 1000.0) / tot_impressions if tot_impressions > 0 else 0.0

    # Top KPI Row
    p1, p2, p3, p4, p5 = st.columns(5)
    with p1:
        st.markdown(f"""
        <div class="saas-card saas-card-accent-rose">
            <div class="card-top">
                <span class="card-label">Total Ad Spend</span>
                <span class="card-icon">💳</span>
            </div>
            <div class="card-value">${tot_spend:,.2f}</div>
            <div class="card-footer-sub">Paid media investment</div>
        </div>
        """, unsafe_allow_html=True)

    with p2:
        st.markdown(f"""
        <div class="saas-card saas-card-accent-cyan">
            <div class="card-top">
                <span class="card-label">Total Clicks</span>
                <span class="card-icon">🖱️</span>
            </div>
            <div class="card-value">{tot_clicks:,}</div>
            <div class="card-footer-sub">Verified paid traffic</div>
        </div>
        """, unsafe_allow_html=True)

    with p3:
        st.markdown(f"""
        <div class="saas-card saas-card-accent-emerald">
            <div class="card-top">
                <span class="card-label">Total Impressions</span>
                <span class="card-icon">👁️</span>
            </div>
            <div class="card-value">{tot_impressions:,}</div>
            <div class="card-footer-sub">Ad impressions served</div>
        </div>
        """, unsafe_allow_html=True)

    with p4:
        st.markdown(f"""
        <div class="saas-card saas-card-accent-violet">
            <div class="card-top">
                <span class="card-label">Cost Per Click (CPC)</span>
                <span class="card-icon">⚡</span>
            </div>
            <div class="card-value">${avg_cpc:.2f}</div>
            <div class="card-footer-sub">Blended CPC efficiency</div>
        </div>
        """, unsafe_allow_html=True)

    with p5:
        st.markdown(f"""
        <div class="saas-card saas-card-accent-amber">
            <div class="card-top">
                <span class="card-label">Cost Per Mille (CPM)</span>
                <span class="card-icon">🎯</span>
            </div>
            <div class="card-value">${avg_cpm:.2f}</div>
            <div class="card-footer-sub">Cost per 1,000 views</div>
        </div>
        """, unsafe_allow_html=True)

    # Charts Row
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.subheader("Advertising Investment by Marketing Channel")
        channel_spend = paid_perf.groupby("marketing_channel")["total_spend"].sum().reset_index()
        fig_ch_spend = px.bar(
            channel_spend,
            x="marketing_channel",
            y="total_spend",
            text="total_spend",
            color="marketing_channel",
            color_discrete_map={
                "Google": "#4285F4",
                "Facebook": "#1877F2",
                "YouTube": "#FF0000"
            }
        )
        fig_ch_spend = apply_saas_plotly_theme(fig_ch_spend, height=340, show_legend=False)
        fig_ch_spend.update_traces(texttemplate="$%{text:,.2f}", textposition="outside")
        st.plotly_chart(fig_ch_spend, use_container_width=True)

    with col_c2:
        st.subheader("Efficiency Matrix: CPC vs. CPM")
        fig_unit = px.scatter(
            paid_perf,
            x="cost_per_click",
            y="cost_per_1000_impressions",
            size="total_spend",
            color="marketing_channel",
            hover_name="campaign_name",
            color_discrete_map={
                "Google": "#4285F4",
                "Facebook": "#1877F2",
                "YouTube": "#FF0000"
            },
            labels={
                "cost_per_click": "Cost Per Click (CPC $)",
                "cost_per_1000_impressions": "CPM ($/1k Views)",
                "marketing_channel": "Channel"
            }
        )
        fig_unit = apply_saas_plotly_theme(fig_unit, height=340, show_legend=True)
        st.plotly_chart(fig_unit, use_container_width=True)

    # Performance Breakdown Table
    st.subheader("Campaign Performance Breakdown")
    st.dataframe(
        filtered_paid[[
            "campaign_id", "campaign_name", "marketing_channel",
            "total_spend", "total_clicks", "total_impressions",
            "cost_per_click", "cost_per_1000_impressions"
        ]].rename(columns={
            "campaign_id": "Campaign ID",
            "campaign_name": "Campaign Name",
            "marketing_channel": "Channel",
            "total_spend": "Spend ($)",
            "total_clicks": "Clicks",
            "total_impressions": "Impressions",
            "cost_per_click": "CPC ($)",
            "cost_per_1000_impressions": "CPM ($)"
        }),
        use_container_width=True
    )

    # Strict Methodological Compliance Note
    st.markdown("""
    <div class="insight-card" style="border-left-color: #F59E0B;">
        <div class="insight-title" style="color: #F59E0B;">⚠️ Methodological Governance Notice</div>
        <div class="insight-body">
            As dictated by sound data analytics practices, ROAS, ROI, and CPA are <b>not calculated</b> between unrelated GA4 organic/referral sources and synthetic ad campaigns. Paid advertising spend and web acquisition channels are strictly kept separate to prevent false or misleading attribution claims.
        </div>
    </div>
    """, unsafe_allow_html=True)

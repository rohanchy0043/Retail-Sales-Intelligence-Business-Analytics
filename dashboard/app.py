from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "dashboard"))

from src.analysis import kpis, monthly_trend, discount_profitability
from src.analysis import monthly_seasonality
from src.customer_segmentation import rfm_segmentation
from src.forecasting import evaluate_monthly_forecast, forecast_monthly_sales
from src.insights import build_insights
from src.reporting import generate_summary_csv, generate_summary_pdf
from components import metric, filter_reset_button
from charts import monthly_chart, bar_chart, donut_chart, apply_layout


st.set_page_config(page_title="Retail Sales Intelligence", page_icon="📊", layout="wide")
st.markdown("""
<style>
[data-testid="stSidebar"] {background: #F8FAFC; border-right: 1px solid #E2E8F0;}
.block-container {padding: 1.25rem 2rem 2rem 2rem; max-width: 1500px;}
h1 {color: #0F172A; font-size: 2rem !important; margin-bottom: 0.25rem;}
div[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 4px 14px rgba(15,23,42,0.04);
}
div[data-testid="stMetricLabel"] {color: #64748B; font-weight: 600;}
div[data-testid="stMetricValue"] {color: #0F172A;}
.stTabs [data-baseweb="tab-list"] {gap: 6px; border-bottom: 1px solid #E2E8F0;}
.stTabs [data-baseweb="tab"] {height: 44px; padding: 0 14px;}
.stTabs [aria-selected="true"] {color: #1D4ED8 !important; border-bottom-color: #2563EB;}
.source-banner {
    display: inline-block;
    background: #EFF6FF;
    color: #1E40AF;
    border: 1px solid #BFDBFE;
    border-radius: 999px;
    padding: 5px 12px;
    font-size: 0.82rem;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data() -> pd.DataFrame:
    path = ROOT / "data" / "processed" / "cleaned_superstore.csv"
    if not path.exists():
        raise FileNotFoundError("Run: python src/data_cleaning.py")
    frame = pd.read_csv(path)
    frame["Order Date"] = pd.to_datetime(frame["Order Date"], errors="coerce")
    frame["Ship Date"] = pd.to_datetime(frame["Ship Date"], errors="coerce")
    return frame


try:
    data = load_data()
except Exception as exc:
    st.error(f"Data unavailable: {exc}")
    st.stop()

st.markdown('<span class="source-banner">Verified public dataset - Sample Superstore</span>', unsafe_allow_html=True)
st.title("Executive Intelligence Dashboard")
st.caption("Superstore retail performance - All KPIs, insights, and reports update with global filters")

with st.sidebar:
    st.header("Filters")
    min_date = data["Order Date"].min()
    max_date = data["Order Date"].max()
    date_range = st.date_input("Date range", (min_date, max_date), key="date_filter")
    region = st.multiselect("Region", sorted(data["Region"].dropna().unique()), key="region_filter")
    state = st.multiselect("State", sorted(data["State"].dropna().unique()), key="state_filter")
    category = st.multiselect("Category", sorted(data["Category"].dropna().unique()), key="category_filter")
    subcategory = st.multiselect("Subcategory", sorted(data["Sub-Category"].dropna().unique()), key="subcategory_filter")
    segment = st.multiselect("Customer segment", sorted(data["Segment"].dropna().unique()), key="segment_filter")
    ship_mode = st.multiselect("Ship mode", sorted(data["Ship Mode"].dropna().unique()), key="ship_filter")
    filter_reset_button()

filtered = data.copy()
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    filtered = filtered[(filtered["Order Date"] >= start) & (filtered["Order Date"] <= end)]
if region:
    filtered = filtered[filtered["Region"].isin(region)]
if state:
    filtered = filtered[filtered["State"].isin(state)]
if category:
    filtered = filtered[filtered["Category"].isin(category)]
if subcategory:
    filtered = filtered[filtered["Sub-Category"].isin(subcategory)]
if segment:
    filtered = filtered[filtered["Segment"].isin(segment)]
if ship_mode:
    filtered = filtered[filtered["Ship Mode"].isin(ship_mode)]

tabs = st.tabs([
    "Executive Overview", "Sales", "Products", "Regions", "Customers",
    "RFM Segmentation", "Forecast & Quality", "Insights", "Data Explorer", "Reports",
])
metrics = kpis(filtered)

with tabs[0]:
    cols = st.columns(4)
    cards = [
        ("Total Revenue", f"${metrics['Revenue']:,.0f}"),
        ("Total Profit", f"${metrics['Profit']:,.0f}"),
        ("Total Orders", f"{metrics['Orders']:,}"),
        ("Average Order Value", f"${metrics['AOV']:,.2f}"),
    ]
    for col, (label, value) in zip(cols, cards):
        with col:
            metric(label, value)
    cols = st.columns(3)
    cards = [
        ("Profit Margin", f"{metrics['Profit Margin']:.1%}"),
        ("Total Customers", f"{metrics['Customers']:,}"),
        (
            "Monthly Sales Growth",
            f"{metrics['Sales Growth']:+.1%}" if metrics["Sales Growth"] is not None else "N/A",
            "Latest month versus prior month",
        ),
    ]
    for col, card in zip(cols, cards):
        label, value = card[0], card[1]
        with col:
            metric(label, value, help_text=card[2] if len(card) > 2 else None)
    st.subheader("Performance snapshot")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(monthly_chart(filtered, "Sales", "Monthly Revenue", "#2563EB"), width="stretch")
    with c2:
        st.plotly_chart(monthly_chart(filtered, "Profit", "Monthly Profit", "#14B8A6"), width="stretch")

with tabs[1]:
    c1, c2 = st.columns(2)
    trend = monthly_trend(filtered)
    from charts import go
    fig = go.Figure()
    fig.add_bar(x=trend["Month"], y=trend["Revenue"], name="Revenue", marker_color="#2563EB")
    fig.add_trace(go.Scatter(x=trend["Month"], y=trend["Profit"], name="Profit", yaxis="y2", line=dict(color="#14B8A6", width=3)))
    fig.update_layout(title="Revenue vs Profit", yaxis=dict(title="Revenue"), yaxis2=dict(title="Profit", overlaying="y", side="right"), legend=dict(orientation="h"))
    apply_layout(fig)
    with c1:
        st.plotly_chart(fig, width="stretch")
    with c2:
        trend["Growth"] = trend["Revenue"].pct_change().fillna(0)
        import plotly.express as px
        growth_fig = px.area(trend, x="Month", y="Growth", title="Month-over-Month Sales Growth")
        growth_fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(apply_layout(growth_fig), width="stretch")
    seasonality = monthly_seasonality(filtered)
    if not seasonality.empty:
        import plotly.express as px
        seasonality_fig = px.bar(
            seasonality, x="Month Name", y="Seasonality Index",
            title="Seasonality Index by Calendar Month",
            labels={"Seasonality Index": "Index (1.0 = average month)"},
            color="Seasonality Index", color_continuous_scale=["#BFDBFE", "#1D4ED8"],
        )
        seasonality_fig.add_hline(y=1, line_dash="dash", line_color="#64748B")
        st.plotly_chart(apply_layout(seasonality_fig), width="stretch")

with tabs[2]:
    product_profit = filtered.groupby("Product Name", observed=True)["Profit"].sum().nlargest(10).reset_index()
    product_loss = filtered.groupby("Product Name", observed=True)["Profit"].sum().nsmallest(10).reset_index()
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(bar_chart(product_profit, "Profit", "Product Name", "Top 10 Products by Profit", True), width="stretch")
    with c2:
        st.plotly_chart(bar_chart(product_loss, "Profit", "Product Name", "Bottom 10 Products by Profit", True, "#EF4444"), width="stretch")
    c1, c2 = st.columns(2)
    category_sales = filtered.groupby("Category", observed=True)["Sales"].sum().reset_index()
    subcategory_profit = filtered.groupby("Sub-Category", observed=True)["Profit"].sum().sort_values().reset_index()
    with c1:
        st.plotly_chart(donut_chart(category_sales, "Category", "Sales", "Category Sales"), width="stretch")
    with c2:
        st.plotly_chart(bar_chart(subcategory_profit, "Profit", "Sub-Category", "Subcategory Profitability", True), width="stretch")

with tabs[3]:
    region_data = filtered.groupby("Region", observed=True).agg(Revenue=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
    state_data = filtered.groupby("State", observed=True)["Sales"].sum().nlargest(15).reset_index()
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(bar_chart(region_data, "Region", "Revenue", "Revenue by Region"), width="stretch")
    with c2:
        st.plotly_chart(bar_chart(region_data, "Region", "Profit", "Profit by Region", color="#14B8A6"), width="stretch")
    st.plotly_chart(bar_chart(state_data, "Sales", "State", "Top 15 States by Sales", True), width="stretch")

with tabs[4]:
    segment_data = filtered.groupby("Segment", observed=True)["Sales"].sum().reset_index()
    customer_data = filtered.groupby(["Customer ID", "Customer Name"], observed=True)["Sales"].sum().nlargest(10).reset_index()
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(donut_chart(segment_data, "Segment", "Sales", "Revenue by Customer Segment"), width="stretch")
    with c2:
        st.plotly_chart(bar_chart(customer_data, "Sales", "Customer Name", "Top Customers", True), width="stretch")
    order_counts = filtered.groupby("Order ID", observed=True).size().reset_index(name="Line Items")
    import plotly.express as px
    st.plotly_chart(apply_layout(px.histogram(order_counts, x="Line Items", nbins=10, title="Line Items per Order")), width="stretch")

with tabs[5]:
    st.subheader("Customer value segments")
    rfm = rfm_segmentation(filtered)
    if rfm.empty:
        st.info("No customer records match the selected filters.")
    else:
        segment_summary = rfm.groupby("RFM Segment", observed=True).agg(
            Customers=("Customer ID", "nunique"),
            Revenue=("Monetary", "sum"),
            Average_Frequency=("Frequency", "mean"),
        ).reset_index().sort_values("Customers", ascending=False)
        c1, c2 = st.columns([1, 2])
        with c1:
            st.plotly_chart(
                donut_chart(segment_summary, "RFM Segment", "Customers", "Customers by RFM Segment"),
                width="stretch",
            )
        with c2:
            st.plotly_chart(
                bar_chart(segment_summary, "Revenue", "RFM Segment", "Revenue by RFM Segment", True),
                width="stretch",
            )
        st.caption("Recency, order frequency, and monetary sales are scored into quartiles. Segments describe the currently filtered dataset.")
        st.dataframe(
            rfm[["Customer ID", "Customer Name", "Recency", "Frequency", "Monetary", "R Score", "F Score", "M Score", "RFM Segment"]],
            width="stretch", hide_index=True,
        )

with tabs[6]:
    c1, c2 = st.columns([2, 1])
    with c1:
        try:
            forecast, forecast_meta = forecast_monthly_sales(filtered)
            from charts import go
            future = forecast[forecast["Type"] == "Forecast"]
            history = forecast[forecast["Type"] == "Actual"]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=history["Period"], y=history["Actual"], name="Actual", line=dict(color="#2563EB")))
            fig.add_trace(go.Scatter(x=forecast["Period"], y=forecast["Forecast"], name="Trend / forecast", line=dict(color="#F97316", dash="dash")))
            if not future.empty:
                fig.add_trace(go.Scatter(
                    x=list(future["Period"]) + list(future["Period"][::-1]),
                    y=list(future["Upper"]) + list(future["Lower"][::-1]),
                    fill="toself", fillcolor="rgba(249,115,22,0.12)", line=dict(color="rgba(0,0,0,0)"),
                    hoverinfo="skip", showlegend=True, name="Forecast interval",
                ))
            fig.update_layout(title="Historical Sales and 3-Month Baseline Forecast", yaxis_title="Revenue")
            st.plotly_chart(apply_layout(fig), width="stretch")
            st.caption(f"{forecast_meta['method']}. {forecast_meta['limitations']}")
            evaluation = evaluate_monthly_forecast(filtered)
            score_cols = st.columns(3)
            score_cols[0].metric(f"Holdout MAE ({evaluation['holdout_months']} months)", f"${evaluation['mae']:,.0f}")
            score_cols[1].metric("Holdout MAPE", f"{evaluation['mape']:.1f}%" if evaluation["mape"] is not None else "N/A")
            score_cols[2].metric("Naive baseline MAE", f"${evaluation['naive_mae']:,.0f}")
            test_frame = pd.DataFrame({
                "Month": evaluation["periods"],
                "Actual": evaluation["actual"],
                "Predicted": evaluation["predicted"],
            })
            st.dataframe(test_frame, width="stretch", hide_index=True)
        except Exception as exc:
            st.warning(f"Forecast unavailable: {exc}")
    with c2:
        st.subheader("Discount vs Profit")
        discount = discount_profitability(filtered)
        st.dataframe(discount, width="stretch", hide_index=True)

    anomaly = filtered.groupby("Month", observed=True)["Sales"].sum()
    if len(anomaly) >= 3:
        z = (anomaly - anomaly.mean()) / anomaly.std(ddof=0)
        anomalous = z[(z > 2) | (z < -2)]
        st.subheader("Anomaly detection")
        if anomalous.empty:
            st.info("No monthly sales period exceeded the z-score threshold of ±2.")
        else:
            st.warning("Unusual monthly sales: " + ", ".join(anomalous.index.astype(str)))

with tabs[7]:
    insight = build_insights(filtered)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Data-backed observations")
        for item in insight["observations"]:
            st.success(item)
    with c2:
        st.subheader("Recommended actions")
        for item in insight["recommendations"]:
            st.info(item)

with tabs[8]:
    search = st.text_input("Search product, customer, city, or order")
    explorer = filtered.copy()
    if search:
        text = "|".join(["Order ID", "Customer Name", "Product Name", "City"])
        mask = explorer[text].astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
        explorer = explorer[mask]
    page_size = st.selectbox("Rows per page", [25, 50, 100], index=1)
    total_pages = max(1, (len(explorer) + page_size - 1) // page_size)
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
    start = (page - 1) * page_size
    st.caption(f"{len(explorer):,} matching rows • Page {page} of {total_pages}")
    st.dataframe(explorer.iloc[start:start + page_size], width="stretch", hide_index=True)
    st.download_button("Download filtered CSV", filtered.to_csv(index=False).encode("utf-8"),
                       file_name="retail_filtered_export.csv", mime="text/csv", width="stretch")

with tabs[9]:
    st.subheader("Automated business reports")
    st.caption("Downloads reflect the active date, region, category, customer, and shipping filters.")
    report_col1, report_col2 = st.columns(2)
    with report_col1:
        st.download_button(
            "Download executive report (PDF)",
            generate_summary_pdf(filtered),
            file_name="retail_executive_report.pdf",
            mime="application/pdf",
            width="stretch",
        )
    with report_col2:
        st.download_button(
            "Download KPI and insights report (CSV)",
            generate_summary_csv(filtered),
            file_name="retail_executive_report.csv",
            mime="text/csv",
            width="stretch",
        )

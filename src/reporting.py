from io import BytesIO, StringIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

from src.analysis import kpis
from src.customer_segmentation import rfm_segmentation
from src.insights import build_insights


def report_tables(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    metrics = kpis(frame)
    kpi_table = pd.DataFrame([{"Metric": key, "Value": value} for key, value in metrics.items()])
    insight_data = build_insights(frame)
    insight_table = pd.DataFrame(
        [{"Type": "Observation", "Finding": text} for text in insight_data["observations"]]
        + [{"Type": "Recommendation", "Finding": text} for text in insight_data["recommendations"]]
    )
    rfm = rfm_segmentation(frame)
    segment_table = rfm.groupby("RFM Segment", observed=True).agg(
        Customers=("Customer ID", "nunique"),
        Revenue=("Monetary", "sum"),
        Average_Orders=("Frequency", "mean"),
    ).reset_index()
    return {"kpis": kpi_table, "insights": insight_table, "rfm_segments": segment_table}


def generate_summary_csv(frame: pd.DataFrame) -> bytes:
    tables = report_tables(frame)
    rows = []
    for _, row in tables["kpis"].iterrows():
        rows.append({"Record Type": "KPI", "Name": row["Metric"], "Value": row["Value"], "Details": ""})
    for _, row in tables["insights"].iterrows():
        rows.append({"Record Type": row["Type"], "Name": row["Finding"], "Value": "", "Details": ""})
    for _, row in tables["rfm_segments"].iterrows():
        rows.append({
            "Record Type": "RFM Segment",
            "Name": row["RFM Segment"],
            "Value": row["Customers"],
            "Details": f"Revenue=${row['Revenue']:.2f}; Average orders/customer={row['Average_Orders']:.2f}",
        })
    output = StringIO()
    pd.DataFrame(rows, columns=["Record Type", "Name", "Value", "Details"]).to_csv(output, index=False)
    return output.getvalue().encode("utf-8-sig")


def generate_summary_pdf(frame: pd.DataFrame) -> bytes:
    tables = report_tables(frame)
    kpis_table = tables["kpis"]
    insights_table = tables["insights"]
    segments_table = tables["rfm_segments"]
    buffer = BytesIO()

    with PdfPages(buffer) as pdf:
        fig, ax = plt.subplots(figsize=(11.7, 8.3))
        ax.axis("off")
        ax.text(0.03, 0.95, "Retail Sales Executive Report", fontsize=22, weight="bold", color="#0F172A")
        ax.text(0.03, 0.90, "Public Sample Superstore dataset | Based on current dashboard filters", fontsize=10, color="#475569")
        values = {row["Metric"]: row["Value"] for _, row in kpis_table.iterrows()}
        kpi_lines = [
            f"Revenue: ${values['Revenue']:,.2f}",
            f"Profit: ${values['Profit']:,.2f}",
            f"Orders: {int(values['Orders']):,}",
            f"Average order value: ${values['AOV']:,.2f}",
            f"Profit margin: {values['Profit Margin']:.1%}",
            f"Customers: {int(values['Customers']):,}",
            (
                f"Latest monthly sales growth: {values['Sales Growth']:.1%}"
                if values.get("Sales Growth") is not None
                else "Latest monthly sales growth: N/A (need two months)"
            ),
        ]
        ax.text(0.04, 0.83, "\n".join(kpi_lines), fontsize=13, va="top", linespacing=1.6, color="#1E293B")
        y = 0.56
        ax.text(0.04, y, "Data-backed observations", fontsize=14, weight="bold", color="#0F172A")
        y -= 0.045
        for _, row in insights_table[insights_table["Type"] == "Observation"].iterrows():
            ax.text(0.06, y, f"• {row['Finding']}", fontsize=9.5, va="top", wrap=True, color="#334155")
            y -= 0.052
        y -= 0.02
        ax.text(0.04, y, "RFM customer segments", fontsize=14, weight="bold", color="#0F172A")
        y -= 0.04
        if segments_table.empty:
            ax.text(0.06, y, "No customers available in this filter selection.", fontsize=10)
        else:
            rows = [
                f"{row['RFM Segment']}: {int(row['Customers']):,} customers | ${row['Revenue']:,.2f} revenue"
                for _, row in segments_table.sort_values("Customers", ascending=False).iterrows()
            ]
            ax.text(0.06, y, "\n".join(rows), fontsize=9.5, va="top", linespacing=1.5, color="#334155")
        ax.text(0.03, 0.025, "Forecasts and segments are analytical estimates, not guarantees of future results.", fontsize=8, color="#64748B")
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        recommendations = insights_table[insights_table["Type"] == "Recommendation"]
        fig, ax = plt.subplots(figsize=(11.7, 8.3))
        ax.axis("off")
        ax.text(0.03, 0.95, "Recommended Actions", fontsize=22, weight="bold", color="#0F172A")
        y = 0.86
        for index, row in enumerate(recommendations["Finding"], start=1):
            ax.text(0.05, y, f"{index}. {row}", fontsize=12, va="top", wrap=True, color="#334155")
            y -= 0.10
        ax.text(0.03, 0.025, "Generated from the current dashboard-filtered data.", fontsize=8, color="#64748B")
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

    return buffer.getvalue()

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.analysis import kpis, monthly_seasonality, monthly_trend
from src.customer_segmentation import rfm_segmentation
from src.data_cleaning import clean_retail_data
from src.forecasting import evaluate_monthly_forecast, forecast_monthly_sales
from src.insights import build_insights
from src.reporting import generate_summary_csv, generate_summary_pdf
from dashboard.charts import bar_chart


def test_kpis_are_independent_calculations():
    frame = pd.DataFrame({
        "Sales": [100.0, 300.0],
        "Profit": [20.0, 30.0],
        "Order ID": ["A", "B"],
        "Customer ID": ["C1", "C2"],
    })
    result = kpis(frame)
    assert result["Revenue"] == 400
    assert result["Profit"] == 50
    assert result["AOV"] == 200
    assert result["Profit Margin"] == 0.125
    assert result["Customers"] == 2


def test_cleaning_removes_duplicates_negative_sales_and_bad_dates():
    frame = pd.DataFrame({
        "Order ID": ["A", "A", "B", "C"],
        "Order Date": ["2026-01-01", "2026-01-01", "2026-01-02", "2026-01-03"],
        "Ship Date": ["2026-01-03", "2026-01-03", "2026-01-01", "2026-01-05"],
        "Sales": [100, 100, -10, 200],
        "Quantity": [1, 1, 1, 0],
        "Profit": [10, 10, -2, 20],
    })
    clean, audit = clean_retail_data(frame)
    assert len(clean) == 1
    assert audit["duplicate_rows_removed"] == 1
    assert audit["invalid_rows_removed"]["negative_sales"] == 1
    assert clean.iloc[0]["Ship Date"] > clean.iloc[0]["Order Date"]


def test_forecast_returns_requested_period_count():
    frame = pd.DataFrame({
        "Month": ["2026-01", "2026-02", "2026-03", "2026-04"],
        "Sales": [100, 110, 120, 130],
    })
    forecast, meta = forecast_monthly_sales(frame, 3)
    assert sum(forecast["Type"] == "Forecast") == 3
    assert "method" in meta


def test_insights_are_calculated_not_hardcoded():
    frame = pd.DataFrame({
        "Region": ["West", "West", "East"],
        "Profit": [100, 50, -20],
        "Category": ["Tech", "Tech", "Office"],
        "Segment": ["Corporate", "Corporate", "Consumer"],
        "Sales": [300, 200, 100],
        "Month": ["2026-01", "2026-02", "2026-01"],
        "Product Name": ["A", "B", "C"],
    })
    result = build_insights(frame)
    assert any("West" in item for item in result["observations"])
    assert any("C" in item for item in result["observations"] if "largest loss" in item)


def test_rfm_segments_are_calculated_from_order_history():
    frame = pd.DataFrame({
        "Customer ID": ["C1", "C1", "C2", "C3"],
        "Customer Name": ["One", "One", "Two", "Three"],
        "Order ID": ["A", "B", "C", "D"],
        "Order Date": ["2026-03-01", "2026-03-15", "2025-01-01", "2026-03-10"],
        "Sales": [100, 200, 50, 20],
    })
    result = rfm_segmentation(frame)
    assert result.loc[result["Customer ID"] == "C1", "Frequency"].iloc[0] == 2
    assert result.loc[result["Customer ID"] == "C1", "Monetary"].iloc[0] == 300
    assert set(result["RFM Segment"]).issubset({
        "Champions", "Loyal Customers", "At Risk", "New Customers",
        "Hibernating", "Potential Loyalists", "Needs Attention",
    })


def test_forecast_backtest_and_seasonality_return_measurable_results():
    dates = pd.date_range("2024-01-01", periods=24, freq="MS")
    frame = pd.DataFrame({
        "Order Date": dates,
        "Month": dates.strftime("%Y-%m"),
        "Year": dates.year,
        "Sales": [100 + i * 5 + dates[i].month * 2 for i in range(len(dates))],
    })
    evaluation = evaluate_monthly_forecast(frame, holdout_months=3)
    seasonality = monthly_seasonality(frame)
    assert len(evaluation["actual"]) == 3
    assert evaluation["mae"] >= 0
    assert len(seasonality) == 12


def test_reports_generate_pdf_and_csv_bytes():
    frame = pd.DataFrame({
        "Customer ID": ["C1", "C1", "C2"],
        "Customer Name": ["One", "One", "Two"],
        "Order ID": ["A", "B", "C"],
        "Order Date": pd.to_datetime(["2026-01-01", "2026-02-01", "2026-02-10"]),
        "Month": ["2026-01", "2026-02", "2026-02"],
        "Region": ["West", "West", "East"],
        "Profit": [15, 20, -3],
        "Category": ["Tech", "Tech", "Office"],
        "Segment": ["Consumer", "Consumer", "Corporate"],
        "Sales": [100, 200, 50],
        "Product Name": ["P1", "P1", "P2"],
    })
    pdf = generate_summary_pdf(frame)
    csv_report = generate_summary_csv(frame)
    assert pdf.startswith(b"%PDF")
    assert b"Record Type,Name,Value,Details" in csv_report
    assert b"RFM Segment" in csv_report


def test_horizontal_bar_chart_keeps_numeric_axis_horizontal():
    chart = bar_chart(pd.DataFrame({"Revenue": [120.0], "Region": ["West"]}), "Revenue", "Region", "Revenue", True)
    assert list(chart.data[0].x) == [120.0]
    assert list(chart.data[0].y) == ["West"]

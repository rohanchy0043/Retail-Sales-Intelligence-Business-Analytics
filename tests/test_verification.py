import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import duckdb
import pandas as pd
from streamlit.testing.v1 import AppTest


def test_dashboard_opens_with_correct_kpis_and_download():
    app = AppTest.from_file(str(ROOT / "dashboard" / "app.py"), default_timeout=30).run()
    assert not app.exception
    values = {metric.label: metric.value for metric in app.metric}
    assert values["Total Revenue"] == "$2,297,201"
    assert values["Total Profit"] == "$286,397"
    assert values["Total Orders"] == "5,009"
    assert values["Average Order Value"] == "$458.61"
    assert values["Profit Margin"] == "12.5%"
    assert values["Total Customers"] == "793"
    assert len(app.get("plotly_chart")) >= 15
    assert len(app.get("download_button")) == 3


def test_region_and_date_filters_update_kpis():
    app = AppTest.from_file(str(ROOT / "dashboard" / "app.py"), default_timeout=30).run()
    app.sidebar.multiselect[0].set_value(["West"]).run()
    assert not app.exception
    west = {metric.label: metric.value for metric in app.metric}
    assert west["Total Revenue"] == "$725,458"

    app.sidebar.date_input[0].set_value(("2017-01-01", "2017-12-31")).run()
    assert not app.exception
    dated = {metric.label: metric.value for metric in app.metric}
    assert dated["Total Revenue"] == "$250,128"


def test_sql_scripts_execute_against_cleaned_csv():
    connection = duckdb.connect()
    frame = pd.read_csv(ROOT / "data" / "processed" / "cleaned_superstore.csv")
    connection.register("source_data", frame)
    connection.execute(
        '''
        CREATE TABLE retail_transactions AS
        SELECT
            "Row ID" AS row_id,
            "Order ID" AS order_id,
            CAST("Order Date" AS DATE) AS order_date,
            CAST("Ship Date" AS DATE) AS ship_date,
            "Ship Mode" AS ship_mode,
            "Customer ID" AS customer_id,
            "Customer Name" AS customer_name,
            "Segment" AS segment,
            "Country" AS country,
            "City" AS city,
            "State" AS state,
            "Postal Code" AS postal_code,
            "Region" AS region,
            "Category" AS category,
            "Sub-Category" AS sub_category,
            "Product Name" AS product_name,
            "Sales" AS sales,
            "Quantity" AS quantity,
            "Discount" AS discount,
            "Profit" AS profit,
            "Year" AS year,
            "Month" AS month,
            "Quarter" AS quarter,
            "Delivery Days" AS delivery_days,
            "Profit Margin" AS profit_margin
        FROM source_data
        '''
    )

    for sql_file in [
        ROOT / "sql" / "sales_analysis.sql",
        ROOT / "sql" / "product_analysis.sql",
        ROOT / "sql" / "customer_analysis.sql",
        ROOT / "sql" / "advanced_queries.sql",
    ]:
        statements = [
            " ".join(line for line in block.splitlines() if not line.strip().startswith("--")).strip()
            for block in sql_file.read_text(encoding="utf-8").split(";")
        ]
        for statement in statements:
            if statement:
                connection.execute(statement).fetchall()

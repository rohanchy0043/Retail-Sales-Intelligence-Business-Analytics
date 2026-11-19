# Retail Sales Intelligence & Business Analytics

An end-to-end retail analytics project built with Python, SQL, and Streamlit. It uses a public retail
dataset to demonstrate data cleaning, executive reporting, customer segmentation, forecasting, and
interactive business analysis.

## Overview

The dashboard helps users explore revenue, profit, order activity, product and regional performance,
customer behavior, and changes over time. Dashboard KPIs, charts, insights, and report downloads respond
to the active filters.

## Dataset

This project uses the public **Sample - Superstore** dataset from Kaggle:

- Dataset page: [Superstore Dataset Final](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)
- Source file: `data/raw/superstore/Sample - Superstore.csv`
- Source rows: 9,994
- Fields include orders, dates, customers, geography, products, sales, quantity, discounts, profit, and shipping.

The source and its limitations are documented in [data/raw/DATA_SOURCE.md](data/raw/DATA_SOURCE.md).
The dataset is public demonstration data; do not treat it as a live company's operational data.

## Features

### Executive Intelligence Dashboard

- Revenue, profit, orders, average order value, profit margin, customers, and latest month-over-month revenue growth
- Monthly revenue and profit trends, sales growth, and calendar-month seasonality index
- Product, category, subcategory, regional, state, and customer analysis
- Global filters for date, region, state, category, subcategory, customer segment, and shipping mode
- Adapts to Streamlit's active light/dark theme for the dashboard, controls, KPI cards, and charts
- Searchable and paginated transaction explorer with filtered CSV export

### Customer Segmentation

RFM analysis scores customers by recency of purchase, distinct order frequency, and monetary sales.
It groups customers into data-derived segments such as Champions, Loyal Customers, At Risk, and
Potential Loyalists. Scores are calculated within the currently selected dataset and are relative
quartile rankings, not fixed customer labels.

### Predictive Analytics

- Three-month baseline sales forecast with a displayed uncertainty interval
- Holdout evaluation on the latest three available months with MAE and MAPE
- Naive last-value baseline comparison
- Monthly sales anomaly detection using a z-score threshold

Forecasts are estimates, not guarantees. The baseline trend does not model promotions, inventory,
seasonality, or external events. The seasonality chart is descriptive and should not be read as a
causal or predictive model.

### Automated Business Reports

The Reports tab downloads a PDF executive summary and a CSV containing KPIs, generated observations,
recommendations, and aggregated RFM results. Downloads reflect current dashboard filters.

## Technology

- Python 3
- Pandas, NumPy
- Matplotlib, Seaborn, Plotly
- Streamlit
- PostgreSQL-oriented SQL
- DuckDB for automated SQL verification
- Pytest

## Project structure

```text
data/
  raw/                  Public source CSV and source note
  processed/            Cleaned dataset and Power BI-ready export
notebooks/              Exploration, cleaning, and sales analysis notebooks
src/                    Cleaning, analytics, forecasting, segmentation, and reporting modules
dashboard/              Streamlit app and reusable chart/UI components
sql/                    Schema and sales, product, customer, and advanced queries
reports/                Data quality, business insights, and verification reports
tests/                  Unit, dashboard, and SQL tests
```

## Setup

Requires Python 3.10 or later.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell prevents environment activation, run commands with the environment's Python executable:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run the project

From the repository root:

```powershell
python src/data_cleaning.py
python src/export_powerbi.py
streamlit run dashboard/app.py
```

Open the local URL printed by Streamlit. The cleaned dataset is created at
`data/processed/cleaned_superstore.csv`; the optional Power BI export is
`data/processed/powerbi_export.csv`.

Run the automated tests with:

```powershell
python -m pytest -q
```

## Data cleaning

The cleaning pipeline parses dates and numeric fields, trims text values, removes exact duplicate rows,
excludes records with missing required fields, negative sales, or non-positive quantities, and flags
ship dates before order dates by replacing those ship dates with missing values. It adds year, month,
quarter, delivery days, and profit margin fields.

Cleaning details and row counts are written to `reports/data_quality_report.md`. No record exclusions
should be interpreted without reviewing that report.

## SQL analysis

`sql/schema.sql` defines a PostgreSQL table. The other SQL files demonstrate aggregations, CTEs,
window functions, rankings, running totals, year-over-year and month-over-month comparisons, and
customer/product analysis.

Example PostgreSQL import after creating the table:

```sql
\copy retail_transactions FROM 'data/processed/cleaned_superstore.csv' CSV HEADER
```

Run the scripts in a PostgreSQL-compatible environment. The automated test suite also executes their
queries against a temporary DuckDB table built from the cleaned CSV.

## Reports and notebooks

- `reports/data_quality_report.md` — cleaning actions and impact
- `reports/business_insights.md` — how to interpret generated findings and recommendations
- `reports/verification_report.md` — project checks
- `notebooks/01_data_exploration.ipynb`
- `notebooks/02_data_cleaning.ipynb`
- `notebooks/03_sales_analysis.ipynb`

## Limitations

- The dataset is a public sample dataset and may not represent current retail conditions.
- RFM values and segment labels depend on the active filters and are relative to the selected rows.
- Forecasting uses a simple trend model; backtest metrics are historical diagnostics, not a guarantee of future performance.
- The z-score anomaly method assumes a reasonably comparable monthly series and can flag seasonal changes as unusual.

## Future improvements

- Add rolling-origin forecast evaluation and compare additional seasonal baselines.
- Add drill-down cohort analysis and customer retention views.
- Automate data ingestion and deployment.
- Add dashboard screenshots after capturing them from a running instance.

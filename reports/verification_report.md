# Verification Report

Verification performed against the cleaned public Sample Superstore dataset.

## Results

| Check | Result |
|---|---|
| Dashboard loads through Streamlit AppTest | Passed |
| Total revenue KPI | Passed - $2,297,201 |
| Total profit KPI | Passed - $286,397 |
| Total orders KPI | Passed - 5,009 |
| Average order value KPI | Passed - $458.61 |
| Profit margin KPI | Passed - 12.5% |
| Total customers KPI | Passed - 793 |
| Plotly chart rendering | Passed - charts present |
| Region filter | Passed - West revenue $725,458 |
| Date filter | Passed - 2017 revenue $250,128 |
| CSV download control | Passed - button present |
| RFM segmentation | Passed - customer segments calculated from filtered order history |
| Seasonality analysis | Passed - monthly index calculated from actual monthly revenue |
| Forecast holdout evaluation | Passed - MAE/MAPE and naive baseline available |
| PDF and executive CSV report downloads | Passed |
| SQL analysis scripts | Passed in DuckDB |
| Automated test suite | Passed - 11 tests |
| Python runtime exceptions | None |

## Independent calculation

The dashboard values were independently calculated from `data/processed/cleaned_superstore.csv` with
Pandas and match the Streamlit KPI cards.

## SQL validation

All statements in `sql/sales_analysis.sql`, `sql/product_analysis.sql`,
`sql/customer_analysis.sql`, and `sql/advanced_queries.sql` were executed against an in-memory
DuckDB table created from the cleaned CSV.

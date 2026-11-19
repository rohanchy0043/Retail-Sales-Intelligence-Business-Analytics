# Business Insights and Recommendations

Insights in this report are generated dynamically from the loaded, filtered dataset by
`src/insights.py`. The Streamlit dashboard also recalculates observations as users apply
filters.

Run the dashboard and review the **Insights** tab to see current data-backed findings.

The **RFM Segmentation** tab groups customers using recency since last order, distinct order frequency,
and monetary sales value. Scoring uses relative quartiles within the active filtered data; segment labels
are analytical classifications rather than fixed customer identities.

The **Reports** tab creates a filtered executive PDF plus a CSV containing KPI values, observations,
recommendations, and aggregated RFM segment results.

## Recommended review framework

1. Prioritize the most profitable region and category, but compare absolute profit with revenue concentration.
2. Review every loss-making product for excessive discounts, freight, and sourcing costs.
3. Compare customer segments by revenue and profit margin rather than revenue alone.
4. Investigate sales and profit anomalies using the displayed z-score view.
5. Treat the three-month forecast as a baseline trend only; compare its displayed holdout metrics against
   the naive baseline before considering operational use.

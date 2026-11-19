-- 1. Total revenue
SELECT ROUND(SUM(sales)::numeric, 2) AS total_revenue FROM retail_transactions;

-- 2. Total profit
SELECT ROUND(SUM(profit)::numeric, 2) AS total_profit FROM retail_transactions;

-- 3. Total orders
SELECT COUNT(DISTINCT order_id) AS total_orders FROM retail_transactions;

-- 4. Average order value
SELECT ROUND(SUM(sales) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS average_order_value
FROM retail_transactions;

-- 5. Monthly sales trends
SELECT month, SUM(sales) AS revenue, SUM(profit) AS profit
FROM retail_transactions GROUP BY month ORDER BY month;

-- 6. Year-over-year sales comparison
SELECT year, SUM(sales) AS revenue,
       LAG(SUM(sales)) OVER (ORDER BY year) AS prior_year_revenue,
       ROUND(100 * (SUM(sales) - LAG(SUM(sales)) OVER (ORDER BY year))
             / NULLIF(LAG(SUM(sales)) OVER (ORDER BY year), 0), 2) AS yoy_growth_pct
FROM retail_transactions GROUP BY year ORDER BY year;

-- 13. Month-over-month growth
WITH monthly AS (
    SELECT month, SUM(sales) AS revenue
    FROM retail_transactions GROUP BY month
)
SELECT month, revenue,
       ROUND(100 * (revenue - LAG(revenue) OVER (ORDER BY month))
             / NULLIF(LAG(revenue) OVER (ORDER BY month), 0), 2) AS mom_growth_pct
FROM monthly ORDER BY month;

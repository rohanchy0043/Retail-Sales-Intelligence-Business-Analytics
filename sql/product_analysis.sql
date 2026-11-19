-- 7. Top 10 products by sales
SELECT product_name, SUM(sales) AS revenue
FROM retail_transactions GROUP BY product_name
ORDER BY revenue DESC LIMIT 10;

-- 8. Bottom 10 products by profit
SELECT product_name, SUM(profit) AS profit
FROM retail_transactions GROUP BY product_name
ORDER BY profit ASC LIMIT 10;

-- 10. Category-wise profitability
SELECT category, SUM(sales) AS revenue, SUM(profit) AS profit,
       ROUND(100 * SUM(profit) / NULLIF(SUM(sales), 0), 2) AS profit_margin_pct
FROM retail_transactions GROUP BY category ORDER BY profit DESC;

-- 14. Ranked products by sales
SELECT product_name, revenue,
       RANK() OVER (ORDER BY revenue DESC) AS sales_rank
FROM (
    SELECT product_name, SUM(sales) AS revenue
    FROM retail_transactions GROUP BY product_name
) ranked;

-- 15. Sales contribution percentage
WITH product_sales AS (
    SELECT product_name, SUM(sales) AS revenue
    FROM retail_transactions GROUP BY product_name
)
SELECT product_name, revenue,
       ROUND(100 * revenue / NULLIF(SUM(revenue) OVER (), 0), 2) AS contribution_pct
FROM product_sales ORDER BY contribution_pct DESC;

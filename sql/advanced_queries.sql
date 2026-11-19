-- Running total of sales
WITH monthly AS (
    SELECT month, SUM(sales) AS revenue
    FROM retail_transactions GROUP BY month
)
SELECT month, revenue,
       SUM(revenue) OVER (ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_revenue
FROM monthly ORDER BY month;

-- Discount bands and profit
SELECT CASE
           WHEN discount = 0 THEN '0%'
           WHEN discount <= 0.1 THEN '1-10%'
           WHEN discount <= 0.2 THEN '11-20%'
           WHEN discount <= 0.3 THEN '21-30%'
           WHEN discount <= 0.5 THEN '31-50%'
           ELSE '>50%'
       END AS discount_band,
       SUM(sales) AS revenue,
       SUM(profit) AS profit,
       ROUND(100 * SUM(profit) / NULLIF(SUM(sales), 0), 2) AS profit_margin_pct
FROM retail_transactions
GROUP BY 1 ORDER BY 1;

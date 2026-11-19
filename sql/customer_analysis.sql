-- 11. Customer segment analysis
SELECT segment, COUNT(DISTINCT customer_id) AS customers,
       COUNT(DISTINCT order_id) AS orders, SUM(sales) AS revenue,
       ROUND(SUM(sales) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS average_order_value
FROM retail_transactions GROUP BY segment ORDER BY revenue DESC;

-- Region-wise revenue
SELECT region, SUM(sales) AS revenue, SUM(profit) AS profit
FROM retail_transactions GROUP BY region ORDER BY revenue DESC;

-- Shipping mode and profitability
SELECT ship_mode, COUNT(DISTINCT order_id) AS orders,
       ROUND(AVG(delivery_days), 2) AS average_delivery_days,
       SUM(sales) AS revenue, SUM(profit) AS profit
FROM retail_transactions GROUP BY ship_mode ORDER BY revenue DESC;

-- Repeat customer analysis
WITH customer_orders AS (
    SELECT customer_id, COUNT(DISTINCT order_id) AS order_count
    FROM retail_transactions GROUP BY customer_id
)
SELECT COUNT(*) FILTER (WHERE order_count > 1) AS repeat_customers,
       COUNT(*) AS total_customers
FROM customer_orders;

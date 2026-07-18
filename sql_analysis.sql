-- ============================================================
-- UrbanCart E-Commerce Analysis — SQL Queries
-- Database: data_clean/urbancart.db (SQLite)
-- Run with: sqlite3 data_clean/urbancart.db < sql_analysis.sql
-- ============================================================

-- 1. MONTHLY REVENUE TREND
-- Business question: How is revenue trending month over month, and where
-- are the seasonal peaks (useful for inventory & marketing spend planning)?
SELECT
    strftime('%Y-%m', o.order_date) AS month,
    COUNT(DISTINCT o.order_id)      AS total_orders,
    ROUND(SUM(oi.line_total), 2)    AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY month
ORDER BY month;


-- 2. TOP 10 PRODUCTS BY REVENUE
-- Business question: Which products should we prioritize for restocking
-- and promotion?
SELECT
    p.product_name,
    p.category,
    SUM(oi.quantity)             AS units_sold,
    ROUND(SUM(oi.line_total), 2) AS revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
WHERE o.order_status = 'Delivered'
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 10;


-- 3. CATEGORY PERFORMANCE
-- Business question: Which categories drive the most revenue vs. the most
-- orders (i.e. where's the average order value strongest)?
SELECT
    p.category,
    COUNT(DISTINCT o.order_id)                          AS orders,
    SUM(oi.quantity)                                     AS units_sold,
    ROUND(SUM(oi.line_total), 2)                         AS revenue,
    ROUND(SUM(oi.line_total) / COUNT(DISTINCT o.order_id), 2) AS revenue_per_order
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
WHERE o.order_status = 'Delivered'
GROUP BY p.category
ORDER BY revenue DESC;


-- 4. CUSTOMER RFM SEGMENTATION (Recency, Frequency, Monetary)
-- Business question: Who are our highest-value customers, and who is at
-- risk of churning (high monetary/frequency but low recency)?
WITH customer_orders AS (
    SELECT
        o.customer_id,
        MAX(o.order_date)              AS last_order_date,
        COUNT(DISTINCT o.order_id)     AS frequency,
        SUM(oi.line_total)             AS monetary
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'Delivered'
    GROUP BY o.customer_id
),
scored AS (
    SELECT
        customer_id,
        frequency,
        ROUND(monetary, 2) AS monetary,
        CAST(julianday('2025-12-31') - julianday(last_order_date) AS INTEGER) AS recency_days,
        NTILE(4) OVER (ORDER BY julianday(last_order_date) DESC) AS recency_score,
        NTILE(4) OVER (ORDER BY frequency ASC)                   AS frequency_score,
        NTILE(4) OVER (ORDER BY monetary ASC)                    AS monetary_score
    FROM customer_orders
)
SELECT
    c.customer_name,
    s.frequency,
    s.monetary,
    s.recency_days,
    (s.recency_score + s.frequency_score + s.monetary_score) AS rfm_total,
    CASE
        WHEN s.recency_score >= 3 AND s.frequency_score >= 3 AND s.monetary_score >= 3 THEN 'Champion'
        WHEN s.recency_score <= 2 AND s.frequency_score >= 3 AND s.monetary_score >= 3 THEN 'At Risk (high value)'
        WHEN s.recency_score >= 3 AND s.frequency_score <= 2 THEN 'New / Occasional'
        ELSE 'Low Engagement'
    END AS customer_segment
FROM scored s
JOIN customers c ON c.customer_id = s.customer_id
ORDER BY rfm_total DESC
LIMIT 20;


-- 5. REPEAT PURCHASE RATE
-- Business question: What share of customers come back for a second order?
SELECT
    COUNT(DISTINCT CASE WHEN order_count > 1 THEN customer_id END) * 100.0
        / COUNT(DISTINCT customer_id) AS repeat_customer_pct
FROM (
    SELECT customer_id, COUNT(DISTINCT order_id) AS order_count
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
);


-- 6. PAYMENT METHOD MIX
-- Business question: Which payment methods should we prioritize for
-- checkout UX and any transaction-fee negotiations?
SELECT
    payment_method,
    COUNT(*)                                              AS orders,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1)    AS pct_of_orders
FROM orders
WHERE order_status = 'Delivered'
GROUP BY payment_method
ORDER BY orders DESC;


-- 7. TOP CITIES BY REVENUE
-- Business question: Where should regional warehousing / same-day delivery
-- expansion be prioritized?
SELECT
    c.city,
    c.state,
    COUNT(DISTINCT o.order_id)   AS orders,
    ROUND(SUM(oi.line_total), 2) AS revenue
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered' AND c.city != 'Unknown'
GROUP BY c.city, c.state
ORDER BY revenue DESC
LIMIT 10;


-- 8. CANCELLATION / RETURN RATE BY CATEGORY
-- Business question: Which categories have quality or expectation-mismatch
-- issues worth investigating?
SELECT
    p.category,
    COUNT(DISTINCT o.order_id)                                            AS total_orders,
    COUNT(DISTINCT CASE WHEN o.order_status IN ('Cancelled','Returned') THEN o.order_id END) AS cancelled_or_returned,
    ROUND(COUNT(DISTINCT CASE WHEN o.order_status IN ('Cancelled','Returned') THEN o.order_id END) * 100.0
          / COUNT(DISTINCT o.order_id), 1) AS pct_cancelled_or_returned
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
GROUP BY p.category
ORDER BY pct_cancelled_or_returned DESC;


-- 9. GROSS PROFIT MARGIN BY CATEGORY
-- Business question: Revenue tells you what sold, not what made money.
-- Which categories actually drive profit, not just top-line sales?
SELECT
    p.category,
    ROUND(SUM(oi.line_total), 2) AS revenue,
    ROUND(SUM(oi.quantity * p.cost_price), 2) AS total_cost,
    ROUND(SUM(oi.line_total) - SUM(oi.quantity * p.cost_price), 2) AS gross_profit,
    ROUND((SUM(oi.line_total) - SUM(oi.quantity * p.cost_price)) * 100.0 / SUM(oi.line_total), 1) AS margin_pct
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
WHERE o.order_status = 'Delivered'
GROUP BY p.category
ORDER BY gross_profit DESC;


-- 10. MONTHLY ROAS (Return on Ad Spend)
-- Business question: Is marketing spend actually paying for itself month to month?
WITH monthly_revenue AS (
    SELECT strftime('%Y-%m', o.order_date) AS month, SUM(oi.line_total) AS revenue
    FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'Delivered'
    GROUP BY month
),
monthly_spend AS (
    SELECT month, SUM(spend) AS total_spend FROM marketing_spend GROUP BY month
)
SELECT r.month, r.revenue, s.total_spend, ROUND(r.revenue / s.total_spend, 2) AS roas
FROM monthly_revenue r
JOIN monthly_spend s ON s.month = r.month
ORDER BY r.month;


-- 11. CUSTOMER ACQUISITION COST (CAC) BY CHANNEL
-- Business question: Which paid channels are efficiently acquiring customers,
-- and which are burning budget for too few signups?
WITH new_customers AS (
    SELECT acquisition_channel, strftime('%Y-%m', signup_date) AS month, COUNT(*) AS new_custs
    FROM customers
    GROUP BY acquisition_channel, month
),
spend_map AS (
    SELECT channel AS acquisition_channel, month, spend FROM marketing_spend
)
SELECT
    nc.acquisition_channel,
    SUM(nc.new_custs)                          AS total_new_customers,
    ROUND(SUM(sm.spend), 2)                    AS total_spend,
    ROUND(SUM(sm.spend) / SUM(nc.new_custs), 2) AS cac
FROM new_customers nc
JOIN spend_map sm ON sm.acquisition_channel = nc.acquisition_channel AND sm.month = nc.month
GROUP BY nc.acquisition_channel
ORDER BY cac;


-- 12. CUSTOMER LIFETIME VALUE (LTV) BY ACQUISITION CHANNEL
-- Business question: Which acquisition channel brings in customers who
-- spend the most over their lifetime — i.e. where should budget shift toward?
SELECT
    c.acquisition_channel,
    COUNT(DISTINCT c.customer_id)                              AS customers,
    ROUND(SUM(oi.line_total), 2)                                AS total_revenue,
    ROUND(SUM(oi.line_total) / COUNT(DISTINCT c.customer_id), 2) AS avg_ltv
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY c.acquisition_channel
ORDER BY avg_ltv DESC;

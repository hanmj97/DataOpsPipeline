-- 원본 복제 테이블
SELECT *
FROM public.etl_orders
WHERE order_id = 1012;

-- DW Fact 테이블
SELECT *
FROM dw.fact_orders
WHERE order_id = 1012;

-- 고객별 Data Mart
SELECT *
FROM mart.customer_summary
WHERE customer_name = 'E2E통합테스트';


-- 데이터 계층별 주문 건수와 금액 비교
SELECT
    'PUBLIC' AS data_layer,
    COUNT(*) AS total_orders,
    SUM(amount) AS total_amount
FROM public.etl_orders

UNION ALL

SELECT
    'DW',
    COUNT(*),
    SUM(amount)
FROM dw.fact_orders

UNION ALL

SELECT
    'MART_ORDER',
    total_orders,
    total_amount
FROM mart.order_summary

UNION ALL

SELECT
    'MART_CUSTOMER',
    SUM(total_orders),
    SUM(total_amount)
FROM mart.customer_summary;
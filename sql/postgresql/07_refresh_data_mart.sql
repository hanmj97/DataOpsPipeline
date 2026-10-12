/*
========================================
STEP 23-3. Data Mart Refresh
========================================

Source : dw.fact_orders
Target : mart.order_summary
         mart.customer_summary

목적:
1. 전체 주문 통계 생성
2. 고객별 주문 통계 생성
3. UPSERT를 통한 집계 갱신
4. 불필요한 중복 행 방지
========================================
*/

-- 적재 작업을 하나의 트랜잭션으로 처리
-- REPEATABLE READ: 두 집계가 동일한 DW 스냅샷을 조회
BEGIN ISOLATION LEVEL REPEATABLE READ;

-- ======================================
-- 1. 전체 주문 통계 집계
-- ======================================

INSERT INTO mart.order_summary AS target (
    summary_id,
    total_orders,
    total_amount,
    avg_amount,
    refreshed_at
)
SELECT
    1,
    COUNT(*),
    COALESCE(SUM(amount), 0),
    COALESCE(ROUND(AVG(amount), 2), 0),
    CURRENT_TIMESTAMP
FROM dw.fact_orders

ON CONFLICT (summary_id)
DO UPDATE SET
    total_orders = EXCLUDED.total_orders,
    total_amount = EXCLUDED.total_amount,
    avg_amount = EXCLUDED.avg_amount,
    refreshed_at = EXCLUDED.refreshed_at;


-- ======================================
-- 2. 고객별 주문 통계 집계
-- ======================================

INSERT INTO mart.customer_summary AS target (
    customer_name,
    total_orders,
    total_amount,
    avg_amount,
    refreshed_at
)
SELECT
    customer_name,
    COUNT(*),
    SUM(amount),
    ROUND(AVG(amount), 2),
    CURRENT_TIMESTAMP
FROM dw.fact_orders
GROUP BY customer_name

ON CONFLICT (customer_name)
DO UPDATE SET
    total_orders = EXCLUDED.total_orders,
    total_amount = EXCLUDED.total_amount,
    avg_amount = EXCLUDED.avg_amount,
    refreshed_at = EXCLUDED.refreshed_at;


-- ======================================
-- 3. 더 이상 원본에 없는 고객 집계 정리
-- ======================================

DELETE FROM mart.customer_summary AS target
WHERE NOT EXISTS (
    SELECT 1
    FROM dw.fact_orders AS src
    WHERE src.customer_name = target.customer_name
);

-- 모든 집계가 성공하면 COMMIT
COMMIT;
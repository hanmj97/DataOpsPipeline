/*
========================================
STEP 26-5. Kubernetes ETL ROLLBACK Test
========================================

목적:
1. 신규 주문 생성
2. Kubernetes ETL 강제 실패
3. PostgreSQL ROLLBACK 검증
4. 정상 재실행 시 주문 반영 확인

Test Order ID : 1013
========================================
*/

-- 1. 기존 주문 ID 중복 여부 확인
IF EXISTS (
    SELECT 1
    FROM dbo.etl_orders
    WHERE order_id = 1013
)
BEGIN
    THROW 50001, 'Order ID 1013 already exists.', 1;
END;

-- 2. 신규 테스트 주문 생성
INSERT INTO dbo.etl_orders (
    order_id,
    customer_name,
    amount
)
VALUES (
    1013,
    N'K8S_ROLLBACK_TEST',
    45000
);

-- 3. 신규 데이터 확인
SELECT
    order_id,
    customer_name,
    amount,
    updated_at
FROM dbo.etl_orders
WHERE order_id = 1013;
GO
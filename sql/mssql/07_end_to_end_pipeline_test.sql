/*
========================================
STEP 24-6. End-to-End Pipeline Test
========================================

목적:
MSSQL → PostgreSQL → DW → Data Mart
전체 데이터 흐름 검증

테스트 주문 ID: 1012
========================================
*/

-- 1. 신규 주문 생성
-- 이미 존재하면 중복 삽입하지 않음
IF NOT EXISTS (
    SELECT 1
    FROM dbo.etl_orders
    WHERE order_id = 1012
)
BEGIN
    INSERT INTO dbo.etl_orders (
        order_id,
        customer_name,
        amount
    )
    VALUES (
        1012,
        N'E2E통합테스트',
        125000
    );

    PRINT '신규 주문 생성 완료';
END
ELSE
BEGIN
    PRINT '이미 존재하는 주문입니다.';
END;
GO

-- 2. 신규 주문 확인
SELECT
    order_id,
    customer_name,
    amount,
    updated_at
FROM dbo.etl_orders
WHERE order_id = 1012;
GO

-- 3. 원본 전체 주문 건수 및 금액 확인
SELECT
    COUNT(*) AS total_orders,
    SUM(amount) AS total_amount
FROM dbo.etl_orders;
GO
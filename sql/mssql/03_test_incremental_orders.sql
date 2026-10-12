BEGIN TRAN;

-- 기존 주문 금액 수정
UPDATE dbo.etl_orders
SET
    amount = 30000,
    updated_at = SYSUTCDATETIME()
WHERE order_id = 1001
  AND amount <> 30000;

-- 신규 주문 추가
IF NOT EXISTS (
    SELECT 1
    FROM dbo.etl_orders
    WHERE order_id = 1005
)
BEGIN
    INSERT INTO dbo.etl_orders (
        order_id,
        customer_name,
        amount
    )
    VALUES (
        1005,
        N'정하늘',
        55000
    );
END;

COMMIT;

-- 데이터 확인
SELECT *
FROM dbo.etl_orders
ORDER BY order_id;
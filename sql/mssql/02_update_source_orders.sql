BEGIN TRAN;

-- 기존 주문 금액 변경
UPDATE dbo.etl_orders
SET
    amount = 20000,
    updated_at = SYSUTCDATETIME()
WHERE order_id = 1001;

-- 신규 주문 추가
IF NOT EXISTS (
    SELECT 1
    FROM dbo.etl_orders
    WHERE order_id = 1004
)
BEGIN
    INSERT INTO dbo.etl_orders (
        order_id,
        customer_name,
        amount
    )
    VALUES (
        1004,
        N'최유진',
        45000
    );
END;

COMMIT;

SELECT *
FROM dbo.etl_orders
ORDER BY order_id;
IF OBJECT_ID('dbo.etl_orders', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.etl_orders (
        order_id INT PRIMARY KEY,
        customer_name NVARCHAR(50) NOT NULL,
        amount DECIMAL(12,2) NOT NULL,
        updated_at DATETIME2(3) NOT NULL
            DEFAULT SYSUTCDATETIME()
    );
END;
GO

INSERT INTO dbo.etl_orders
    (order_id, customer_name, amount)
SELECT
    src.order_id,
    src.customer_name,
    src.amount
FROM (
    VALUES
        (1001, N'김민수', 15000.00),
        (1002, N'이서연', 25000.00),
        (1003, N'박지훈', 35000.00)
) AS src(order_id, customer_name, amount)
WHERE NOT EXISTS (
    SELECT 1
    FROM dbo.etl_orders AS t
    WHERE t.order_id = src.order_id
);

SELECT *
FROM dbo.etl_orders
ORDER BY order_id;
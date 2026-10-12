/*
    STEP 22. Airflow 자동 재시도 및 장애 복구 테스트

    목적
    1. MSSQL에 신규 주문 생성
    2. Airflow에서 강제 장애 발생
    3. PostgreSQL ROLLBACK 확인
    4. Airflow 자동 재시도 후 정상 적재 검증
*/

-- 테스트용 주문 INSERT
IF NOT EXISTS (
    SELECT 1
    FROM dbo.etl_orders
    WHERE order_id = 1011
)
BEGIN
    INSERT INTO dbo.etl_orders (
        order_id,
        customer_name,
        amount
    )
    VALUES (
        1011,
        N'Airflow재시도테스트',
        115000
    );
END;

-- 원본 데이터 확인
SELECT *
FROM dbo.etl_orders
WHERE order_id = 1011;
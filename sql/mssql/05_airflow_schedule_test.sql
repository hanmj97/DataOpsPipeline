
/*
====================================================
STEP 21. Airflow Scheduled ETL Test
====================================================

목적:
1. MSSQL에 신규 주문 데이터 생성
2. Airflow Cron 스케줄링 동작 확인
3. 사용자 개입 없이 ETL 자동 실행
4. PostgreSQL 적재 및 Watermark 갱신 확인

Airflow DAG : dataops_incremental_etl
실행 주기   : */5 * * * * (5분 간격)
원본 DB     : Dataops_mssql
대상 DB     : PostgreSQL / dataops
====================================================
*/

-- 1. 기존 주문 존재 여부 확인
IF NOT EXISTS (
    SELECT 1
    FROM dbo.etl_orders
    WHERE order_id = 1010
)
BEGIN
    -- 2. 자동 스케줄링 테스트용 신규 주문 생성
    INSERT INTO dbo.etl_orders (
        order_id,
        customer_name,
        amount
    )
    VALUES (
        1010,
        N'자동스케줄테스트',
        105000
    );
END;
GO

-- 3. 신규 생성된 주문 조회
SELECT
    order_id,
    customer_name,
    amount,
    updated_at
FROM dbo.etl_orders
WHERE order_id = 1010;
GO

-- 4. MSSQL 원본 데이터 건수 및 금액 합계 확인
SELECT
    COUNT(*) AS total_count,
    SUM(amount) AS total_amount
FROM dbo.etl_orders;
GO

/*
[Airflow 자동 실행 검증 절차]

1. dataops_incremental_etl DAG 활성화

2. DAG 스케줄 설정 확인
   schedule="*/5 * * * *"

3. Airflow Trigger 버튼을 누르지 않고 대기

4. Airflow Scheduler가 DAG 자동 실행

5. DAG Run ID 확인
   scheduled__... 형태인지 확인

6. Task 로그 확인
   Extract → Transform → Load → Validate

7. PostgreSQL에서 order_id = 1010 조회

8. Watermark 갱신 여부 확인

[기대 결과]
- 신규 주문 자동 추출
- PostgreSQL에 데이터 적재
- Airflow Task Success
- Watermark 정상 갱신
*/
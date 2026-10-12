/*
====================================================
STEP 20. Airflow Manual ETL Test
====================================================

목적:
1. MSSQL 원본 데이터에 신규 주문 생성
2. Airflow에서 dataops_incremental_etl DAG 수동 실행
3. PostgreSQL에 신규 데이터 적재 확인
4. Watermark 갱신 및 데이터 정합성 검증

원본 DB : Dataops_mssql
원본 테이블 : dbo.etl_orders
대상 DB : PostgreSQL / dataops
대상 테이블 : public.etl_orders
====================================================
*/

-- 1. 중복 데이터 방지를 위한 존재 여부 확인
IF NOT EXISTS (
    SELECT 1
    FROM dbo.etl_orders
    WHERE order_id = 1009
)
BEGIN
    -- 2. Airflow 수동 실행 테스트용 신규 주문 생성
    INSERT INTO dbo.etl_orders (
        order_id,
        customer_name,
        amount
    )
    VALUES (
        1009,
        N'Airflow테스트',
        95000
    );
END;
GO

-- 3. 생성된 원본 주문 데이터 확인
SELECT
    order_id,
    customer_name,
    amount,
    updated_at
FROM dbo.etl_orders
WHERE order_id = 1009;
GO

-- 4. 전체 주문 건수 및 금액 합계 확인
SELECT
    COUNT(*) AS total_count,
    SUM(amount) AS total_amount
FROM dbo.etl_orders;
GO

/*
[Airflow 실행 절차]

1. Airflow Web UI 접속
   http://localhost:8080

2. DAG 선택
   dataops_incremental_etl

3. Trigger 버튼을 눌러 수동 실행

4. run_incremental_etl Task 로그 확인

5. PostgreSQL에서 order_id = 1009 적재 여부 검증

[기대 결과]
- MSSQL 신규 주문 생성
- Airflow Task 실행 성공
- PostgreSQL 신규 주문 적재
- Watermark 최신 처리 시각 반영
*/

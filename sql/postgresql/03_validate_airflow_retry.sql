/*
    STEP 22. Airflow 장애 복구 검증

    1차 실행 실패 후
    - 신규 주문이 적재되지 않았는지 확인
    - Watermark가 변경되지 않았는지 확인

    2차 실행 성공 후
    - 신규 주문 적재 확인
    - Watermark 갱신 확인
*/

-- 신규 주문 적재 여부
SELECT *
FROM public.etl_orders
WHERE order_id = 1011;

-- ETL 마지막 처리 시각
SELECT
    pipeline_name,
    last_updated_at
FROM public.etl_watermarks;

-- 전체 주문 데이터 건수 및 금액
SELECT
    COUNT(*) AS total_count,
    SUM(amount) AS total_amount
FROM public.etl_orders;
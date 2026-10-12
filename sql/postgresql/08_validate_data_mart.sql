/*
========================================
STEP 24. Automated Data Validation
========================================

Database : dataops

목적:
1. public 원본 복제 데이터와 DW 비교
2. DW와 전체 주문 마트 비교
3. DW와 고객별 마트 비교
4. 불일치 발생 시 예외 발생

Airflow에서 자동 실행할 검증 SQL
========================================
*/

DO $$
BEGIN

    -- 1. public.etl_orders 와 dw.fact_orders 비교
    -- 누락된 주문 또는 서로 다른 값이 있는지 확인
    IF EXISTS (
        SELECT 1
        FROM public.etl_orders AS src
        FULL OUTER JOIN dw.fact_orders AS dw
            ON src.order_id = dw.order_id
        WHERE src.order_id IS NULL
           OR dw.order_id IS NULL
           OR (
               src.customer_name,
               src.amount,
               src.updated_at
           ) IS DISTINCT FROM (
               dw.customer_name,
               dw.amount,
               dw.updated_at
           )
    ) THEN
        RAISE EXCEPTION
            'Source와 DW 데이터 불일치';
    END IF;

    -- 2. 전체 주문 데이터 마트 검증
    -- 건수, 금액 합계, 평균 금액 비교
    IF NOT EXISTS (
        SELECT 1
        FROM mart.order_summary AS m
        CROSS JOIN (
            SELECT
                COUNT(*) AS total_orders,
                COALESCE(SUM(amount), 0) AS total_amount,
                COALESCE(ROUND(AVG(amount), 2), 0)
                    AS avg_amount
            FROM dw.fact_orders
        ) AS d
        WHERE m.summary_id = 1
          AND (
              m.total_orders,
              m.total_amount,
              m.avg_amount
          ) IS NOT DISTINCT FROM (
              d.total_orders,
              d.total_amount,
              d.avg_amount
          )
    ) THEN
        RAISE EXCEPTION
            'DW와 Order Mart 집계 불일치';
    END IF;

    -- 3. 고객별 데이터 마트 검증
    -- 고객 누락, 불필요한 고객, 집계값 오류 확인
    IF EXISTS (
        WITH expected AS (
            SELECT
                customer_name,
                COUNT(*) AS total_orders,
                SUM(amount) AS total_amount,
                ROUND(AVG(amount), 2) AS avg_amount
            FROM dw.fact_orders
            GROUP BY customer_name
        )
        SELECT 1
        FROM expected AS e
        FULL OUTER JOIN mart.customer_summary AS m
            ON e.customer_name = m.customer_name
        WHERE e.customer_name IS NULL
           OR m.customer_name IS NULL
           OR (
               e.total_orders,
               e.total_amount,
               e.avg_amount
           ) IS DISTINCT FROM (
               m.total_orders,
               m.total_amount,
               m.avg_amount
           )
    ) THEN
        RAISE EXCEPTION
            'DW와 Customer Mart 집계 불일치';
    END IF;

    -- 4. 모든 검증 성공
    RAISE NOTICE 'Data Validation Success!';

END $$;

-- 검증 결과 확인용 조회
SELECT
    COUNT(*) AS total_orders,
    COALESCE(SUM(amount), 0) AS total_amount
FROM dw.fact_orders;
/*
========================================
STEP 23-2. DW Fact Orders Load
========================================

Source : public.etl_orders
Target : dw.fact_orders

목적:
1. 신규 주문 INSERT
2. 기존 주문의 변경 데이터 UPDATE
3. 변경 없는 데이터 UPDATE 방지
4. 원본과 DW 데이터 정합성 검증
========================================
*/

-- 적재 및 검증을 하나의 트랜잭션으로 처리
BEGIN;

-- 1. 원본 데이터를 DW Fact 테이블에 적재
INSERT INTO dw.fact_orders AS target (
    order_id,
    customer_name,
    amount,
    updated_at
)
SELECT
    src.order_id,
    src.customer_name,
    src.amount,
    src.updated_at
FROM public.etl_orders AS src

-- ON CONFLICT 구문과의 구문 해석 모호성 방지
WHERE TRUE

-- 2. 기존 주문이 존재하면 변경된 값만 갱신
ON CONFLICT (order_id)
DO UPDATE SET
    customer_name = EXCLUDED.customer_name,
    amount = EXCLUDED.amount,
    updated_at = EXCLUDED.updated_at,
    dw_loaded_at = CURRENT_TIMESTAMP

-- 3. 실제 데이터가 변경된 경우에만 UPDATE
WHERE (
    target.customer_name,
    target.amount,
    target.updated_at
) IS DISTINCT FROM (
    EXCLUDED.customer_name,
    EXCLUDED.amount,
    EXCLUDED.updated_at
);

-- 4. 원본과 DW 데이터 일치 여부 검증
-- 하나라도 불일치하면 예외 발생
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM public.etl_orders AS src
        FULL OUTER JOIN dw.fact_orders AS target
            ON src.order_id = target.order_id
        WHERE src.order_id IS NULL
           OR target.order_id IS NULL
           OR (
               src.customer_name,
               src.amount,
               src.updated_at
           ) IS DISTINCT FROM (
               target.customer_name,
               target.amount,
               target.updated_at
           )
    ) THEN
        RAISE EXCEPTION
            'DW 데이터 정합성 검증 실패';
    END IF;
END
$$;

-- 5. 검증까지 성공하면 COMMIT
COMMIT;

-- 6. 원본과 DW의 건수 및 금액 비교
SELECT
    'SOURCE' AS data_layer,
    COUNT(*) AS total_count,
    SUM(amount) AS total_amount
FROM public.etl_orders

UNION ALL

SELECT
    'DW' AS data_layer,
    COUNT(*) AS total_count,
    SUM(amount) AS total_amount
FROM dw.fact_orders;
/*
========================================
STEP 23. Data Warehouse 구축
========================================

DBMS : PostgreSQL
Database : dataops

목적
1. 분석용 DW 스키마 생성
2. 데이터 마트 스키마 생성
3. 주문 Fact 테이블 생성
========================================
*/

-- 1. 데이터 웨어하우스 스키마 생성
CREATE SCHEMA IF NOT EXISTS dw;

-- 2. 데이터 마트 스키마 생성
CREATE SCHEMA IF NOT EXISTS mart;

-- 3. 주문 Fact 테이블 생성
-- Grain: 주문 1건당 1행
CREATE TABLE IF NOT EXISTS dw.fact_orders (
    order_id INT PRIMARY KEY,
    customer_name VARCHAR(50) NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    updated_at TIMESTAMP(3) NOT NULL,

    -- DW에 데이터가 적재된 시각
    dw_loaded_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_fact_orders_amount
        CHECK (amount >= 0)
);

-- 4. 테이블 생성 확인
SELECT
    table_schema,
    table_name
FROM information_schema.tables
WHERE table_schema IN ('dw', 'mart')
ORDER BY table_schema, table_name;
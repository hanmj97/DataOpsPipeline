/*
========================================
STEP 23-3. Data Mart Table Creation
========================================

DBMS : PostgreSQL
Database : dataops

목적:
1. 전체 주문 집계 테이블 생성
2. 고객별 주문 집계 테이블 생성
========================================
*/

-- 1. 데이터 마트 스키마 생성
CREATE SCHEMA IF NOT EXISTS mart;

-- 2. 전체 주문 집계 테이블
CREATE TABLE IF NOT EXISTS mart.order_summary (
    summary_id SMALLINT PRIMARY KEY
        CHECK (summary_id = 1),

    total_orders BIGINT NOT NULL,
    total_amount NUMERIC(20,2) NOT NULL,
    avg_amount NUMERIC(20,2) NOT NULL,

    -- 마지막 집계 수행 시각
    refreshed_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);

-- 3. 고객별 주문 집계 테이블
CREATE TABLE IF NOT EXISTS mart.customer_summary (
    customer_name VARCHAR(50) PRIMARY KEY,

    total_orders BIGINT NOT NULL,
    total_amount NUMERIC(20,2) NOT NULL,
    avg_amount NUMERIC(20,2) NOT NULL,

    refreshed_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);

-- 4. 테이블 생성 확인
SELECT
    table_schema,
    table_name
FROM information_schema.tables
WHERE table_schema = 'mart'
ORDER BY table_name;
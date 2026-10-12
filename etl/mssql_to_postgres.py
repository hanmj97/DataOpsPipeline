
import os
from pathlib import Path
from contextlib import closing

import pyodbc
import psycopg
from dotenv import load_dotenv


# 1. 프로젝트 환경 변수 로드
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

pg_password = os.getenv("PG_PASSWORD")

if not pg_password:
    raise RuntimeError("PG_PASSWORD 환경 변수가 없습니다.")


# 2. MSSQL 연결
drivers = pyodbc.drivers()
driver = next(
    (d for d in [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server"
    ] if d in drivers),
    None
)

if not driver:
    raise RuntimeError("SQL Server ODBC Driver가 없습니다.")

mssql_conn_str = (
    f"DRIVER={{{driver}}};"
    "SERVER=localhost;"
    "DATABASE=Dataops_mssql;"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)


# 3. Extract - MSSQL 데이터 추출
with closing(pyodbc.connect(mssql_conn_str)) as conn:
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            order_id,
            customer_name,
            amount,
            updated_at
        FROM dbo.etl_orders
        ORDER BY order_id
    """)

    source_rows = cursor.fetchall()

print(f"[Extract] MSSQL 데이터 {len(source_rows)}건 추출")


# 4. Transform - 데이터 정제
orders = [
    (
        int(row.order_id),
        row.customer_name.strip(),
        row.amount,
        row.updated_at
    )
    for row in source_rows
]

print(f"[Transform] 데이터 {len(orders)}건 변환 완료")


# 5. Load - PostgreSQL 적재
with psycopg.connect(
    host=os.getenv("PG_HOST", "127.0.0.1"),
    port=int(os.getenv("PG_PORT", "5433")),
    dbname=os.getenv("PG_DATABASE", "dataops"),
    user=os.getenv("PG_USER", "hanmj97"),
    password=pg_password
) as pg_conn:

    with pg_conn.cursor() as cursor:
        cursor.executemany("""
            INSERT INTO public.etl_orders (
                order_id,
                customer_name,
                amount,
                updated_at
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (order_id)
            DO UPDATE SET
                customer_name = EXCLUDED.customer_name,
                amount = EXCLUDED.amount,
                updated_at = EXCLUDED.updated_at
        """, orders)

        print(f"[Load] PostgreSQL {len(orders)}건 UPSERT 실행")

        # 6. Validate - 적재 결과 비교
        ids = [row[0] for row in orders]

        cursor.execute("""
            SELECT
                order_id,
                customer_name,
                amount,
                updated_at
            FROM public.etl_orders
            WHERE order_id = ANY(%s)
            ORDER BY order_id
        """, (ids,))

        target_rows = cursor.fetchall()

        if orders != target_rows:
            raise ValueError("원본과 적재 데이터가 일치하지 않습니다.")

        print(f"[Validate] 데이터 {len(target_rows)}건 검증 완료")

print("[Success] ETL 작업 완료!")

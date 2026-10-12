import os
from pathlib import Path
from contextlib import closing

import pyodbc
import psycopg
from dotenv import load_dotenv

import logging
import sys
from logging.handlers import RotatingFileHandler


# 1-1. 환경 변수
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# 1-2. Logging 환경 설정
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("dataops.incremental_etl")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 로그 파일 기록
    file_handler = RotatingFileHandler(
        LOG_DIR / "incremental_etl.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # PowerShell 콘솔 출력
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


PIPELINE_NAME = "mssql_orders_to_postgres"

if not os.getenv("PG_PASSWORD"):
    raise RuntimeError("PG_PASSWORD가 설정되지 않았습니다.")


# 2-1. MSSQL 연결 설정
driver = next(
    (
        d for d in [
            "ODBC Driver 18 for SQL Server",
            "ODBC Driver 17 for SQL Server"
        ]
        if d in pyodbc.drivers()
    ),
    None
)

if not driver:
    raise RuntimeError("SQL Server ODBC 드라이버가 없습니다.")


# 2-2. MSSQL 접속 환경 설정
mssql_auth = os.getenv("MSSQL_AUTH", "windows").lower()
mssql_host = os.getenv("MSSQL_HOST", "localhost")
mssql_port = os.getenv("MSSQL_PORT", "1433")
mssql_database = os.getenv("MSSQL_DATABASE", "Dataops_mssql")

mssql_conn_str = (
    f"DRIVER={{{driver}}};"
    f"SERVER=tcp:{mssql_host},{mssql_port};"
    f"DATABASE={mssql_database};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

if mssql_auth == "sql":
    user = os.getenv("MSSQL_USER")
    password = os.getenv("MSSQL_PASSWORD")

    if not user or not password:
        raise RuntimeError("MSSQL 계정 정보가 없습니다.")

    # ODBC 연결 문자열의 특수문자 처리
    def escape_odbc(value):
        return "{" + value.replace("}", "}}") + "}"

    mssql_conn_str += (
        f"UID={escape_odbc(user)};"
        f"PWD={escape_odbc(password)};"
    )

elif mssql_auth == "windows":
    mssql_conn_str += "Trusted_Connection=yes;"

else:
    raise ValueError("지원하지 않는 MSSQL 인증 방식입니다.")



# 3. Extract: 변경 데이터 조회
def extract_orders(watermark):
    with closing(pyodbc.connect(mssql_conn_str)) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                order_id,
                customer_name,
                amount,
                updated_at
            FROM dbo.etl_orders
            WHERE updated_at >= ?
            ORDER BY updated_at, order_id
        """, watermark)

        rows = cursor.fetchall()
        cursor.close()

    return [
        (
            int(row.order_id),
            row.customer_name.strip(),
            row.amount,
            row.updated_at
        )
        for row in rows
    ]


# 4. PostgreSQL 연결
def run_etl():
    with psycopg.connect(
        host=os.getenv("PG_HOST", "127.0.0.1"),
        port=int(os.getenv("PG_PORT", "5433")),
        dbname=os.getenv("PG_DATABASE", "dataops"),
        user=os.getenv("PG_USER", "hanmj97"),
        password=os.getenv("PG_PASSWORD")
    ) as pg_conn:

        with pg_conn.cursor() as cursor:

            # 5. 마지막 Watermark 조회 및 잠금
            cursor.execute("""
                SELECT last_updated_at
                FROM public.etl_watermarks
                WHERE pipeline_name = %s
                FOR UPDATE
            """, (PIPELINE_NAME,))

            result = cursor.fetchone()

            if result is None:
                raise RuntimeError("Watermark 정보가 없습니다.")

            watermark = result[0]
            logger.info(f"[Watermark] 마지막 처리 시각: {watermark}")

            # 6. 증분 데이터 추출 및 변환
            orders = extract_orders(watermark)
            logger.info(f"[Extract] {len(orders)}건 추출")

            if not orders:
                logger.info("[Success] 처리할 데이터가 없습니다.")
                return

            logger.info(f"[Transform] {len(orders)}건 변환 완료")

            # 7. PostgreSQL UPSERT
            cursor.executemany("""
                INSERT INTO public.etl_orders AS target (
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

                WHERE (
                    target.customer_name,
                    target.amount,
                    target.updated_at
                ) IS DISTINCT FROM (
                    EXCLUDED.customer_name,
                    EXCLUDED.amount,
                    EXCLUDED.updated_at
                )
            """, orders)

            logger.info(f"[Load] {len(orders)}건 UPSERT 처리")
	    
	    # 테스트용 강제 장애 발생
            if os.getenv("ETL_FAIL_AFTER_LOAD") == "1":
                raise RuntimeError(
                    "[TEST ERROR] PostgreSQL 적재 후 강제 장애 발생!"
                )

            # 8. 적재 데이터 검증
            order_ids = [row[0] for row in orders]

            cursor.execute("""
                SELECT
                    order_id,
                    customer_name,
                    amount,
                    updated_at
                FROM public.etl_orders
                WHERE order_id = ANY(%s)
                ORDER BY order_id
            """, (order_ids,))

            target_rows = cursor.fetchall()
            expected = sorted(orders, key=lambda x: x[0])

            if target_rows != expected:
                raise ValueError("데이터 정합성 검증 실패")

            logger.info(f"[Validate] {len(target_rows)}건 검증 완료")

            # 9. Watermark 갱신
            new_watermark = max(row[3] for row in orders)

            cursor.execute("""
                UPDATE public.etl_watermarks
                SET last_updated_at =
                    GREATEST(last_updated_at, %s)
                WHERE pipeline_name = %s
            """, (new_watermark, PIPELINE_NAME))

            logger.info(f"[Watermark] 갱신 시각: {new_watermark}")

    # PostgreSQL 트랜잭션 정상 종료 시 COMMIT
    logger.info("[Success] 증분 ETL 완료!")


if __name__ == "__main__":
    try:
        logger.info("========== ETL 실행 시작 ==========")

        run_etl()

        logger.info("========== ETL 정상 종료 ==========")

    except Exception:
        logger.exception("ETL 실행 중 오류 발생")
        sys.exit(1)


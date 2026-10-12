import os
import sys
import logging
import argparse
from pathlib import Path

import psycopg


# 1. Logging 설정
# 콘솔에 실행 시각, 로그 등급, 메시지 출력
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger("dataops.sql_runner")


# 2. Airflow Worker에 마운트된 SQL 파일 위치
SQL_DIR = Path("/opt/airflow/dataops/sql/postgresql")

# 실행을 허용할 SQL 파일 목록
ALLOWED_FILES = [
    "05_load_dw_fact_orders.sql",
    "07_refresh_data_mart.sql",
    "08_validate_data_mart.sql"
]


def run_sql(filename):

    # 3. SQL 파일 존재 여부 확인
    sql_path = SQL_DIR / filename

    if not sql_path.is_file():
        raise FileNotFoundError(
            f"SQL 파일이 없습니다: {sql_path}"
        )

    # 4. SQL 파일 읽기
    # utf-8-sig: UTF-8 BOM이 있어도 정상 처리
    sql_query = sql_path.read_text(
        encoding="utf-8-sig"
    )

    if not sql_query.strip():
        raise ValueError("SQL 파일 내용이 비어 있습니다.")

    logger.info(f"[SQL] 실행 시작: {filename}")

    # 5. PostgreSQL 연결
    # 비밀번호는 컨테이너 환경 변수에서 읽음
    with psycopg.connect(
        host=os.getenv("PG_HOST", "dataops-postgres"),
        port=int(os.getenv("PG_PORT", "5432")),
        dbname=os.getenv("PG_DATABASE", "dataops"),
        user=os.environ["PG_USER"],
        password=os.environ["PG_PASSWORD"],

        # SQL 파일 내 BEGIN / COMMIT 사용
        autocommit=True

    ) as conn:

        with conn.cursor() as cursor:

            # 6. SQL 파일 전체 실행
            # 매개변수 없는 다중 SQL문 실행
            # prepare=False: Prepared Statement 비활성화
            cursor.execute(sql_query, prepare=False)

    # 7. 전체 SQL 실행 성공
    logger.info(f"[SQL] 실행 성공: {filename}")


if __name__ == "__main__":

    # 8. 실행할 SQL 파일명을 명령행 인자로 받음
    parser = argparse.ArgumentParser(
        description="DataOps PostgreSQL SQL Runner"
    )

    parser.add_argument(
        "filename",
        choices=ALLOWED_FILES,
        help="실행할 SQL 파일 이름"
    )

    args = parser.parse_args()

    try:
        run_sql(args.filename)

    except Exception:
        # 실패 원인과 Traceback 기록
        logger.exception("[SQL] 실행 실패")

        # Airflow에서 실패를 감지하도록 종료 코드 1 반환
        sys.exit(1)
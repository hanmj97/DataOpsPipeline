import os
import sys
import logging
import subprocess
from datetime import timedelta
from pathlib import Path

import pendulum
from airflow.sdk import dag, task


# Airflow Task 로그 설정
logger = logging.getLogger("airflow.task")

# Worker에 연결된 Python 및 SQL Runner 경로
ETL_DIR = Path("/opt/airflow/dataops/etl")

INCREMENTAL_ETL = ETL_DIR / "mssql_to_postgres_incremental.py"
SQL_RUNNER = ETL_DIR / "run_postgres_sql.py"


# 공통 Python 실행 함수
def execute_python(script_path, *args):

    # Worker의 실행 환경 변수 복사
    env = os.environ.copy()

    # 이전 장애 테스트 옵션 제거
    env.pop("ETL_FAIL_AFTER_LOAD", None)

    # 읽기 전용 마운트에 Python 캐시 파일 생성 방지
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    command = [
        sys.executable,
        str(script_path),
        *args
    ]

    logger.info("작업 실행: %s", script_path.name)

    # 별도 Python 프로세스로 실행
    with subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env
    ) as process:

        # 실행 결과를 Airflow Task 로그에 기록
        for line in process.stdout:
            logger.info("%s", line.rstrip())

        return_code = process.wait()

    # 실패 시 Airflow가 감지하도록 예외 발생
    if return_code != 0:
        raise RuntimeError(
            f"{script_path.name} 실행 실패: {return_code}"
        )

    logger.info("작업 정상 완료: %s", script_path.name)


# End-to-End DAG 정의
@dag(
    dag_id="dataops_end_to_end_pipeline",
    description="MSSQL to PostgreSQL DW and Data Mart Pipeline",

    # 첫 실습에서는 수동 실행
    schedule=None,

    start_date=pendulum.datetime(
        2026, 10, 1, tz="Asia/Seoul"
    ),

    catchup=False,
    max_active_runs=1,

    tags=["dataops", "etl", "dw", "mart"]
)
def dataops_end_to_end_pipeline():

    # STEP 1. MSSQL → PostgreSQL 증분 적재
    @task(
        retries=1,
        retry_delay=timedelta(minutes=1)
    )
    def incremental_etl():
        execute_python(INCREMENTAL_ETL)

    # STEP 2. DW Fact Orders 적재
    @task(
        retries=1,
        retry_delay=timedelta(minutes=1)
    )
    def load_dw():
        execute_python(
            SQL_RUNNER,
            "05_load_dw_fact_orders.sql"
        )

    # STEP 3. 데이터 마트 갱신
    @task(
        retries=1,
        retry_delay=timedelta(minutes=1)
    )
    def refresh_mart():
        execute_python(
            SQL_RUNNER,
            "07_refresh_data_mart.sql"
        )

    # STEP 4. 전체 데이터 정합성 검증
    @task(
        retries=1,
        retry_delay=timedelta(minutes=1)
    )
    def validate():
        execute_python(
            SQL_RUNNER,
            "08_validate_data_mart.sql"
        )

    # DAG 작업 등록
    t1 = incremental_etl()
    t2 = load_dw()
    t3 = refresh_mart()
    t4 = validate()

    # 실행 순서 정의
    t1 >> t2 >> t3 >> t4


# DAG 등록
dataops_end_to_end_pipeline()
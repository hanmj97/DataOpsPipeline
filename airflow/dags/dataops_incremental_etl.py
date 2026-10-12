import logging
import subprocess
import sys
from datetime import timedelta

import pendulum
from airflow.sdk import dag, task


# Airflow에서 작업 로그를 기록하기 위한 Logger
logger = logging.getLogger("airflow.task")


# DAG 정의
@dag(
    dag_id="dataops_incremental_etl",
    description="MSSQL to PostgreSQL Incremental ETL",
    schedule="*/5 * * * *",
    start_date=pendulum.datetime(
        2026, 10, 1, tz="Asia/Seoul"
    ),
    catchup=False,
    max_active_runs=1,
    tags=["dataops", "etl", "incremental"],
)
def dataops_incremental_etl():

    # 실제 Python 증분 ETL 프로그램 실행
    @task(
        retries=1,
        retry_delay=timedelta(minutes=1),
    )
    def run_incremental_etl():

        # Airflow Worker에 마운트된 ETL 파일 경로
        script_path = (
            "/opt/airflow/dataops/etl/"
            "mssql_to_postgres_incremental.py"
        )

        logger.info("DataOps 증분 ETL 실행 시작")

        # 별도의 Python 프로세스로 기존 ETL 실행
        # sys.executable : 현재 Airflow Python 실행 파일
        # stderr=STDOUT : 오류 출력도 함께 수집
        # text=True : 출력을 문자열로 읽음
        with subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        ) as process:

            # ETL 실행 로그를 Airflow 작업 로그에 기록
            for line in process.stdout:
                logger.info(line.rstrip())

            # ETL 프로세스 종료까지 대기
            return_code = process.wait()

        # 종료 코드가 0이 아니면 Airflow 작업 실패 처리
        if return_code != 0:
            raise RuntimeError(
                f"증분 ETL 실패: exit code {return_code}"
            )

        logger.info("DataOps 증분 ETL 정상 종료")

    # DAG에 작업 등록
    run_incremental_etl()


# Airflow에 DAG 등록
dataops_incremental_etl()

import os
import sys
import logging
import subprocess
from datetime import timedelta

import pendulum
from airflow.sdk import dag, task, get_current_context


logger = logging.getLogger("airflow.task")


# 자동 재시도 실습용 DAG
@dag(
    dag_id="dataops_etl_retry_lab",
    description="ETL Failure and Automatic Retry Test",
    schedule=None,
    start_date=pendulum.datetime(
        2026, 10, 1, tz="Asia/Seoul"
    ),
    catchup=False,
    max_active_runs=1,
    tags=["dataops", "retry", "practice"],
)
def dataops_etl_retry_lab():

    @task(
        retries=1,
        retry_delay=timedelta(minutes=2),
    )
    def run_etl_retry_lab():

        # Airflow에서 현재 실행 정보를 가져옴
        context = get_current_context()

        # 현재 Task가 몇 번째 시도인지 확인
        attempt = context["ti"].try_number

        logger.info(f"ETL 실행 시도: {attempt}")

        # 기존 ETL 프로그램 위치
        script_path = (
            "/opt/airflow/dataops/etl/"
            "mssql_to_postgres_incremental.py"
        )

        # 현재 컨테이너 환경 변수 복사
        env = os.environ.copy()

        # 이전 장애 테스트 환경 변수 제거
        env.pop("ETL_FAIL_AFTER_LOAD", None)

        if attempt == 1:
            # 첫 번째 시도에서만 강제 오류 발생
            env["ETL_FAIL_AFTER_LOAD"] = "1"
            logger.warning("1차 시도: 강제 장애 테스트")

        else:
            # 두 번째 시도에서는 정상 ETL 실행
            logger.info("재시도: 정상 복구 시작")

        # 기존 증분 ETL 프로그램 실행
        with subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        ) as process:

            # ETL 로그를 Airflow 로그에 기록
            for line in process.stdout:
                logger.info(line.rstrip())

            return_code = process.wait()

        # 비정상 종료 시 Airflow에 오류 전달
        if return_code != 0:
            raise RuntimeError(
                f"ETL 실패 (종료 코드: {return_code})"
            )

        logger.info("ETL 정상 복구 완료")

    run_etl_retry_lab()


dataops_etl_retry_lab()
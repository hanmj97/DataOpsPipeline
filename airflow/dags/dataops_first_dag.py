import pendulum

from airflow.sdk import dag, task


# DAG 정의
# schedule=None : 자동 스케줄 없이 수동 실행
# catchup=False : 과거 실행 구간 자동 생성 방지
@dag(
    dag_id="dataops_first_dag",
    schedule=None,
    start_date=pendulum.datetime(
        2026, 10, 1, tz="Asia/Seoul"
    ),
    catchup=False,
    tags=["dataops", "practice"],
)
def dataops_first_dag():

    # 1. Extract: 실습용 주문 데이터 생성
    @task
    def extract():
        orders = [
            {"order_id": 1001, "amount": 15000},
            {"order_id": 1002, "amount": 25000},
            {"order_id": 1003, "amount": 35000},
        ]

        print(f"주문 {len(orders)}건 추출")
        return orders

    # 2. Transform: 주문 건수 및 금액 합계 계산
    @task
    def transform(orders):
        result = {
            "count": len(orders),
            "total_amount": sum(
                order["amount"] for order in orders
            ),
        }

        print(f"변환 결과: {result}")
        return result

    # 3. Validate: 처리 결과 정합성 검증
    @task
    def validate(result):
        assert result["count"] == 3
        assert result["total_amount"] == 75000

        print("데이터 정합성 검증 성공!")

    # 작업 실행 순서 정의
    validate(transform(extract()))


# Airflow에 DAG 등록
dataops_first_dag()

\# DataOps Pipeline



Docker, Apache Airflow, Python, MSSQL, PostgreSQL을 활용한

End-to-End 데이터 파이프라인 구축 프로젝트입니다.





\## 1. Project Overview



MSSQL 운영 데이터를 PostgreSQL로 증분 적재하고,

Data Warehouse(DW)와 Data Mart를 구성하여

데이터 처리 및 분석 과정을 자동화하는 개인 프로젝트입니다.



단순 데이터 이관뿐 아니라 데이터 정합성,

트랜잭션 관리, 장애 복구, 자동 재시도 등

안정적인 데이터 파이프라인 운영을 목표로 합니다.





\## 2. Tech Stack



| Category | Technology |

|---|---|

| Source Database | Microsoft SQL Server |

| Target Database | PostgreSQL 17 |

| ETL | Python, pyodbc, psycopg |

| Orchestration | Apache Airflow 3.3.2 |

| Container | Docker, Docker Compose |

| Database Tool | SSMS, DBeaver |

| Environment | Windows 11, WSL2, Linux |





\## 3. Architecture



MSSQL (Dataops\_mssql)

&#x20;       |

&#x20;       v

Apache Airflow + Python Incremental ETL

&#x20;       |

&#x20;       v

PostgreSQL (dataops)

&#x20;       |

&#x20;       v

public.etl\_orders

&#x20;       |

&#x20;       v

dw.fact\_orders

&#x20;       |

&#x20;       v

mart.order\_summary

mart.customer\_summary

&#x20;       |

&#x20;       v

Data Validation





\## 4. Key Features



\### Incremental ETL

\- Watermark 기반 변경 데이터 추출

\- PostgreSQL UPSERT 처리

\- 데이터 정합성 검증

\- 중복 실행 시 불필요한 UPDATE 방지



\### Reliability

\- PostgreSQL 트랜잭션 및 ROLLBACK

\- 실패 시 Watermark 유지

\- Python Logging 및 오류 Traceback 기록

\- Airflow 자동 재시도 및 장애 복구



\### Data Warehouse

\- 주문 단위 Fact 테이블 구축

\- 전체 주문 데이터 마트 생성

\- 고객별 주문 집계

\- DW와 Data Mart 데이터 검증



\### Orchestration

\- Airflow DAG 기반 실행 순서 제어

\- Cron 스케줄링

\- 작업별 로그 및 실행 상태 관리

\- End-to-End 파이프라인 자동화





\## 5. Airflow DAG



| DAG | Purpose |

|---|---|

| dataops\_first\_dag | TaskFlow API 실습 |

| dataops\_incremental\_etl | MSSQL 증분 ETL |

| dataops\_etl\_retry\_lab | 장애 및 자동 재시도 테스트 |

| dataops\_end\_to\_end\_pipeline | ETL, DW, Mart, 검증 통합 실행 |



통합 DAG 실행 순서:



incremental\_etl

&#x20;   |

&#x20;   v

load\_dw

&#x20;   |

&#x20;   v

refresh\_mart

&#x20;   |

&#x20;   v

validate





\## 6. Project Structure



DataOpsPipeline/

├── airflow/

│   ├── dags/

│   ├── Dockerfile.worker

│   └── docker-compose.yaml

├── etl/

│   ├── mssql\_to\_postgres\_incremental.py

│   └── run\_postgres\_sql.py

├── sql/

│   ├── mssql/

│   └── postgresql/

├── Dockerfile

├── docker-compose.yaml

├── requirements.txt

└── README.md





\## 7. Execution



로컬 개발 환경을 기준으로 구성했습니다.



사전 준비:

\- Docker Desktop 및 WSL2

\- SQL Server와 테스트 데이터베이스

\- PostgreSQL 및 Airflow 환경 변수

\- Docker 네트워크 및 DB 연결 권한



실행 순서:

1\. 환경 변수 파일 설정

2\. DataOps PostgreSQL 컨테이너 실행

3\. Airflow 컨테이너 실행

4\. Airflow Web UI 접속

5\. dataops\_end\_to\_end\_pipeline DAG 실행

6\. PostgreSQL에서 결과 검증



Airflow Web UI:

http://localhost:8080



참고: 실제 실행에는 로컬 SQL Server 설정과

Docker 네트워크 구성이 추가로 필요합니다.





\## 8. Data Quality



다음 항목을 검증합니다.

\- 원본 복제 데이터와 DW의 주문별 값 일치

\- DW와 주문 집계 마트의 건수 및 금액 일치

\- 고객별 집계 데이터 정합성

\- 오류 발생 시 작업 실패 및 재시도





\## 9. Limitations



\- 현재 증분 추출은 updated\_at 기반으로 구현

\- 늦게 커밋되는 변경의 완전한 추적은 보장하지 않음

\- 원본 DELETE 동기화는 별도 구현 필요

\- 고객별 집계는 실습용 customer\_name 기준

\- 실제 운영에서는 CDC, 고유 고객 ID, 비밀정보 관리 등 개선 필요





\## 10. Future Improvements



\- Kubernetes Job / CronJob 실습

\- 파이프라인 운영 및 모니터링 고도화

\- CDC 기반 변경 데이터 수집 검토

\- 데이터 품질 검증 및 테스트 자동화




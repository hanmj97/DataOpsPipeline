# Python 3.13 + Debian 12
FROM python:3.13-slim-bookworm

# 컨테이너 작업 디렉터리
WORKDIR /app

# MSSQL 연결용 ODBC Driver 18 설치
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates curl gnupg unixodbc libgssapi-krb5-2 \
    && curl -fsSL \
        https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb \
        -o /tmp/packages-microsoft-prod.deb \
    && dpkg -i /tmp/packages-microsoft-prod.deb \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && rm -rf /var/lib/apt/lists/* \
        /tmp/packages-microsoft-prod.deb

# Python 라이브러리 설치
COPY requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

# ETL 소스코드 복사
COPY etl/ ./etl/

# 컨테이너 실행 시 기본 명령어
CMD ["python", "etl/mssql_to_postgres_incremental.py"]

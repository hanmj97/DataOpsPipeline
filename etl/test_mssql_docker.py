import os
from contextlib import closing

import pyodbc


# ODBC 연결 문자열에서 특수문자 처리
def escape_odbc(value):
    return "{" + value.replace("}", "}}") + "}"


# MSSQL 연결 정보
connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=tcp:host.docker.internal,1433;"
    "DATABASE=Dataops_mssql;"
    f"UID={escape_odbc(os.environ['MSSQL_USER'])};"
    f"PWD={escape_odbc(os.environ['MSSQL_PASSWORD'])};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

try:
    with closing(
        pyodbc.connect(connection_string, timeout=5)
    ) as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                SUSER_SNAME() AS LoginName,
                DB_NAME() AS DatabaseName,
                COUNT(*) AS OrderCount
            FROM dbo.etl_orders
        """)

        row = cursor.fetchone()

        print("[Success] Docker MSSQL 연결 성공!")
        print("Login:", row.LoginName)
        print("Database:", row.DatabaseName)
        print("Orders:", row.OrderCount)

        cursor.close()

except pyodbc.Error as e:
    print("[Error] MSSQL 연결 실패")
    print(e)
    raise

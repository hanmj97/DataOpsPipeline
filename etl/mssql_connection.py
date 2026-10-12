import pyodbc

# 설치된 ODBC 드라이버 확인
drivers = pyodbc.drivers()

driver = next(
    (d for d in [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server"
    ] if d in drivers),
    None
)

if driver is None:
    raise RuntimeError("SQL Server ODBC Driver 17 또는 18이 필요합니다.")

# MSSQL 접속 정보
connection_string = (
    f"DRIVER={{{driver}}};"
    "SERVER=localhost;"
    "DATABASE=Dataops_mssql;"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

conn = None

try:
    conn = pyodbc.connect(connection_string, timeout=5)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            @@SERVERNAME AS ServerName,
            DB_NAME() AS DatabaseName,
            SUSER_SNAME() AS LoginName
    """)

    row = cursor.fetchone()

    print("MSSQL 연결 성공!")
    print("서버:", row.ServerName)
    print("데이터베이스:", row.DatabaseName)
    print("로그인:", row.LoginName)

except pyodbc.Error as e:
    print("MSSQL 연결 실패:", e)

finally:
    if conn is not None:
        conn.close()
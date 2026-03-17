import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = oracledb.connect(
        user=os.environ.get("DB_USER", "kim1"),
        password=os.environ.get("DB_PASSWORD", "1"),
        dsn=os.environ.get("DB_DSN", "192.168.0.80:1521/XE")
    )
    cursor = conn.cursor()
    cursor.execute("SELECT ITEM_SEQ, ITEM_NAME FROM REF_DRUG_PERMIT_LIST WHERE ROWNUM <= 5")
    for row in cursor:
        print(row)
    cursor.close()
    conn.close()
    print("Oracle 연결 성공")
except Exception as e:
    print("Oracle 연결 실패:", e)

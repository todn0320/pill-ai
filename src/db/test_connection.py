import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = oracledb.connect(
        user=os.environ.get("DB_USER", "system"),
        password=os.environ.get("DB_PASSWORD", "Asd147258369"),
        dsn=os.environ.get("DB_DSN", "72.155.73.199:1521/xe")
    )
    cursor = conn.cursor()
    #cursor.execute("SELECT ITEM_SEQ, ITEM_NAME FROM REF_DRUG_PERMIT_LIST WHERE ROWNUM <= 5")
    #for row in cursor:
    #    print(row)
    #cursor.close()
    conn.close()
    print("Oracle 연결 성공")
except Exception as e:
    print("Oracle 연결 실패:", e)

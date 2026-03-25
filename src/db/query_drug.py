"""
Oracle DB 쿼리 함수 모음
약 검색 / 상세정보 / DUR 경고 / 낱알 검색 / RAG 청크 / 병용금기 체크
"""
import os
import oracledb
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return oracledb.connect(
        user=os.environ.get("DB_USER", "medi"),
        password=os.environ.get("DB_PASSWORD", "1234"),
        dsn=os.environ.get("DB_DSN", "72.155.73.199:1521/xe")
    )

def row_to_dict(cursor, row):
    """CLOB 포함한 Oracle row를 dict로 변환"""
    result = {}
    for i, col in enumerate(cursor.description):
        val = row[i]
        if val is None:
            result[col[0]] = None
        elif hasattr(val, 'read'):  # CLOB 타입
            try:
                result[col[0]] = val.read()
            except Exception:
                result[col[0]] = None
        else:
            result[col[0]] = val
    return result

def rows_to_list(cursor, rows):
    """여러 row를 dict 리스트로 변환"""
    return [row_to_dict(cursor, row) for row in rows]


# ============================================================
# 약 이름으로 검색
# ============================================================
def search_drug_by_name(name: str, limit: int = 10) -> list:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.ITEM_SEQ, p.ITEM_NAME, p.ENTP_NAME, p.ETC_OTC_CODE,
               o.SUMMARY, pi.DRUG_SHAPE, pi.COLOR_CLASS1, pi.ITEM_IMAGE_URL
        FROM REF_DRUG_PERMIT_LIST p
        LEFT JOIN REF_DRUG_OVERVIEW o ON p.ITEM_SEQ = o.ITEM_SEQ
        LEFT JOIN PILL_IMAGE_FEATURE pi ON p.ITEM_SEQ = pi.ITEM_SEQ
        WHERE UPPER(p.ITEM_NAME) LIKE UPPER(:1)
        AND p.CANCEL_DATE IS NULL
        FETCH FIRST :2 ROWS ONLY
    """, [f"%{name}%", limit])

    rows = cursor.fetchall()
    result = rows_to_list(cursor, rows)
    cursor.close()
    conn.close()
    return result


# ============================================================
# 약 상세정보 조회
# ============================================================
def get_drug_detail(item_seq: str) -> dict:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.ITEM_SEQ, p.ITEM_NAME, p.ENTP_NAME, p.ETC_OTC_CODE, p.ITEM_PERMIT_DATE,
               d.EFCY_QESITM, d.USE_METHOD_QESITM, d.ATPN_WARN_QESITM,
               d.ATPN_QESITM, d.INTRC_QESITM, d.SE_QESITM,
               o.SUMMARY, o.CAUTION, o.STORAGE_METHOD,
               pi.DRUG_SHAPE, pi.COLOR_CLASS1, pi.COLOR_CLASS2,
               pi.PRINT_FRONT, pi.PRINT_BACK, pi.ITEM_IMAGE_URL
        FROM REF_DRUG_PERMIT_LIST p
        LEFT JOIN REF_DRUG_PERMIT_DETAIL d ON p.ITEM_SEQ = d.ITEM_SEQ
        LEFT JOIN REF_DRUG_OVERVIEW o ON p.ITEM_SEQ = o.ITEM_SEQ
        LEFT JOIN PILL_IMAGE_FEATURE pi ON p.ITEM_SEQ = pi.ITEM_SEQ
        WHERE p.ITEM_SEQ = :1
    """, [item_seq])

    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return None

    result = row_to_dict(cursor, row)

    # 성분 목록
    cursor.execute("""
        SELECT INGR_NAME, INGR_ENG_NAME, INGR_AMOUNT, INGR_UNIT
        FROM REF_DRUG_INGREDIENT
        WHERE ITEM_SEQ = :1
    """, [item_seq])

    ingr_rows = cursor.fetchall()
    result['INGREDIENTS'] = [
        {
            "name": r[0],
            "eng_name": r[1],
            "amount": r[2],
            "unit": r[3]
        } for r in ingr_rows
    ]

    cursor.close()
    conn.close()
    return result


# ============================================================
# DUR 병용금기/경고 조회
# ============================================================
def get_dur_warnings(item_seq: str, type_name: str = None) -> list:
    conn = get_connection()
    cursor = conn.cursor()

    if type_name:
        cursor.execute("""
            SELECT WARNING_ID, ITEM_SEQ, TYPE_NAME, PROHBT_CONTENT,
                   MIX_ITEM_SEQ, GRADE, NOTIFICATION_DATE
            FROM REF_DUR_ITEM_WARNING
            WHERE ITEM_SEQ = :1 AND TYPE_NAME = :2
            ORDER BY GRADE, TYPE_NAME
        """, [item_seq, type_name])
    else:
        cursor.execute("""
            SELECT WARNING_ID, ITEM_SEQ, TYPE_NAME, PROHBT_CONTENT,
                   MIX_ITEM_SEQ, GRADE, NOTIFICATION_DATE
            FROM REF_DUR_ITEM_WARNING
            WHERE ITEM_SEQ = :1
            ORDER BY GRADE, TYPE_NAME
        """, [item_seq])

    rows = cursor.fetchall()
    result = rows_to_list(cursor, rows)
    cursor.close()
    conn.close()
    return result


# ============================================================
# 병용금기 체크 (두 약 품목코드로 확인)
# ============================================================
def check_drug_interaction(item_seq_a: str, item_seq_b: str) -> list:
    """두 약의 병용금기 여부 확인 (A→B, B→A 양방향 체크)"""
    conn = get_connection()
    cursor = conn.cursor()

    # A → B 방향 확인
    cursor.execute("""
        SELECT WARNING_ID, ITEM_SEQ, TYPE_NAME, PROHBT_CONTENT,
               MIX_ITEM_SEQ, GRADE
        FROM REF_DUR_ITEM_WARNING
        WHERE ITEM_SEQ = :1
        AND MIX_ITEM_SEQ = :2
        AND TYPE_NAME LIKE '%병용%'
    """, [item_seq_a, item_seq_b])

    rows = cursor.fetchall()
    result = rows_to_list(cursor, rows)

    # B → A 방향도 확인 (역방향)
    if not result:
        cursor.execute("""
            SELECT WARNING_ID, ITEM_SEQ, TYPE_NAME, PROHBT_CONTENT,
                   MIX_ITEM_SEQ, GRADE
            FROM REF_DUR_ITEM_WARNING
            WHERE ITEM_SEQ = :1
            AND MIX_ITEM_SEQ = :2
            AND TYPE_NAME LIKE '%병용%'
        """, [item_seq_b, item_seq_a])

        rows = cursor.fetchall()
        result = rows_to_list(cursor, rows)

    cursor.close()
    conn.close()
    return result


# ============================================================
# 낱알 모양/색상/각인으로 검색
# ============================================================
def search_pill_by_shape(
    shape: str = None,
    color: str = None,
    print_text: str = None,
    limit: int = 20
) -> list:
    conn = get_connection()
    cursor = conn.cursor()

    conditions = ["p.CANCEL_DATE IS NULL"]
    params = []

    if shape:
        conditions.append("pi.DRUG_SHAPE = :shape")
        params.append(shape)
    if color:
        conditions.append("(pi.COLOR_CLASS1 = :color1 OR pi.COLOR_CLASS2 = :color2)")
        params.append(color)
        params.append(color)
    if print_text:
        conditions.append("(UPPER(pi.PRINT_FRONT) LIKE UPPER(:print1) OR UPPER(pi.PRINT_BACK) LIKE UPPER(:print2))")
        params.append(f"%{print_text}%")
        params.append(f"%{print_text}%")

    where = " AND ".join(conditions)

    cursor.execute(f"""
        SELECT p.ITEM_SEQ, p.ITEM_NAME, p.ENTP_NAME,
               pi.DRUG_SHAPE, pi.COLOR_CLASS1, pi.COLOR_CLASS2,
               pi.PRINT_FRONT, pi.PRINT_BACK,
               pi.LENG_LONG, pi.LENG_SHORT, pi.THICK,
               pi.ITEM_IMAGE_URL
        FROM REF_DRUG_PERMIT_LIST p
        JOIN PILL_IMAGE_FEATURE pi ON p.ITEM_SEQ = pi.ITEM_SEQ
        WHERE {where}
        FETCH FIRST :limit ROWS ONLY
    """, params + [limit])

    rows = cursor.fetchall()
    result = rows_to_list(cursor, rows)
    cursor.close()
    conn.close()
    return result


# ============================================================
# RAG 청크 조회
# ============================================================
def get_rag_chunks(item_seq: str, section_type: str = None) -> list:
    conn = get_connection()
    cursor = conn.cursor()

    if section_type:
        cursor.execute("""
            SELECT CHUNK_ID, ITEM_SEQ, SOURCE_TYPE, SECTION_TYPE, CHUNK_TEXT
            FROM RAG_CHUNK
            WHERE ITEM_SEQ = :1 AND SECTION_TYPE = :2
            ORDER BY SOURCE_TYPE, SECTION_TYPE
        """, [item_seq, section_type])
    else:
        cursor.execute("""
            SELECT CHUNK_ID, ITEM_SEQ, SOURCE_TYPE, SECTION_TYPE, CHUNK_TEXT
            FROM RAG_CHUNK
            WHERE ITEM_SEQ = :1
            ORDER BY SOURCE_TYPE, SECTION_TYPE
        """, [item_seq])

    rows = cursor.fetchall()
    result = rows_to_list(cursor, rows)
    cursor.close()
    conn.close()
    return result


# ============================================================
# run_pipeline.py 호환용 래퍼 함수
# ============================================================
def query_drug(topk: list, ocr_result: dict) -> dict:
    """run_pipeline에서 호출하는 함수 - topk 결과로 약 정보 조회"""
    results = []
    for item in topk:
        item_seq = str(item.get("item_seq", ""))
        if not item_seq:
            continue
        detail = get_drug_detail(item_seq)
        if detail:
            results.append(detail)

    return {
        "candidates": results,
        "ocr": ocr_result
    }
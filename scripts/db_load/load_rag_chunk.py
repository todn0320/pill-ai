"""
RAG_CHUNK 생성 스크립트
REF_DRUG_PERMIT_DETAIL + REF_DRUG_OVERVIEW 텍스트를 청킹해서 RAG_CHUNK에 적재
실행: python scripts/db_load/load_rag_chunk.py
"""
import os
import oracledb
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

def get_connection():
    return oracledb.connect(
        user=os.environ.get("DB_USER", "medi"),
        password=os.environ.get("DB_PASSWORD", "1234"),
        dsn=os.environ.get("DB_DSN", "72.155.73.199:1521/xe")
    )

def safe_str(val):
    if val is None:
        return None
    s = str(val).strip()
    if not s or s == 'nan':
        return None
    return s

def chunk_text(text, max_len=2000):
    """텍스트를 max_len 단위로 청킹"""
    if not text:
        return []
    chunks = []
    while len(text) > max_len:
        chunks.append(text[:max_len])
        text = text[max_len:]
    if text:
        chunks.append(text)
    return chunks

# ============================================================
# REF_DRUG_PERMIT_DETAIL → RAG_CHUNK
# section_type: 효능 / 용법 / 경고주의 / 주의사항 / 금기 / 부작용
# ============================================================
def load_permit_detail_chunks(conn):
    print("\n[1/2] REF_DRUG_PERMIT_DETAIL → RAG_CHUNK 적재 중...")

    read_cursor = conn.cursor()
    read_cursor.execute("""
        SELECT ITEM_SEQ, EFCY_QESITM, USE_METHOD_QESITM,
               ATPN_WARN_QESITM, ATPN_QESITM, INTRC_QESITM, SE_QESITM
        FROM REF_DRUG_PERMIT_DETAIL
        WHERE ITEM_SEQ IS NOT NULL
    """)

    rows = read_cursor.fetchall()
    read_cursor.close()
    print(f"  총 {len(rows)}개 품목 처리 중...")

    write_cursor = conn.cursor()
    write_cursor.execute("DELETE FROM RAG_CHUNK")
    conn.commit()

    sql = """INSERT INTO RAG_CHUNK
             (ITEM_SEQ, SOURCE_TYPE, SECTION_TYPE, CHUNK_TEXT, VECTOR_ID)
             VALUES (:1, :2, :3, :4, NULL)"""

    # section_type 매핑
    section_map = {
        '효능': 1,       # EFCY_QESITM
        '용법': 2,       # USE_METHOD_QESITM
        '경고주의': 3,   # ATPN_WARN_QESITM
        '주의사항': 4,   # ATPN_QESITM
        '금기': 5,       # INTRC_QESITM
        '부작용': 6,     # SE_QESITM
    }

    total = 0
    for row in tqdm(rows, desc="허가상세 청킹"):
        item_seq = safe_str(row[0])
        if not item_seq:
            continue

        fields = [
            ('효능', row[1]),
            ('용법', row[2]),
            ('경고주의', row[3]),
            ('주의사항', row[4]),
            ('금기', row[5]),
            ('부작용', row[6]),
        ]

        for section_type, text in fields:
            text = safe_str(text)
            if not text:
                continue

            chunks = chunk_text(text, max_len=2000)
            for chunk in chunks:
                try:
                    write_cursor.execute(sql, (
                        item_seq,
                        'DUR',
                        section_type,
                        chunk,
                    ))
                    total += 1
                except Exception:
                    pass

    conn.commit()
    write_cursor.close()
    print(f"  ✅ {total}건 청크 적재 완료")


# ============================================================
# REF_DRUG_OVERVIEW → RAG_CHUNK (e약은요 요약)
# ============================================================
def load_overview_chunks(conn):
    print("\n[2/2] REF_DRUG_OVERVIEW → RAG_CHUNK 적재 중...")

    read_cursor = conn.cursor()
    read_cursor.execute("""
        SELECT ITEM_SEQ, MAIN_INGR, SUMMARY, CAUTION, STORAGE_METHOD
        FROM REF_DRUG_OVERVIEW
        WHERE ITEM_SEQ IS NOT NULL
    """)

    rows = read_cursor.fetchall()
    read_cursor.close()
    print(f"  총 {len(rows)}개 품목 처리 중...")

    write_cursor = conn.cursor()

    sql = """INSERT INTO RAG_CHUNK
             (ITEM_SEQ, SOURCE_TYPE, SECTION_TYPE, CHUNK_TEXT, VECTOR_ID)
             VALUES (:1, :2, :3, :4, NULL)"""

    total = 0
    for row in tqdm(rows, desc="e약은요 청킹"):
        item_seq = safe_str(row[0])
        if not item_seq:
            continue

        fields = [
            ('주성분', row[1]),
            ('효능', row[2]),
            ('주의사항', row[3]),
            ('보관방법', row[4]),
        ]

        for section_type, text in fields:
            text = safe_str(text)
            if not text:
                continue

            chunks = chunk_text(text, max_len=2000)
            for chunk in chunks:
                try:
                    write_cursor.execute(sql, (
                        item_seq,
                        'e약은요',
                        section_type,
                        chunk,
                    ))
                    total += 1
                except Exception:
                    pass

    conn.commit()
    write_cursor.close()
    print(f"  ✅ {total}건 청크 적재 완료")


# ============================================================
# 메인
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("RAG_CHUNK 생성 시작")
    print("=" * 50)

    conn = get_connection()
    print("DB 연결 성공")

    load_permit_detail_chunks(conn)
    load_overview_chunks(conn)

    # 최종 확인
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM RAG_CHUNK")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT SOURCE_TYPE, SECTION_TYPE, COUNT(*) FROM RAG_CHUNK GROUP BY SOURCE_TYPE, SECTION_TYPE ORDER BY SOURCE_TYPE, SECTION_TYPE")
    rows = cursor.fetchall()
    cursor.close()

    print(f"\n총 RAG_CHUNK: {total}건")
    print("\n소스별 섹션별 건수:")
    for row in rows:
        print(f"  [{row[0]}] {row[1]}: {row[2]}건")

    conn.close()
    print("\n" + "=" * 50)
    print("RAG_CHUNK 생성 완료!")
    print("=" * 50)

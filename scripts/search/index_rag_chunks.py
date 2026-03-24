"""
Azure AI Search 인덱싱 스크립트
RAG_CHUNK 데이터를 Azure AI Search에 업로드
실행: python scripts/search/index_rag_chunks.py
"""
import os
import json
import oracledb
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
)
from azure.core.credentials import AzureKeyCredential
from tqdm import tqdm

load_dotenv()

# ============================================================
# 설정
# ============================================================
SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.environ.get("AZURE_SEARCH_KEY")
INDEX_NAME = os.environ.get("AZURE_SEARCH_INDEX", "pill-rag-index")

DB_USER = os.environ.get("DB_USER", "medi")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "1234")
DB_DSN = os.environ.get("DB_DSN", "72.155.73.199:1521/xe")

BATCH_SIZE = 1000  # 한 번에 업로드할 문서 수


# ============================================================
# 1. 인덱스 생성
# ============================================================
def create_index():
    print("\n[1/3] Azure AI Search 인덱스 생성 중...")

    index_client = SearchIndexClient(
        endpoint=SEARCH_ENDPOINT,
        credential=AzureKeyCredential(SEARCH_KEY)
    )

    # 기존 인덱스 삭제 (재실행 시)
    try:
        index_client.delete_index(INDEX_NAME)
        print(f"  기존 인덱스 삭제: {INDEX_NAME}")
    except Exception:
        pass

    # 인덱스 스키마 정의
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SimpleField(name="chunk_id", type=SearchFieldDataType.Int64, filterable=True),
        SimpleField(name="item_seq", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="source_type", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="section_type", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="chunk_text", type=SearchFieldDataType.String, analyzer_name="ko.microsoft"),
        SearchableField(name="item_name", type=SearchFieldDataType.String, analyzer_name="ko.microsoft"),
        SimpleField(name="entp_name", type=SearchFieldDataType.String, filterable=True),
    ]

    index = SearchIndex(name=INDEX_NAME, fields=fields)
    index_client.create_index(index)
    print(f"  ✅ 인덱스 생성 완료: {INDEX_NAME}")


# ============================================================
# 2. Oracle에서 RAG_CHUNK + 약 이름 조회
# ============================================================
def fetch_chunks():
    print("\n[2/3] Oracle DB에서 RAG_CHUNK 조회 중...")

    conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.CHUNK_ID, r.ITEM_SEQ, r.SOURCE_TYPE, r.SECTION_TYPE, r.CHUNK_TEXT,
               p.ITEM_NAME, p.ENTP_NAME
        FROM RAG_CHUNK r
        LEFT JOIN REF_DRUG_PERMIT_LIST p ON r.ITEM_SEQ = p.ITEM_SEQ
        WHERE r.CHUNK_TEXT IS NOT NULL
        ORDER BY r.CHUNK_ID
    """)

    result = []
    for row in tqdm(cursor, desc="DB 조회"):
        result.append((
            row[0],
            row[1],
            row[2],
            row[3],
            row[4].read() if row[4] else "",  # CLOB 즉시 읽기
            row[5],
            row[6],
        ))

    cursor.close()
    conn.close()

    print(f"  ✅ {len(result)}건 조회 완료")
    return result


# ============================================================
# 3. Azure AI Search에 업로드
# ============================================================
def upload_chunks(rows):
    print(f"\n[3/3] Azure AI Search 업로드 중... (배치 크기: {BATCH_SIZE})")

    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_KEY)
    )

    total = 0
    batch = []

    for row in tqdm(rows, desc="업로드"):
        chunk_id, item_seq, source_type, section_type, chunk_text, item_name, entp_name = row

        doc = {
            "id": str(chunk_id),
            "chunk_id": int(chunk_id),
            "item_seq": str(item_seq) if item_seq else "",
            "source_type": str(source_type) if source_type else "",
            "section_type": str(section_type) if section_type else "",
            "chunk_text": str(chunk_text) if chunk_text else "",
            "item_name": str(item_name) if item_name else "",
            "entp_name": str(entp_name) if entp_name else "",
        }
        batch.append(doc)

        if len(batch) >= BATCH_SIZE:
            try:
                result = search_client.upload_documents(documents=batch)
                total += len(batch)
            except Exception as e:
                print(f"  배치 업로드 오류: {e}")
            batch = []

    # 남은 배치 처리
    if batch:
        try:
            search_client.upload_documents(documents=batch)
            total += len(batch)
        except Exception as e:
            print(f"  마지막 배치 오류: {e}")

    print(f"  ✅ 총 {total}건 업로드 완료")


# ============================================================
# 4. 검색 테스트
# ============================================================
def test_search():
    print("\n[테스트] 검색 동작 확인...")

    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_KEY)
    )

    # 테스트 쿼리
    test_queries = ["타이레놀 효능", "임부금기", "아스피린 주의사항"]

    for query in test_queries:
        results = search_client.search(
            search_text=query,
            top=2,
            select=["item_seq", "item_name", "section_type", "chunk_text"]
        )
        print(f"\n  쿼리: '{query}'")
        for r in results:
            text_preview = r['chunk_text'][:80] + "..." if r['chunk_text'] else ""
            print(f"    → [{r['section_type']}] {r['item_name']}: {text_preview}")


# ============================================================
# 메인
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("Azure AI Search 인덱싱 시작")
    print(f"엔드포인트: {SEARCH_ENDPOINT}")
    print(f"인덱스명: {INDEX_NAME}")
    print("=" * 50)

    if not SEARCH_ENDPOINT or not SEARCH_KEY:
        print("❌ .env 파일에 AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY 설정 필요!")
        exit(1)

    create_index()
    rows = fetch_chunks()
    upload_chunks(rows)
    test_search()

    print("\n" + "=" * 50)
    print("✅ Azure AI Search 인덱싱 완료!")
    print("=" * 50)
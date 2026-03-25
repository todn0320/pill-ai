"""
RAG 기반 약 설명 생성 모듈
Azure AI Search + Azure OpenAI 연동
퍼지 검색 (오타 교정) 포함
"""
import os
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

load_dotenv()

# ============================================================
# 설정
# ============================================================
SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.environ.get("AZURE_SEARCH_KEY")
INDEX_NAME = os.environ.get("AZURE_SEARCH_INDEX", "pill-rag-index")

OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
OPENAI_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")

OPENAI_KEY = (
    os.environ.get("AZURE_OPENAI_API_KEY")
    or os.environ.get("AZURE_OPENAI_KEY")
)


# ============================================================
# Azure AI Search - 관련 청크 검색 (RAG용)
# ============================================================
def search_relevant_chunks(query: str, item_seq: str = None, top: int = 5) -> list:
    """질문과 관련된 RAG 청크 검색"""
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_KEY)
    )

    filter_expr = f"item_seq eq '{item_seq}'" if item_seq else None

    results = search_client.search(
        search_text=query,
        filter=filter_expr,
        top=top,
        select=["item_seq", "item_name", "section_type", "chunk_text", "source_type"]
    )

    chunks = []
    for r in results:
        chunks.append({
            "item_seq": r.get("item_seq", ""),
            "item_name": r.get("item_name", ""),
            "section_type": r.get("section_type", ""),
            "source_type": r.get("source_type", ""),
            "chunk_text": r.get("chunk_text", ""),
        })

    return chunks


# ============================================================
# Azure AI Search - 퍼지 검색 (오타 교정용)
# ============================================================
def fuzzy_search_drug(name: str, top: int = 5) -> list:
    """
    Azure AI Search 퍼지 검색으로 유사 약 이름 검색
    '타이래놀' → '타이레놀' 자동 매칭
    검색어 뒤에 ~ 붙이면 편집 거리 기반 퍼지 검색 활성화
    """
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_KEY)
    )

    # 퍼지 검색: 검색어~ 형태로 오타 허용
    fuzzy_query = f"{name}~"

    results = search_client.search(
        search_text=fuzzy_query,
        top=top,
        select=["item_seq", "item_name", "source_type"],
        search_fields=["item_name", "chunk_text"]
    )

    seen = set()
    suggestions = []

    for r in results:
        item_name = r.get("item_name", "")
        item_seq = r.get("item_seq", "")

        if not item_name or item_seq in seen:
            continue

        seen.add(item_seq)
        suggestions.append({
            "item_seq": item_seq,
            "item_name": item_name,
            "score": r.get("@search.score", 0),
        })

        if len(suggestions) >= top:
            break

    return suggestions


# ============================================================
# Azure OpenAI - RAG 답변 생성
# ============================================================
def generate_rag_answer(question: str, chunks: list, drug_name: str = "") -> str:
    """검색된 청크를 기반으로 AI 답변 생성"""

    if not chunks:
        return "관련 약 정보를 찾을 수 없습니다. 의사나 약사에게 문의하세요."

    context = ""
    for chunk in chunks:
        section = chunk.get("section_type", "")
        text = chunk.get("chunk_text", "")
        name = chunk.get("item_name", "")
        if text:
            context += f"[{name} - {section}]\n{text}\n\n"

    client = AzureOpenAI(
        azure_endpoint=OPENAI_ENDPOINT,
        api_key=OPENAI_KEY,
        api_version="2024-02-01"
    )

    system_prompt = """당신은 복약 정보를 안내하는 의약품 정보 도우미입니다.
주어진 약품 정보를 바탕으로 질문에 정확하고 친절하게 답변하세요.
의학적 진단이나 처방은 하지 않으며, 불확실한 내용은 의사나 약사 상담을 권유하세요.
답변은 한국어로 간결하게 작성하세요."""

    user_prompt = f"""다음은 {drug_name}에 관한 의약품 정보입니다:

{context}

질문: {question}

위 정보를 참고하여 질문에 답변해주세요."""

    response = client.chat.completions.create(
        model=OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=500,
        temperature=0.3
    )

    return response.choices[0].message.content


# ============================================================
# 메인 함수 - run_pipeline 호환용 (기존 유지)
# ============================================================
def safe_text(value):
    if value is None:
        return ""
    return str(value).strip()

def shorten_text(text, max_len=120):
    text = safe_text(text)
    return text if len(text) <= max_len else text[:max_len] + "..."

def generate_explanation(drug_info: dict) -> str:
    """run_pipeline 호환용 - 기본 텍스트 설명 생성"""
    candidates = drug_info.get("candidates", [])
    if not candidates:
        return "약 정보를 확인하지 못했습니다."

    top = candidates[0]
    item_seq = top.get("ITEM_SEQ", "")
    item_name = safe_text(top.get("ITEM_NAME", ""))

    if OPENAI_ENDPOINT and OPENAI_KEY and item_seq:
        try:
            chunks = search_relevant_chunks(
                query=f"{item_name} 효능 용법 주의사항",
                item_seq=str(item_seq),
                top=5
            )
            return generate_rag_answer(
                question=f"{item_name}에 대해 설명해주세요.",
                chunks=chunks,
                drug_name=item_name
            )
        except Exception as e:
            print(f"RAG 답변 생성 실패: {e}")

    parts = []
    if safe_text(top.get("ITEM_NAME")):
        parts.append(f"인식된 약은 {safe_text(top.get('ITEM_NAME'))}입니다.")
    if safe_text(top.get("ENTP_NAME")):
        parts.append(f"제조사: {safe_text(top.get('ENTP_NAME'))}")
    if shorten_text(top.get("EFCY_QESITM")):
        parts.append(f"효능·효과: {shorten_text(top.get('EFCY_QESITM'))}")
    if shorten_text(top.get("ATPN_QESITM")):
        parts.append(f"주의사항: {shorten_text(top.get('ATPN_QESITM'))}")

    return " ".join(parts) if parts else "약 정보를 확인하지 못했습니다."
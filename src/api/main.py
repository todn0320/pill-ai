import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.pipeline.run_pipeline import run_pipeline
from src.db.query_drug import (
    search_drug_by_name,
    get_drug_detail,
    get_dur_warnings,
    search_pill_by_shape,
    get_rag_chunks,
    check_drug_interaction,
)
from src.rag.explain import search_relevant_chunks, generate_rag_answer, fuzzy_search_drug

app = FastAPI(title="Pill AI API", description="약 식별 + 복약 관리 AI 서비스")

# CORS 설정 (프론트엔드 연동)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 기본
# ============================================================
@app.get("/")
def root():
    return {"message": "Pill AI API is running"}


# ============================================================
# 이미지 인식
# ============================================================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="파일이 없습니다.")
    os.makedirs("temp", exist_ok=True)
    temp_path = os.path.join("temp", file.filename)
    try:
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        result = run_pipeline(temp_path)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ============================================================
# 약 검색 (이름으로)
# ============================================================
@app.get("/drug/search")
def drug_search(
    name: str = Query(..., description="약 이름 (예: 타이레놀)"),
    limit: int = Query(10, description="최대 결과 수")
):
    """
    약 이름으로 검색
    - GET /drug/search?name=타이레놀
    - GET /drug/search?name=아스피린&limit=5
    """
    try:
        results = search_drug_by_name(name, limit)
        return {"query": name, "count": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 퍼지 검색 (오타 교정 - Azure AI Search)
# ============================================================
@app.get("/drug/suggest")
def drug_suggest(
    name: str = Query(..., description="검색어 (오타 포함 가능, 예: 타이래놀)"),
    top: int = Query(5, description="최대 추천 수")
):
    """
    Azure AI Search 퍼지 검색으로 유사 약 이름 추천
    오타나 유사어 입력 시 올바른 약 이름 추천
    - GET /drug/suggest?name=타이래놀
    - GET /drug/suggest?name=아스피빈
    """
    try:
        # 1. 먼저 정확한 검색
        exact = search_drug_by_name(name, limit=3)

        # 2. 결과 없으면 Azure AI Search 퍼지 검색
        fuzzy = []
        if not exact:
            fuzzy = fuzzy_search_drug(name, top=top)

        return {
            "query": name,
            "exact_match": len(exact) > 0,
            "exact_results": exact,
            "suggestions": fuzzy,
            "has_suggestions": len(fuzzy) > 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 약 상세정보
# ============================================================
@app.get("/drug/info/{item_seq}")
def drug_info(item_seq: str):
    """
    품목코드로 약 상세정보 조회
    - GET /drug/info/200808876
    """
    try:
        result = get_drug_detail(item_seq)
        if not result:
            raise HTTPException(status_code=404, detail=f"약을 찾을 수 없습니다: {item_seq}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# DUR 병용금기 / 경고 조회
# ============================================================
@app.get("/drug/dur/{item_seq}")
def drug_dur(
    item_seq: str,
    type_name: str = Query(None, description="경고 유형 필터 (예: 병용금기, 임부금기, 효능군중복)")
):
    """
    품목코드로 DUR 경고 조회
    - GET /drug/dur/200808876
    - GET /drug/dur/200808876?type_name=병용금기
    """
    try:
        results = get_dur_warnings(item_seq, type_name)
        return {
            "item_seq": item_seq,
            "type_filter": type_name,
            "count": len(results),
            "warnings": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 병용금기 체크 (두 약 이름/코드로 확인)
# ============================================================
@app.get("/drug/check")
def drug_check(
    item_seq_a: str = Query(..., description="첫 번째 약 품목코드"),
    item_seq_b: str = Query(..., description="두 번째 약 품목코드"),
):
    """
    두 약의 병용금기 여부 확인 (A→B, B→A 양방향)
    - GET /drug/check?item_seq_a=199601110&item_seq_b=200501560
    """
    try:
        warnings = check_drug_interaction(item_seq_a, item_seq_b)
        return {
            "item_seq_a": item_seq_a,
            "item_seq_b": item_seq_b,
            "is_prohibited": len(warnings) > 0,
            "warning_count": len(warnings),
            "warnings": warnings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 낱알 모양/색상으로 검색
# ============================================================
@app.get("/drug/pill")
def pill_search(
    shape: str = Query(None, description="모양 (예: 원형, 타원형, 장방형)"),
    color: str = Query(None, description="색상 (예: 하양, 노랑, 분홍)"),
    print_text: str = Query(None, description="각인 문자 (예: IDG, KH10)"),
    limit: int = Query(20, description="최대 결과 수")
):
    """
    낱알 특징으로 약 검색
    - GET /drug/pill?shape=원형&color=하양
    - GET /drug/pill?print_text=IDG
    """
    try:
        results = search_pill_by_shape(shape, color, print_text, limit)
        return {
            "filters": {"shape": shape, "color": color, "print_text": print_text},
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# RAG 청크 조회
# ============================================================
@app.get("/drug/rag/{item_seq}")
def drug_rag(
    item_seq: str,
    section_type: str = Query(None, description="섹션 타입 (효능/용법/주의사항/경고주의/금기/부작용)")
):
    """
    품목코드로 RAG 청크 조회
    - GET /drug/rag/200808876
    - GET /drug/rag/200808876?section_type=효능
    """
    try:
        results = get_rag_chunks(item_seq, section_type)
        return {
            "item_seq": item_seq,
            "section_type": section_type,
            "count": len(results),
            "chunks": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# AI 질문 답변 (RAG + Azure OpenAI)
# ============================================================
@app.get("/drug/ask")
def drug_ask(
    question: str = Query(..., description="질문 (예: 임산부가 먹어도 돼?)"),
    item_seq: str = Query(None, description="특정 약 품목코드 (선택)"),
    item_name: str = Query(None, description="약 이름 (선택)")
):
    """
    약에 대한 AI 질문 답변
    - GET /drug/ask?question=타이레놀+임산부+먹어도돼
    - GET /drug/ask?question=이+약+부작용뭐야&item_seq=200808876
    """
    try:
        search_query = f"{item_name} {question}" if item_name else question

        chunks = search_relevant_chunks(
            query=search_query,
            item_seq=item_seq,
            top=5
        )

        answer = generate_rag_answer(
            question=question,
            chunks=chunks,
            drug_name=item_name or ""
        )

        return {
            "question": question,
            "item_seq": item_seq,
            "answer": answer,
            "references": [
                {
                    "item_name": c["item_name"],
                    "section_type": c["section_type"],
                    "source_type": c["source_type"],
                }
                for c in chunks
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from src.pipeline.run_pipeline import run_pipeline
from src.db.query_drug import (
    search_drug_by_name,
    get_drug_detail,
    get_dur_warnings,
    search_pill_by_shape,
    get_rag_chunks,
)
from src.rag.explain import search_relevant_chunks, generate_rag_answer

app = FastAPI(title="Pill AI API", description="약 식별 + 복약 관리 AI 서비스")


# ============================================================
# 기본
# ============================================================
@app.get("/")
def root():
    return {"message": "Pill AI API is running"}


# ============================================================
# 이미지 인식 (기존)
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
    - GET /drug/pill?shape=타원형&color=분홍&print_text=KH
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
    - GET /drug/ask?question=아스피린+주의사항&item_name=아스피린
    """
    try:
        # 검색 쿼리 구성
        search_query = f"{item_name} {question}" if item_name else question

        # 관련 청크 검색
        chunks = search_relevant_chunks(
            query=search_query,
            item_seq=item_seq,
            top=5
        )

        # AI 답변 생성
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

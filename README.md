# 💊 Pill AI — MediLink

알약 이미지 인식 기반 AI 복약 관리 서비스

## 프로젝트 구조
```
pill-ai/
├── data/
│   ├── processed/          # 정제된 parquet 데이터
│   │   ├── dur_item/       # DUR 품목 경고
│   │   ├── dur_ingredient/ # DUR 성분 경고
│   │   └── drug_info/      # 허가정보, 낱알식별, e약은요
│   └── images/             # 알약 이미지 (git 제외)
├── experiments/            # PC1~5 모델 실험
├── models/best/            # 최종 모델
├── frontend/               # React + Vite 프론트엔드
├── src/
│   ├── api/                # FastAPI
│   ├── db/                 # Oracle 연결
│   ├── inference/          # 모델 추론
│   ├── ocr/                # Azure OCR
│   ├── rag/                # RAG + Azure OpenAI 답변
│   └── pipeline/           # 전체 파이프라인
└── scripts/
    ├── db_load/            # parquet → Oracle 적재
    └── search/             # Azure AI Search 인덱싱
```

## 실행
```bash
pip install -r requirements.txt
cp .env.example .env  # 환경변수 설정

# DB 적재
python scripts/db_load/load_parquet_to_oracle.py

# RAG 청킹
python scripts/db_load/load_rag_chunk.py

# Azure AI Search 인덱싱
python scripts/search/index_rag_chunks.py

# API 서버
uvicorn src.api.main:app --reload
```

## 프론트엔드
```bash
cd frontend
npm install
npm run dev
```

## 주요 API

| 엔드포인트 | 설명 |
|-----------|------|
| GET /drug/search?name=타이레놀 | 약 이름 검색 |
| GET /drug/info/{item_seq} | 약 상세정보 |
| GET /drug/dur/{item_seq} | DUR 병용금기 경고 |
| GET /drug/pill?shape=원형&color=하양 | 낱알 모양 검색 |
| GET /drug/ask?question=임산부가+먹어도+돼&item_name=타이레놀 | AI 답변 |
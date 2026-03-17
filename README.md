# 💊 Pill AI

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
├── src/
│   ├── api/                # FastAPI
│   ├── db/                 # Oracle 연결
│   ├── inference/          # 모델 추론
│   ├── ocr/                # Azure OCR
│   ├── rag/                # RAG 설명 생성
│   └── pipeline/           # 전체 파이프라인
└── scripts/
    └── db_load/            # parquet → Oracle 적재
```

## 실행

```bash
pip install -r requirements.txt
cp .env.example .env  # 환경변수 설정

# DB 적재
python scripts/db_load/load_parquet_to_oracle.py

# API 서버
uvicorn src.api.main:app --reload
```

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
    ├── search/             # Azure AI Search 인덱싱
    └── data/               # 이미지 데이터 처리
        ├── unzip_data.sh       # 압축 해제 (병렬 + 이어서 실행)
        └── convert_to_yolo.py  # COCO JSON → YOLO 포맷 변환
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

## 이미지 데이터 처리 (AI Hub 경구약제 데이터셋)

### 1. 압축 해제

```bash
# pillv2 서버에서 실행
chmod +x scripts/data/unzip_data.sh
nohup scripts/data/unzip_data.sh > /data/unzip_main.log 2>&1 &

# 진행 확인
tail -f /data/unzip_progress.log
ls /data/unzip_done/ | wc -l   # 완료 개수
```

- 병렬 30코어로 압축 해제 (PARALLEL 변수로 조정 가능)
- 중단되어도 재실행 시 완료된 파일 건너뜀 (`.done` 마커 방식)
- 실패한 파일은 자동 삭제 후 재시도

### 2. YOLO 포맷 변환

```bash
# tqdm 설치
pip3 install tqdm

# pillv2 서버에서 실행
nohup python3 scripts/data/convert_to_yolo.py > /data/convert_log.txt 2>&1 &

# 진행 확인
tail -f /data/convert_log.txt
```

- COCO JSON `[x, y, w, h]` → YOLO `[cx, cy, w, h]` (정규화) 변환
- 약 코드(K-000059 등) → class_id 자동 매핑
- 중단되어도 재실행 시 이어서 변환
- 출력: `/data/yolo_dataset/` (images/, labels/, dataset.yaml)

### 데이터셋 현황 (AI Hub 단일경구약제 5000종)

| 항목 | 수량 |
|------|------|
| Training 이미지 | 2,467,942장 |
| Training 라벨링 | 2,451,927개 |
| Validation 이미지 | 162,056장 |
| Validation 라벨링 | 165,576개 |
| 약 종류 | 3,975종 |
| 서버 | Azure pillv2 (Korea Central) |
| 디스크 | 32TB (/data) |

### YOLO 학습 시작

```bash
# YOLOv8 설치
pip install ultralytics

# 학습 시작 (NC80 H100 x2 기준)
yolo detect train \
  data=/data/yolo_dataset/dataset.yaml \
  model=yolov8m.pt \
  epochs=100 \
  imgsz=640 \
  batch=64 \
  device=0,1
```

## 주요 API

| 엔드포인트 | 설명 |
|-----------|------|
| GET /drug/search?name=타이레놀 | 약 이름 검색 |
| GET /drug/suggest?name=타이래놀 | 오타 교정 (Azure AI Search 퍼지 검색) |
| GET /drug/info/{item_seq} | 약 상세정보 |
| GET /drug/dur/{item_seq} | DUR 병용금기 경고 |
| GET /drug/check?item_seq_a=...&item_seq_b=... | 병용금기 체크 |
| GET /drug/pill?shape=원형&color=하양 | 낱알 모양 검색 |
| GET /drug/ask?question=임산부가+먹어도+돼&item_name=타이레놀 | AI 답변 (RAG) |
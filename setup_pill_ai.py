"""
pill-ai 프로젝트 초기 설정 스크립트
실행: python setup_pill_ai.py
"""

import os

BASE = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────
# 1. 폴더 구조 생성
# ─────────────────────────────────────────
DIRS = [
    "data/processed/dur_item",
    "data/processed/dur_ingredient",
    "data/processed/drug_info",
    "data/images",
    "experiments/common/scripts",
    "experiments/common/models",
    "experiments/pc1/data/meta",
    "experiments/pc1/experiments",
    "experiments/pc1/models/eval_results",
    "experiments/pc2/data/meta",
    "experiments/pc2/experiments",
    "experiments/pc2/models/eval_results",
    "experiments/pc3/data/meta",
    "experiments/pc3/experiments",
    "experiments/pc3/models/eval_results",
    "experiments/pc4/data/meta",
    "experiments/pc4/experiments",
    "experiments/pc4/models/eval_results",
    "experiments/pc5/data/meta",
    "experiments/pc5/experiments",
    "experiments/pc5/models/eval_results",
    "experiments/results",
    "models/best",
    "src/api",
    "src/db",
    "src/inference",
    "src/ocr",
    "src/rag",
    "src/pipeline",
    "src/ui",
    "scripts/db_load",
    "scripts/train",
    "tests",
    "logs",
    "docs",
]

for d in DIRS:
    full = os.path.join(BASE, d)
    os.makedirs(full, exist_ok=True)
    print(f"  📁 {d}")

# ─────────────────────────────────────────
# 2. .gitkeep (빈 폴더 유지용)
# ─────────────────────────────────────────
GITKEEP_DIRS = [
    "data/images",
    "data/processed/dur_item",
    "data/processed/dur_ingredient",
    "data/processed/drug_info",
    "experiments/results",
    "models/best",
    "logs",
    "docs",
]

for d in GITKEEP_DIRS:
    path = os.path.join(BASE, d, ".gitkeep")
    open(path, "w").close()

# ─────────────────────────────────────────
# 3. __init__.py
# ─────────────────────────────────────────
INIT_DIRS = [
    "src",
    "src/api",
    "src/db",
    "src/inference",
    "src/ocr",
    "src/rag",
    "src/pipeline",
    "src/ui",
]

for d in INIT_DIRS:
    path = os.path.join(BASE, d, "__init__.py")
    open(path, "w").close()

# ─────────────────────────────────────────
# 4. 소스 파일 생성
# ─────────────────────────────────────────
FILES = {}

# ── src/api/main.py ──
FILES["src/api/main.py"] = '''import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from src.pipeline.run_pipeline import run_pipeline

app = FastAPI(title="Pill Identification API")

@app.get("/")
def root():
    return {"message": "Pill Identification API is running"}

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
'''

# ── src/pipeline/run_pipeline.py ──
FILES["src/pipeline/run_pipeline.py"] = '''import os
import json
from src.inference.predictor import predict_topk
from src.ocr.ocr_engine import run_ocr
from src.db.query_drug import query_drug
from src.rag.explain import generate_explanation

def run_pipeline(image_path: str):
    topk = predict_topk(image_path, k=5)
    ocr_result = run_ocr(image_path)
    drug_info = query_drug(topk, ocr_result)
    rag_text = generate_explanation(drug_info)
    return {
        "topk": topk,
        "ocr": ocr_result,
        "drug_info": drug_info,
        "rag_text": rag_text
    }

if __name__ == "__main__":
    image_path = "data/images/sample.png"
    if not os.path.exists(image_path):
        print("이미지 파일을 찾을 수 없습니다.")
    else:
        result = run_pipeline(image_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
'''

# ── src/pipeline/schemas.py ──
FILES["src/pipeline/schemas.py"] = '''from pydantic import BaseModel
from typing import List, Optional

class TopKResult(BaseModel):
    item_seq: str
    score: float

class OCRResult(BaseModel):
    ocr_raw: List[str]
    ocr_norm: List[str]

class PipelineResult(BaseModel):
    topk: List[TopKResult]
    ocr: OCRResult
    drug_info: dict
    rag_text: str
'''

# ── src/inference/model_loader.py ──
FILES["src/inference/model_loader.py"] = '''import torch
import torch.nn as nn
from torchvision import models

def load_model(model_path: str, num_classes: int, device: str = None):
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    checkpoint = torch.load(model_path, map_location=device)
    if isinstance(checkpoint, dict):
        if "model_state_dict" in checkpoint:
            state_dict = checkpoint["model_state_dict"]
        elif "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]
        else:
            state_dict = checkpoint
        model.load_state_dict(state_dict)
    else:
        model = checkpoint
    model.to(device)
    model.eval()
    return model, device
'''

# ── src/inference/preprocess.py ──
FILES["src/inference/preprocess.py"] = '''from PIL import Image
from torchvision import transforms

def get_inference_transform():
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

def preprocess_image(image_path: str):
    image = Image.open(image_path).convert("RGB")
    transform = get_inference_transform()
    return transform(image).unsqueeze(0)
'''

# ── src/inference/predictor.py ──
FILES["src/inference/predictor.py"] = '''import os
import json
import torch
from src.inference.model_loader import load_model
from src.inference.preprocess import preprocess_image

MODEL_PATH = os.path.join("models", "best", "pill_cls_best.pt")
LABEL_MAP_PATH = os.path.join("models", "best", "label_map.json")

def load_label_map(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_class_to_item_seq(label_map: dict):
    if not label_map:
        return {}
    if "idx_to_class" in label_map:
        return {int(k): str(v) for k, v in label_map["idx_to_class"].items()}
    if "class_to_idx" in label_map:
        return {int(v): str(k) for k, v in label_map["class_to_idx"].items()}
    sample_val = label_map[next(iter(label_map.keys()))]
    if isinstance(sample_val, int):
        return {int(v): str(k) for k, v in label_map.items()}
    return {int(k): str(v) for k, v in label_map.items()}

def predict_topk(image_path: str, k: int = 5):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"입력 이미지 없음: {image_path}")
    label_map = load_label_map(LABEL_MAP_PATH)
    class_to_item_seq = build_class_to_item_seq(label_map)
    model, device = load_model(MODEL_PATH, num_classes=len(class_to_item_seq))
    image_tensor = preprocess_image(image_path).to(device)
    with torch.no_grad():
        probs = torch.softmax(model(image_tensor), dim=1)
        top_probs, top_indices = torch.topk(probs, k=min(k, len(class_to_item_seq)), dim=1)
    return [
        {"item_seq": class_to_item_seq.get(idx, f"unknown_{idx}"), "score": round(float(score), 4)}
        for idx, score in zip(top_indices.squeeze(0).cpu().tolist(), top_probs.squeeze(0).cpu().tolist())
    ]
'''

# ── src/inference/topk.py ──
FILES["src/inference/topk.py"] = '''# topk 후처리 유틸
def filter_topk_by_threshold(topk: list, threshold: float = 0.01) -> list:
    return [x for x in topk if x["score"] >= threshold]
'''

# ── src/ocr/ocr_engine.py (Azure) ──
FILES["src/ocr/ocr_engine.py"] = '''import os
import cv2
import tempfile
from dotenv import load_dotenv
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from src.ocr.preprocess_ocr import generate_ocr_variants
from src.ocr.normalize import normalize_imprint

load_dotenv()

client = DocumentIntelligenceClient(
    endpoint=os.environ["AZURE_DOC_INTELLIGENCE_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["AZURE_DOC_INTELLIGENCE_KEY"])
)

def run_ocr(image_path: str):
    variants = generate_ocr_variants(image_path)
    ocr_raw, ocr_norm = [], []
    for variant_name, variant_img in variants:
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                temp_path = tmp.name
                cv2.imwrite(temp_path, variant_img)
            with open(temp_path, "rb") as f:
                poller = client.begin_analyze_document(
                    "prebuilt-read",
                    analyze_request=f,
                    content_type="application/octet-stream"
                )
            result = poller.result()
            for page in result.pages:
                for word in page.words:
                    raw = word.content.strip()
                    norm = normalize_imprint(raw)
                    if raw:
                        ocr_raw.append(raw)
                    if norm:
                        ocr_norm.append(norm)
        except Exception as e:
            print(f"OCR 실패 ({variant_name}):", e)
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
    return {
        "ocr_raw": list(dict.fromkeys(ocr_raw)),
        "ocr_norm": list(dict.fromkeys(ocr_norm))
    }
'''

# ── src/ocr/preprocess_ocr.py ──
FILES["src/ocr/preprocess_ocr.py"] = '''import cv2

def resize_if_needed(image, max_side=1280):
    h, w = image.shape[:2]
    if max(h, w) <= max_side:
        return image
    scale = max_side / max(h, w)
    return cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

def generate_ocr_variants(image_path: str):
    img = cv2.imread(image_path)
    if img is None:
        return []
    img = resize_if_needed(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    enlarged = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    h, w = img.shape[:2]
    crop = img[int(h*0.2):int(h*0.8), int(w*0.2):int(w*0.8)]
    return [
        ("original", img),
        ("gray", gray),
        ("threshold", thresh),
        ("enlarged_gray", enlarged),
        ("center_crop", crop),
    ]
'''

# ── src/ocr/normalize.py ──
FILES["src/ocr/normalize.py"] = '''def normalize_imprint(text: str) -> str:
    if not text:
        return ""
    return text.upper().replace("-", "").replace(" ", "").replace("_", "")
'''

# ── src/db/query_drug.py ──
FILES["src/db/query_drug.py"] = '''import os
import oracledb
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return oracledb.connect(
        user=os.environ.get("DB_USER", "kim1"),
        password=os.environ.get("DB_PASSWORD", "1"),
        dsn=os.environ.get("DB_DSN", "192.168.0.80:1521/XE")
    )

def normalize_text(text: str) -> str:
    if text is None:
        return ""
    return str(text).upper().replace("-", "").replace(" ", "").replace("_", "")

def read_lob(value):
    if value is None:
        return None
    try:
        return value.read()
    except AttributeError:
        return value

def score_ocr_match(ocr_norm_list, print_front, print_back):
    score = 0.0
    for ocr_text in ocr_norm_list:
        ocr_norm = normalize_text(ocr_text)
        if not ocr_norm:
            continue
        for target in [normalize_text(print_front), normalize_text(print_back)]:
            if not target:
                continue
            if ocr_norm == target:
                score = max(score, 1.0)
            elif len(ocr_norm) >= 2 and ocr_norm in target:
                score = max(score, 0.6)
            elif len(target) >= 2 and target in ocr_norm:
                score = max(score, 0.5)
    return score

def query_drug(topk_candidates, ocr_result):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        item_seqs = [str(x["item_seq"]) for x in topk_candidates]
        ai_score_map = {str(x["item_seq"]): float(x["score"]) for x in topk_candidates}
        ocr_norm_list = ocr_result.get("ocr_norm", [])
        if not item_seqs:
            return {"selected_item": None, "candidates": [], "message": "topk 후보가 없습니다."}
        placeholders = ",".join([f":{i+1}" for i in range(len(item_seqs))])
        sql = f"""
            SELECT p.ITEM_SEQ, p.ITEM_NAME, p.ENTP_NAME, p.ETC_OTC_CODE,
                   f.PRINT_FRONT, f.PRINT_BACK, f.DRUG_SHAPE, f.COLOR_CLASS1, f.COLOR_CLASS2,
                   d.EFCY_QESITM, d.USE_METHOD_QESITM, d.ATPN_QESITM, d.INTRC_QESITM
            FROM REF_DRUG_PERMIT_LIST p
            LEFT JOIN PILL_IMAGE_FEATURE f ON p.ITEM_SEQ = f.ITEM_SEQ
            LEFT JOIN REF_DRUG_PERMIT_DETAIL d ON p.ITEM_SEQ = d.ITEM_SEQ
            WHERE p.ITEM_SEQ IN ({placeholders})
        """
        cursor.execute(sql, item_seqs)
        candidates = []
        for row in cursor.fetchall():
            item_seq = str(row[0])
            ai_score = ai_score_map.get(item_seq, 0.0)
            ocr_score = score_ocr_match(ocr_norm_list, row[4], row[5])
            candidates.append({
                "item_seq": item_seq, "item_name": row[1], "entp_name": row[2],
                "etc_otc_code": row[3], "print_front": row[4], "print_back": row[5],
                "drug_shape": row[6], "color_class1": row[7], "color_class2": row[8],
                "ai_score": round(ai_score, 4), "ocr_match_score": round(ocr_score, 4),
                "final_score": round((0.8 * ai_score) + (0.2 * ocr_score), 4),
                "effect": read_lob(row[9]), "usage": read_lob(row[10]),
                "warning": read_lob(row[11]), "interaction": read_lob(row[12])
            })
        candidates.sort(key=lambda x: x["final_score"], reverse=True)
        if not candidates:
            return {"selected_item": None, "candidates": [], "message": "DB에서 후보를 찾지 못했습니다."}
        selected = candidates[0]
        return {
            "selected_item": {"item_seq": selected["item_seq"], "item_name": selected["item_name"], "confidence": selected["final_score"]},
            "candidates": candidates, "message": "후보 재정렬 완료"
        }
    finally:
        cursor.close()
        conn.close()
'''

# ── src/db/test_connection.py ──
FILES["src/db/test_connection.py"] = '''import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = oracledb.connect(
        user=os.environ.get("DB_USER", "kim1"),
        password=os.environ.get("DB_PASSWORD", "1"),
        dsn=os.environ.get("DB_DSN", "192.168.0.80:1521/XE")
    )
    cursor = conn.cursor()
    cursor.execute("SELECT ITEM_SEQ, ITEM_NAME FROM REF_DRUG_PERMIT_LIST WHERE ROWNUM <= 5")
    for row in cursor:
        print(row)
    cursor.close()
    conn.close()
    print("Oracle 연결 성공")
except Exception as e:
    print("Oracle 연결 실패:", e)
'''

# ── src/rag/explain.py ──
FILES["src/rag/explain.py"] = '''def safe_text(value):
    if value is None:
        return ""
    return str(value).strip()

def shorten_text(text, max_len=120):
    text = safe_text(text)
    return text if len(text) <= max_len else text[:max_len] + "..."

def generate_explanation(drug_info: dict) -> str:
    candidates = drug_info.get("candidates", [])
    if not candidates:
        return "약 정보를 확인하지 못했습니다."
    top = candidates[0]
    parts = []
    if safe_text(top.get("item_name")):
        parts.append(f"인식된 약은 {safe_text(top.get('item_name'))}입니다.")
    if safe_text(top.get("entp_name")):
        parts.append(f"제조사: {safe_text(top.get('entp_name'))}")
    if safe_text(top.get("etc_otc_code")):
        parts.append(f"구분: {safe_text(top.get('etc_otc_code'))}")
    if shorten_text(top.get("effect")):
        parts.append(f"효능·효과: {shorten_text(top.get('effect'))}")
    if shorten_text(top.get("usage")):
        parts.append(f"용법·용량: {shorten_text(top.get('usage'))}")
    if shorten_text(top.get("warning")):
        parts.append(f"주의사항: {shorten_text(top.get('warning'))}")
    if shorten_text(top.get("interaction")):
        parts.append(f"상호작용: {shorten_text(top.get('interaction'))}")
    return " ".join(parts)
'''

# ── scripts/db_load/load_parquet_to_oracle.py ──
FILES["scripts/db_load/load_parquet_to_oracle.py"] = '''"""
parquet → Oracle DB 적재 스크립트
실행: python scripts/db_load/load_parquet_to_oracle.py
"""
import os
import pandas as pd
import oracledb
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

def get_connection():
    return oracledb.connect(
        user=os.environ.get("DB_USER", "kim1"),
        password=os.environ.get("DB_PASSWORD", "1"),
        dsn=os.environ.get("DB_DSN", "192.168.0.80:1521/XE")
    )

def load_permit_list(conn):
    """의약품 허가목록 → REF_DRUG_PERMIT_LIST"""
    path = "data/processed/drug_info/drugPrmsnInfo_의약품제품허가목록_clean.parquet"
    if not os.path.exists(path):
        print(f"파일 없음: {path}")
        return
    df = pd.read_parquet(path)
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE REF_DRUG_PERMIT_LIST")
    sql = "INSERT INTO REF_DRUG_PERMIT_LIST (ITEM_SEQ, ITEM_NAME, ENTP_NAME, ETC_OTC_CODE) VALUES (:1, :2, :3, :4)"
    data = [(str(row.item_seq), str(row.item_name)[:200] if pd.notna(row.item_name) else None,
             str(row.entp_name)[:200] if pd.notna(row.entp_name) else None,
             str(row.etc_otc)[:50] if pd.notna(row.etc_otc) else None)
            for row in tqdm(df.itertuples(), total=len(df), desc="허가목록")]
    cursor.executemany(sql, data)
    conn.commit()
    cursor.close()
    print(f"  허가목록 {len(data)}건 적재 완료")

def load_pill_image_feature(conn):
    """낱알식별정보 → PILL_IMAGE_FEATURE"""
    path = "data/processed/drug_info/낱알식별정보.parquet"
    if not os.path.exists(path):
        print(f"파일 없음: {path}")
        return
    df = pd.read_parquet(path)
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE PILL_IMAGE_FEATURE")
    sql = """INSERT INTO PILL_IMAGE_FEATURE
             (ITEM_SEQ, PRINT_FRONT, PRINT_BACK, DRUG_SHAPE, COLOR_CLASS1, COLOR_CLASS2, LINE_FRONT, LINE_BACK)
             VALUES (:1, :2, :3, :4, :5, :6, :7, :8)"""
    data = []
    for row in tqdm(df.itertuples(), total=len(df), desc="낱알식별"):
        data.append((
            str(row.item_seq),
            str(row.print_front)[:100] if pd.notna(getattr(row, "print_front", None)) else None,
            str(row.print_back)[:100] if pd.notna(getattr(row, "print_back", None)) else None,
            str(row.drug_shape)[:50] if pd.notna(getattr(row, "drug_shape", None)) else None,
            str(row.color_class1)[:50] if pd.notna(getattr(row, "color_class1", None)) else None,
            str(row.color_class2)[:50] if pd.notna(getattr(row, "color_class2", None)) else None,
            str(row.line_front)[:50] if pd.notna(getattr(row, "line_front", None)) else None,
            str(row.line_back)[:50] if pd.notna(getattr(row, "line_back", None)) else None,
        ))
    cursor.executemany(sql, data)
    conn.commit()
    cursor.close()
    print(f"  낱알식별 {len(data)}건 적재 완료")

def load_permit_detail(conn):
    """의약품 허가정보 → REF_DRUG_PERMIT_DETAIL"""
    path = "data/processed/drug_info/drugPrmsnInfo_의약품제품허가정보_cleantext_NB_DOC_DEL.parquet"
    if not os.path.exists(path):
        print(f"파일 없음: {path}")
        return
    df = pd.read_parquet(path)
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE REF_DRUG_PERMIT_DETAIL")
    sql = """INSERT INTO REF_DRUG_PERMIT_DETAIL
             (ITEM_SEQ, EFCY_QESITM, USE_METHOD_QESITM, ATPN_QESITM, INTRC_QESITM)
             VALUES (:1, :2, :3, :4, :5)"""
    data = []
    for row in tqdm(df.itertuples(), total=len(df), desc="허가상세"):
        data.append((
            str(row.item_seq),
            str(row.ee_doc_data)[:4000] if pd.notna(getattr(row, "ee_doc_data", None)) else None,
            str(row.ud_doc_data)[:4000] if pd.notna(getattr(row, "ud_doc_data", None)) else None,
            str(row.warning_text)[:4000] if pd.notna(getattr(row, "warning_text", None)) else None,
            str(row.caution_text)[:4000] if pd.notna(getattr(row, "caution_text", None)) else None,
        ))
    cursor.executemany(sql, data)
    conn.commit()
    cursor.close()
    print(f"  허가상세 {len(data)}건 적재 완료")

if __name__ == "__main__":
    print("Oracle DB 적재 시작...")
    conn = get_connection()
    load_permit_list(conn)
    load_pill_image_feature(conn)
    load_permit_detail(conn)
    conn.close()
    print("\\n✅ 전체 적재 완료!")
'''

# ── .env 템플릿 ──
FILES[".env.example"] = '''# Azure OCR
AZURE_DOC_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOC_INTELLIGENCE_KEY=your-key-here

# Oracle DB
DB_USER=kim1
DB_PASSWORD=1
DB_DSN=192.168.0.80:1521/XE

# Azure OpenAI (RAG용, 나중에)
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_KEY=
AZURE_OPENAI_DEPLOYMENT=
'''

# ── .gitignore ──
FILES[".gitignore"] = '''# 이미지 데이터 (용량 큼)
data/images/*
!data/images/.gitkeep

# 모델 파일
models/*
!models/best/.gitkeep

# parquet 데이터 (필요시 주석 해제)
# *.parquet

# 환경변수
.env

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.egg-info/
dist/
build/

# OS
.DS_Store
Thumbs.db

# temp
temp/
logs/*.log
'''

# ── requirements.txt ──
FILES["requirements.txt"] = '''# Core
torch>=2.0.0
torchvision>=0.15.0
numpy>=1.24.0
pandas>=2.0.0
Pillow>=10.0.0
opencv-python>=4.8.0
scikit-learn>=1.3.0

# Azure
azure-ai-documentintelligence>=1.0.0
azure-core>=1.29.0
openai>=1.0.0

# DB
oracledb>=2.0.0

# API
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0

# Data
pyarrow>=12.0.0
fastparquet>=2023.0.0

# Utils
python-dotenv>=1.0.0
tqdm>=4.65.0
PyYAML>=6.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
tiktoken>=0.5.0

# UI
gradio>=4.0.0
'''

# ── README.md ──
FILES["README.md"] = '''# 💊 Pill AI

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
'''

# 파일 생성
for path, content in FILES.items():
    full_path = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  📄 {path}")

print("\n✅ pill-ai 프로젝트 초기 설정 완료!")
print("다음 단계:")
print("  1. cp .env.example .env  →  실제 키값 입력")
print("  2. data/processed/ 에 parquet 파일 복사")
print("  3. python scripts/db_load/load_parquet_to_oracle.py")

from pydantic import BaseModel
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

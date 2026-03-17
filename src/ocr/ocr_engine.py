import os
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

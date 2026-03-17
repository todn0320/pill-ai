import os
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

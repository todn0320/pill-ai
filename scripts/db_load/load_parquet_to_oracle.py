"""
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
    print("\n✅ 전체 적재 완료!")

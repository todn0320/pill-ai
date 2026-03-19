"""
parquet → Oracle DB 전체 적재 스크립트
실행: python scripts/db_load/load_parquet_to_oracle.py
"""
import os
import glob
import pandas as pd
import oracledb
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

def get_connection():
    return oracledb.connect(
        user=os.environ.get("DB_USER", "medi"),
        password=os.environ.get("DB_PASSWORD", "1234"),
        dsn=os.environ.get("DB_DSN", "72.155.73.199:1521/xe")
    )

def safe_str(val, max_len=None):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = str(val).strip()
    if not s or s == 'nan':
        return None
    if max_len:
        return s[:max_len]
    return s

def delete_all(cursor, table):
    """FK 때문에 TRUNCATE 안되니까 DELETE 사용"""
    try:
        cursor.execute(f"DELETE FROM {table}")
    except Exception as e:
        print(f"  DELETE {table} 실패: {e}")

# ============================================================
# 1. REF_DRUG_PERMIT_LIST
# ============================================================
def load_permit_list(conn):
    print("\n[1/8] REF_DRUG_PERMIT_LIST 적재 중...")
    path = "data/processed/drug_info/drugPrmsnInfo_의약품제품허가목록_clean.parquet"
    if not os.path.exists(path):
        print(f"  파일 없음: {path}"); return

    df = pd.read_parquet(path)
    print(f"  컬럼: {list(df.columns)}, 행: {len(df)}")

    cursor = conn.cursor()
    delete_all(cursor, "REF_DRUG_PERMIT_LIST")
    conn.commit()

    sql = """INSERT INTO REF_DRUG_PERMIT_LIST
             (ITEM_SEQ, ITEM_NAME, ENTP_NAME, ITEM_PERMIT_DATE, ETC_OTC_CODE, CANCEL_DATE, CANCEL_NAME)
             VALUES (:1, :2, :3, :4, :5, :6, :7)"""

    success = 0
    for row in tqdm(df.itertuples(), total=len(df), desc="허가목록"):
        try:
            cursor.execute(sql, (
                safe_str(getattr(row, 'item_seq', None), 20),
                safe_str(getattr(row, 'item_name', None), 500),
                safe_str(getattr(row, 'entp_name', None), 500),
                safe_str(getattr(row, 'item_permit_date', None), 20),
                safe_str(getattr(row, 'etc_otc', None), 50),
                safe_str(getattr(row, 'cancel_date', None), 20),
                safe_str(getattr(row, 'cancel_name', None), 200),
            ))
            success += 1
        except Exception:
            pass

    conn.commit()
    cursor.close()
    print(f"  ✅ {success}/{len(df)}건 적재 완료")


# ============================================================
# 2. REF_DRUG_PERMIT_DETAIL
# 실제 컬럼: item_seq, ee_doc_data, ud_doc_data, warning_text,
#           contraindication_text, caution_text, adverse_text
# ============================================================
def load_permit_detail(conn):
    print("\n[2/8] REF_DRUG_PERMIT_DETAIL 적재 중...")
    path = "data/processed/drug_info/drugPrmsnInfo_의약품제품허가정보_cleantext_NB_DOC_DEL.parquet"
    if not os.path.exists(path):
        print(f"  파일 없음: {path}"); return

    df = pd.read_parquet(path)
    print(f"  컬럼: {list(df.columns)}, 행: {len(df)}")

    cursor = conn.cursor()
    delete_all(cursor, "REF_DRUG_PERMIT_DETAIL")
    conn.commit()

    sql = """INSERT INTO REF_DRUG_PERMIT_DETAIL
             (ITEM_SEQ, EFCY_QESITM, USE_METHOD_QESITM, ATPN_WARN_QESITM, ATPN_QESITM, INTRC_QESITM, SE_QESITM)
             VALUES (:1, :2, :3, :4, :5, :6, :7)"""

    success = 0
    for row in tqdm(df.itertuples(), total=len(df), desc="허가상세"):
        try:
            cursor.execute(sql, (
                safe_str(getattr(row, 'item_seq', None), 20),
                safe_str(getattr(row, 'ee_doc_data', None)),
                safe_str(getattr(row, 'ud_doc_data', None)),
                safe_str(getattr(row, 'warning_text', None)),
                safe_str(getattr(row, 'caution_text', None)),
                safe_str(getattr(row, 'contraindication_text', None)),
                safe_str(getattr(row, 'adverse_text', None)),
            ))
            success += 1
        except Exception:
            pass

    conn.commit()
    cursor.close()
    print(f"  ✅ {success}/{len(df)}건 적재 완료")


# ============================================================
# 3. REF_DRUG_INGREDIENT
# 실제 컬럼: item_seq, mtral_nm, qnt, ingd_unit_cd, main_ingr_eng
# ============================================================
def load_drug_ingredient(conn):
    print("\n[3/8] REF_DRUG_INGREDIENT 적재 중...")
    paths = glob.glob("data/processed/drug_info/drugPrmsnInfo_의약품제품주성분_*.parquet")
    if not paths:
        print("  파일 없음"); return

    cursor = conn.cursor()
    delete_all(cursor, "REF_DRUG_INGREDIENT")
    conn.commit()

    sql = """INSERT INTO REF_DRUG_INGREDIENT
             (ITEM_SEQ, INGREDIENT_CODE, INGR_NAME, INGR_ENG_NAME, INGR_AMOUNT, INGR_UNIT)
             VALUES (:1, :2, :3, :4, :5, :6)"""

    total = 0
    for path in sorted(paths):
        df = pd.read_parquet(path)
        print(f"  {os.path.basename(path)}: {list(df.columns)}, 행={len(df)}")

        success = 0
        for row in tqdm(df.itertuples(), total=len(df), desc=os.path.basename(path)[:30]):
            try:
                cursor.execute(sql, (
                    safe_str(getattr(row, 'item_seq', None), 20),
                    safe_str(getattr(row, 'mtral_nm', None), 20),   # code 대신 성분명 앞20자
                    safe_str(getattr(row, 'mtral_nm', None), 200),  # 성분명
                    safe_str(getattr(row, 'main_ingr_eng', None), 200),
                    safe_str(getattr(row, 'qnt', None), 50),
                    safe_str(getattr(row, 'ingd_unit_cd', None), 20),
                ))
                success += 1
            except Exception:
                pass

        conn.commit()
        total += success

    cursor.close()
    print(f"  ✅ 총 {total}건 적재 완료")


# ============================================================
# 4. REF_DRUG_OVERVIEW (e약은요)
# 실제 컬럼: item_seq, item_name, efficacy_text_easy,
#           caution_text_easy, storage_text_easy
# ============================================================
def load_drug_overview(conn):
    print("\n[4/8] REF_DRUG_OVERVIEW 적재 중...")
    path = "data/processed/drug_info/의약품개요정보(e약은요).parquet"
    if not os.path.exists(path):
        print(f"  파일 없음: {path}"); return

    df = pd.read_parquet(path)
    print(f"  컬럼: {list(df.columns)}, 행: {len(df)}")

    cursor = conn.cursor()
    delete_all(cursor, "REF_DRUG_OVERVIEW")
    conn.commit()

    sql = """INSERT INTO REF_DRUG_OVERVIEW
             (ITEM_SEQ, MAIN_INGR, SUMMARY, CAUTION, STORAGE_METHOD)
             VALUES (:1, :2, :3, :4, :5)"""

    success = 0
    for row in tqdm(df.itertuples(), total=len(df), desc="e약은요"):
        try:
            cursor.execute(sql, (
                safe_str(getattr(row, 'item_seq', None), 20),
                safe_str(getattr(row, 'item_name', None), 500),
                safe_str(getattr(row, 'efficacy_text_easy', None)),
                safe_str(getattr(row, 'caution_text_easy', None)),
                safe_str(getattr(row, 'storage_text_easy', None), 500),
            ))
            success += 1
        except Exception:
            pass

    conn.commit()
    cursor.close()
    print(f"  ✅ {success}/{len(df)}건 적재 완료")


# ============================================================
# 5. PILL_IMAGE_FEATURE (낱알식별정보)
# ============================================================
def load_pill_image_feature(conn):
    print("\n[5/8] PILL_IMAGE_FEATURE 적재 중...")
    path = "data/processed/drug_info/낱알식별정보.parquet"
    if not os.path.exists(path):
        print(f"  파일 없음: {path}"); return

    df = pd.read_parquet(path)
    print(f"  컬럼: {list(df.columns)}, 행: {len(df)}")

    cursor = conn.cursor()
    delete_all(cursor, "PILL_IMAGE_FEATURE")
    conn.commit()

    sql = """INSERT INTO PILL_IMAGE_FEATURE
             (ITEM_SEQ, PRINT_FRONT, PRINT_BACK, DRUG_SHAPE, COLOR_CLASS1, COLOR_CLASS2,
              LINE_FRONT, LINE_BACK, LENG_LONG, LENG_SHORT, THICK, ITEM_IMAGE_URL)
             VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12)"""

    def to_num(row, attr):
        try:
            v = getattr(row, attr, None)
            return float(v) if v is not None and str(v) != 'nan' else None
        except:
            return None

    success = 0
    for row in tqdm(df.itertuples(), total=len(df), desc="낱알식별"):
        try:
            cursor.execute(sql, (
                safe_str(getattr(row, 'ITEM_SEQ', None) or getattr(row, 'item_seq', None), 20),
                safe_str(getattr(row, 'PRINT_FRONT', None) or getattr(row, 'print_front', None), 100),
                safe_str(getattr(row, 'PRINT_BACK', None) or getattr(row, 'print_back', None), 100),
                safe_str(getattr(row, 'DRUG_SHAPE', None) or getattr(row, 'drug_shape', None), 50),
                safe_str(getattr(row, 'COLOR_CLASS1', None) or getattr(row, 'color_class1', None), 50),
                safe_str(getattr(row, 'COLOR_CLASS2', None) or getattr(row, 'color_class2', None), 50),
                safe_str(getattr(row, 'LINE_FRONT', None) or getattr(row, 'line_front', None), 50),
                safe_str(getattr(row, 'LINE_BACK', None) or getattr(row, 'line_back', None), 50),
                to_num(row, 'LENG_LONG') or to_num(row, 'leng_long'),
                to_num(row, 'LENG_SHORT') or to_num(row, 'leng_short'),
                to_num(row, 'THICK') or to_num(row, 'thick'),
                safe_str(getattr(row, 'ITEM_IMAGE', None) or getattr(row, 'item_image_url', None), 500),
            ))
            success += 1
        except Exception:
            pass

    conn.commit()
    cursor.close()
    print(f"  ✅ {success}/{len(df)}건 적재 완료")


# ============================================================
# 6. REFERENCE_INGREDIENT (성분 마스터)
# ingredient_code 없으므로 mtral_nm으로 dedupe
# ============================================================
def load_reference_ingredient(conn):
    print("\n[6/8] REFERENCE_INGREDIENT 적재 중...")
    paths = glob.glob("data/processed/drug_info/drugPrmsnInfo_의약품제품주성분_*.parquet")
    if not paths:
        print("  파일 없음"); return

    cursor = conn.cursor()
    delete_all(cursor, "REFERENCE_INGREDIENT")
    conn.commit()

    dfs = [pd.read_parquet(p) for p in paths]
    df = pd.concat(dfs, ignore_index=True)

    sql = """INSERT INTO REFERENCE_INGREDIENT
             (INGREDIENT_CODE, INGREDIENT_NAME_KOR, INGREDIENT_NAME_ENG, DATA_SOURCE)
             VALUES (:1, :2, :3, :4)"""

    seen = set()
    success = 0
    for row in tqdm(df.itertuples(), total=len(df), desc="성분마스터"):
        name = safe_str(getattr(row, 'mtral_nm', None), 200)
        if not name or name in seen:
            continue
        seen.add(name)
        try:
            cursor.execute(sql, (
                name[:20],  # code 대신 성분명 앞20자
                name,
                safe_str(getattr(row, 'main_ingr_eng', None), 200),
                'DUR',
            ))
            success += 1
        except Exception:
            pass

    conn.commit()
    cursor.close()
    print(f"  ✅ {success}건 적재 완료")


# ============================================================
# 7. REF_DUR_ITEM_WARNING (품목 DUR 경고)
# ============================================================
def load_dur_item_warning(conn):
    print("\n[7/8] REF_DUR_ITEM_WARNING 적재 중...")
    paths = glob.glob("data/processed/dur_item/*.parquet")
    if not paths:
        print("  파일 없음"); return

    cursor = conn.cursor()
    delete_all(cursor, "REF_DUR_ITEM_WARNING")
    conn.commit()

    sql = """INSERT INTO REF_DUR_ITEM_WARNING
             (ITEM_SEQ, TYPE_NAME, PROHBT_CONTENT, MIX_ITEM_SEQ, GRADE, NOTIFICATION_DATE)
             VALUES (:1, :2, :3, :4, :5, :6)"""

    total = 0
    for path in sorted(paths):
        df = pd.read_parquet(path)
        type_name = os.path.basename(path).replace('dur_item_', '').replace('_clean.parquet', '')
        print(f"  {os.path.basename(path)}: {list(df.columns)}, 행={len(df)}")

        success = 0
        for row in tqdm(df.itertuples(), total=len(df), desc=type_name[:20]):
            item_seq = safe_str(getattr(row, 'item_seq', None) or getattr(row, 'ITEM_SEQ', None), 20)
            if not item_seq:
                continue
            try:
                cursor.execute(sql, (
                    item_seq,
                    safe_str(getattr(row, 'type_name', None) or type_name, 50),
                    safe_str(getattr(row, 'prohbt_content', None) or getattr(row, 'mix_prohbt_content', None)),
                    safe_str(getattr(row, 'mix_item_seq', None) or getattr(row, 'mixture_item_seq', None), 20),
                    safe_str(getattr(row, 'grade', None), 10),
                    safe_str(getattr(row, 'notification_date', None), 20),
                ))
                success += 1
            except Exception:
                pass

        conn.commit()
        total += success

    cursor.close()
    print(f"  ✅ 총 {total}건 적재 완료")


# ============================================================
# 8. REF_DUR_INGREDIENT_WARNING (성분 DUR 경고)
# ============================================================
def load_dur_ingredient_warning(conn):
    print("\n[8/8] REF_DUR_INGREDIENT_WARNING 적재 중...")
    paths = glob.glob("data/processed/dur_ingredient/*.parquet")
    if not paths:
        print("  파일 없음"); return

    cursor = conn.cursor()
    delete_all(cursor, "REF_DUR_INGREDIENT_WARNING")
    conn.commit()

    sql = """INSERT INTO REF_DUR_INGREDIENT_WARNING
             (INGREDIENT_CODE, TYPE_NAME, PROHBT_CONTENT, MIX_INGR_CODE, GRADE, NOTIFICATION_DATE)
             VALUES (:1, :2, :3, :4, :5, :6)"""

    total = 0
    for path in sorted(paths):
        df = pd.read_parquet(path)
        type_name = os.path.basename(path).replace('dur_ingredient_', '').replace('_clean.parquet', '')
        print(f"  {os.path.basename(path)}: {list(df.columns)}, 행={len(df)}")

        success = 0
        for row in tqdm(df.itertuples(), total=len(df), desc=type_name[:20]):
            ingr_code = safe_str(getattr(row, 'ingr_code', None) or getattr(row, 'ingredient_code', None), 20)
            if not ingr_code:
                continue

            # REFERENCE_INGREDIENT에 없으면 자동 추가
            try:
                cursor.execute("""
                    INSERT INTO REFERENCE_INGREDIENT (INGREDIENT_CODE, INGREDIENT_NAME_KOR, DATA_SOURCE)
                    SELECT :1, :2, 'DUR' FROM DUAL
                    WHERE NOT EXISTS (SELECT 1 FROM REFERENCE_INGREDIENT WHERE INGREDIENT_CODE = :1)
                """, [ingr_code, safe_str(getattr(row, 'ingr_name', None), 200)])
            except:
                pass

            try:
                cursor.execute(sql, (
                    ingr_code,
                    safe_str(getattr(row, 'type_name', None) or type_name, 50),
                    safe_str(getattr(row, 'prohbt_content', None) or getattr(row, 'mix_prohbt_content', None)),
                    safe_str(getattr(row, 'mix_ingr_code', None) or getattr(row, 'mixture_ingr_code', None), 20),
                    safe_str(getattr(row, 'grade', None), 10),
                    safe_str(getattr(row, 'notification_date', None), 20),
                ))
                success += 1
            except Exception:
                pass

        conn.commit()
        total += success

    cursor.close()
    print(f"  ✅ 총 {total}건 적재 완료")


# ============================================================
# 메인 실행
# ============================================================
if __name__ == "__main__":
    conn = get_connection()
    print("DB 연결 성공")

    # load_permit_list(conn)
    # load_permit_detail(conn)
    # load_drug_ingredient(conn)
    # load_drug_overview(conn)
    load_pill_image_feature(conn)
    # load_reference_ingredient(conn)
    # load_dur_item_warning(conn)
    load_dur_ingredient_warning(conn)

    conn.close()
    print("완료!")
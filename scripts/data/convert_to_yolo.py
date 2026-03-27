"""
COCO JSON → YOLO 포맷 변환 스크립트
- Training/Validation 라벨링 JSON을 YOLO txt 포맷으로 변환
- 멀티프로세싱으로 빠르게 처리
- 중단 시 이어서 실행 가능

YOLO 포맷:
  <class_id> <cx> <cy> <w> <h>  (모두 0~1 정규화)

실행:
  python convert_to_yolo.py
"""

import os
import json
import shutil
from pathlib import Path
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

# =============================================================
# 경로 설정
# =============================================================
BASE = Path("/data/166.약품식별_인공지능_개발을_위한_경구약제_이미지_데이터/01.데이터")

TRAIN_IMG_BASE = BASE / "1.Training/원천데이터/단일경구약제_5000종"
VAL_IMG_BASE   = BASE / "2.Validation/원천데이터/단일경구약제_5000종"
TRAIN_LBL_BASE = BASE / "1.Training/라벨링데이터/단일경구약제_5000종"
VAL_LBL_BASE   = BASE / "2.Validation/라벨링데이터/단일경구약제_5000종"

OUTPUT_BASE  = Path("/data/yolo_dataset")
TRAIN_IMG_OUT = OUTPUT_BASE / "images/train"
TRAIN_LBL_OUT = OUTPUT_BASE / "labels/train"
VAL_IMG_OUT   = OUTPUT_BASE / "images/val"
VAL_LBL_OUT   = OUTPUT_BASE / "labels/val"

DONE_FILE      = OUTPUT_BASE / "convert_done.txt"
CLASS_MAP_FILE = OUTPUT_BASE / "class_map.json"
LOG_FILE       = OUTPUT_BASE / "convert_log.txt"

CLASS_MAP = {}


# =============================================================
# 클래스 맵 생성 (약 코드 → class_id)
# =============================================================
def build_class_map():
    print("클래스 맵 생성 중...")
    drug_codes = set()

    for ts_folder in sorted(TRAIN_IMG_BASE.iterdir()):
        if not ts_folder.is_dir():
            continue
        for drug_folder in ts_folder.iterdir():
            if drug_folder.is_dir():
                drug_codes.add(drug_folder.name)

    class_map = {code: idx for idx, code in enumerate(sorted(drug_codes))}
    print(f"  총 클래스 수: {len(class_map)}")

    with open(CLASS_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(class_map, f, ensure_ascii=False, indent=2)

    print(f"  저장: {CLASS_MAP_FILE}")
    return class_map


# =============================================================
# JSON 하나 변환
# =============================================================
def convert_json(args):
    json_path, img_src_path, img_out_dir, lbl_out_dir, class_map, done_set = args

    json_path = Path(json_path)
    img_src   = Path(img_src_path)
    img_out   = Path(img_out_dir)
    lbl_out   = Path(lbl_out_dir)
    stem      = json_path.stem

    # 이미 완료된 파일 건너뜀
    if stem in done_set:
        return "skip"

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        img_info    = data["images"][0]
        annotations = data["annotations"]
        img_w       = img_info["width"]
        img_h       = img_info["height"]
        drug_code   = img_info["drug_N"]
        file_name   = img_info["file_name"]

        # 클래스 ID
        class_id = class_map.get(drug_code, -1)
        if class_id == -1:
            return f"error:no_class:{stem}"

        # 이미지 복사
        src_img = img_src / file_name
        dst_img = img_out / file_name
        if not dst_img.exists() and src_img.exists():
            shutil.copy2(src_img, dst_img)

        # YOLO 라벨 생성
        yolo_lines = []
        for ann in annotations:
            x, y, w, h = ann["bbox"]  # COCO [x, y, w, h]

            # YOLO 포맷 변환 (중심점 + 정규화)
            cx = (x + w / 2) / img_w
            cy = (y + h / 2) / img_h
            nw = w / img_w
            nh = h / img_h

            # 범위 클리핑 (0~1)
            cx = max(0.0, min(1.0, cx))
            cy = max(0.0, min(1.0, cy))
            nw = max(0.0, min(1.0, nw))
            nh = max(0.0, min(1.0, nh))

            yolo_lines.append(f"{class_id} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")

        # txt 저장
        lbl_file = lbl_out / (Path(file_name).stem + ".txt")
        with open(lbl_file, "w") as f:
            f.write("\n".join(yolo_lines))

        return stem

    except Exception as e:
        return f"error:{stem}:{str(e)}"


# =============================================================
# 데이터셋 변환 실행
# =============================================================
def convert_dataset(img_base, lbl_base, img_out, lbl_out, split_name):
    print(f"\n{'='*50}")
    print(f"{split_name} 변환 시작")
    print(f"{'='*50}")

    img_out.mkdir(parents=True, exist_ok=True)
    lbl_out.mkdir(parents=True, exist_ok=True)

    # 완료 목록 로드
    done_set = set()
    if DONE_FILE.exists():
        with open(DONE_FILE, "r") as f:
            done_set = set(f.read().splitlines())

    # JSON 파일 목록 수집
    args_list = []
    for ts_folder in sorted(lbl_base.iterdir()):
        if not ts_folder.is_dir():
            continue

        ts_name     = ts_folder.name
        ts_img_name = ts_name.replace("TL_", "TS_").replace("VL_", "VS_")
        img_ts_folder = img_base / ts_img_name

        for drug_json_folder in ts_folder.iterdir():
            if not drug_json_folder.is_dir():
                continue

            drug_code      = drug_json_folder.name.replace("_json", "")
            img_drug_folder = img_ts_folder / drug_code

            for json_file in drug_json_folder.glob("*.json"):
                args_list.append((
                    str(json_file),
                    str(img_drug_folder),
                    str(img_out),
                    str(lbl_out),
                    CLASS_MAP,
                    done_set
                ))

    total  = len(args_list)
    remain = sum(1 for a in args_list if Path(a[0]).stem not in done_set)
    print(f"전체: {total}개 / 남은 작업: {remain}개")

    if remain == 0:
        print("이미 모두 완료됐어요!")
        return

    cores = min(cpu_count(), 30)
    print(f"병렬 코어: {cores}개")

    done_count  = 0
    error_count = 0

    with Pool(cores) as pool:
        for result in tqdm(pool.imap_unordered(convert_json, args_list), total=total, desc=split_name):
            if result == "skip":
                continue
            elif result.startswith("error"):
                error_count += 1
                with open(LOG_FILE, "a") as f:
                    f.write(result + "\n")
            else:
                done_count += 1
                with open(DONE_FILE, "a") as f:
                    f.write(result + "\n")

    print(f"\n완료: {done_count}개 / 오류: {error_count}개")


# =============================================================
# YAML 파일 생성
# =============================================================
def create_yaml():
    yaml_path  = OUTPUT_BASE / "dataset.yaml"
    class_names = [k for k, v in sorted(CLASS_MAP.items(), key=lambda x: x[1])]

    content = f"""# MediLink YOLO 데이터셋
path: {OUTPUT_BASE}
train: images/train
val: images/val

nc: {len(class_names)}
names: {class_names}
"""
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\nYAML 저장: {yaml_path}")
    print("\n학습 시작 명령어:")
    print(f"  yolo detect train data={yaml_path} model=yolov8m.pt epochs=100 imgsz=640")


# =============================================================
# 메인
# =============================================================
if __name__ == "__main__":
    import time
    start = time.time()

    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)

    # 1. 클래스 맵 생성 또는 로드
    if CLASS_MAP_FILE.exists():
        print(f"기존 클래스 맵 로드: {CLASS_MAP_FILE}")
        with open(CLASS_MAP_FILE, "r") as f:
            CLASS_MAP.update(json.load(f))
    else:
        CLASS_MAP.update(build_class_map())

    print(f"총 클래스 수: {len(CLASS_MAP)}")

    # 2. Training 변환
    convert_dataset(
        img_base   = TRAIN_IMG_BASE,
        lbl_base   = TRAIN_LBL_BASE,
        img_out    = TRAIN_IMG_OUT,
        lbl_out    = TRAIN_LBL_OUT,
        split_name = "Training"
    )

    # 3. Validation 변환
    convert_dataset(
        img_base   = VAL_IMG_BASE,
        lbl_base   = VAL_LBL_BASE,
        img_out    = VAL_IMG_OUT,
        lbl_out    = VAL_LBL_OUT,
        split_name = "Validation"
    )

    # 4. YAML 생성
    create_yaml()

    elapsed = time.time() - start
    print(f"\n{'='*50}")
    print(f"전체 완료! 소요 시간: {elapsed/3600:.1f}시간")
    print(f"출력 경로: {OUTPUT_BASE}")
    print(f"{'='*50}")

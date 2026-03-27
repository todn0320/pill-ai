#!/bin/bash
# =============================================================
# MediLink 이미지 데이터 압축 해제 스크립트 v2
# - 32코어 병렬 처리 (PARALLEL=30 권장)
# - 중단 시 이어서 실행 (.done 마커 방식)
# - 실패 시 자동 재시도 가능
# - 진행 상황 실시간 확인 가능
# =============================================================

PARALLEL=30
DONE_DIR="/data/unzip_done"
LOG="/data/unzip_progress.log"
DATA_BASE="/data/166.약품식별_인공지능_개발을_위한_경구약제_이미지_데이터/01.데이터"

mkdir -p "$DONE_DIR"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG"
}

# =============================================================
# 핵심 함수: 압축 해제 (이어서 실행 지원)
# =============================================================
do_unzip() {
  local zip_path="$1"
  local zip_file=$(basename "$zip_path")
  local folder_name="${zip_file%.zip}"
  local dir_name=$(dirname "$zip_path")
  local output_dir="$dir_name/$folder_name"
  local done_marker="$DONE_DIR/${folder_name}.done"

  # 이미 완료된 항목이면 건너뜀
  if [ -f "$done_marker" ]; then
    echo "⏭️  건너뜀: $folder_name"
    return 0
  fi

  echo "📂 압축 해제 시작: $folder_name"
  mkdir -p "$output_dir"

  # 7z로 압축 해제
  if 7z x "$zip_path" -o"$output_dir" -aoa > /dev/null 2>&1; then
    touch "$done_marker"
    echo "✅ 완료: $folder_name"
  else
    echo "❌ 실패: $folder_name" | tee -a "$LOG"
    rm -rf "$output_dir"   # 실패 시 삭제 → 다음 실행 시 재시도
    return 1
  fi
}

export -f do_unzip
export DONE_DIR LOG

# =============================================================
# 7z 설치 확인
# =============================================================
if ! command -v 7z &> /dev/null; then
  log "7z 없음 → 설치 중..."
  sudo apt-get install -y p7zip-full >> "$LOG" 2>&1
  log "7z 설치 완료"
fi

# =============================================================
# 시작 요약
# =============================================================
TOTAL=$(find "$DATA_BASE" -name "*.zip" | wc -l)
DONE=$(ls "$DONE_DIR"/*.done 2>/dev/null | wc -l)
REMAIN=$((TOTAL - DONE))

log "=============================="
log "전체 zip 파일: ${TOTAL}개"
log "이미 완료:     ${DONE}개"
log "남은 작업:     ${REMAIN}개"
log "병렬 코어:     ${PARALLEL}개"
log "=============================="

if [ "$REMAIN" -eq 0 ]; then
  log "모든 파일이 이미 압축 해제됐어요!"
  exit 0
fi

# =============================================================
# 전체 zip 파일 병렬 압축 해제
# =============================================================
log "=== 압축 해제 시작 ==="

find "$DATA_BASE" -name "*.zip" | \
  xargs -P "$PARALLEL" -I {} bash -c 'do_unzip "$@"' _ {}

log "=== 전체 압축 해제 완료 ==="

# =============================================================
# 최종 결과 요약
# =============================================================
DONE_FINAL=$(ls "$DONE_DIR"/*.done 2>/dev/null | wc -l)
FAIL=$((TOTAL - DONE_FINAL))

log "=============================="
log "완료: ${DONE_FINAL}개 / 전체: ${TOTAL}개"
if [ "$FAIL" -gt 0 ]; then
  log "실패: ${FAIL}개 → 스크립트 재실행 시 자동 재시도"
fi
log "=============================="
log "압축 해제된 폴더 수:"
log "  Training 이미지: $(ls $DATA_BASE/1.Training/원천데이터/단일경구약제_5000종/ | grep -v .zip | wc -l)"
log "  Training 라벨링: $(ls $DATA_BASE/1.Training/라벨링데이터/단일경구약제_5000종/ | grep -v .zip | wc -l)"
log "  Validation 이미지: $(ls $DATA_BASE/2.Validation/원천데이터/단일경구약제_5000종/ 2>/dev/null | grep -v .zip | wc -l)"
log "  Validation 라벨링: $(ls $DATA_BASE/2.Validation/라벨링데이터/단일경구약제_5000종/ 2>/dev/null | grep -v .zip | wc -l)"
log "=============================="

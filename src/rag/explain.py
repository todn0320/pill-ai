def safe_text(value):
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

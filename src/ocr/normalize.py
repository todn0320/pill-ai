def normalize_imprint(text: str) -> str:
    if not text:
        return ""
    return text.upper().replace("-", "").replace(" ", "").replace("_", "")

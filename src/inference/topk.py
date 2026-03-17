# topk 후처리 유틸
def filter_topk_by_threshold(topk: list, threshold: float = 0.01) -> list:
    return [x for x in topk if x["score"] >= threshold]

import os
import json
import torch
from src.inference.model_loader import load_model
from src.inference.preprocess import preprocess_image

MODEL_PATH = os.path.join("models", "best", "pill_cls_best.pt")
LABEL_MAP_PATH = os.path.join("models", "best", "label_map.json")

def load_label_map(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_class_to_item_seq(label_map: dict):
    if not label_map:
        return {}
    if "idx_to_class" in label_map:
        return {int(k): str(v) for k, v in label_map["idx_to_class"].items()}
    if "class_to_idx" in label_map:
        return {int(v): str(k) for k, v in label_map["class_to_idx"].items()}
    sample_val = label_map[next(iter(label_map.keys()))]
    if isinstance(sample_val, int):
        return {int(v): str(k) for k, v in label_map.items()}
    return {int(k): str(v) for k, v in label_map.items()}

def predict_topk(image_path: str, k: int = 5):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"입력 이미지 없음: {image_path}")
    label_map = load_label_map(LABEL_MAP_PATH)
    class_to_item_seq = build_class_to_item_seq(label_map)
    model, device = load_model(MODEL_PATH, num_classes=len(class_to_item_seq))
    image_tensor = preprocess_image(image_path).to(device)
    with torch.no_grad():
        probs = torch.softmax(model(image_tensor), dim=1)
        top_probs, top_indices = torch.topk(probs, k=min(k, len(class_to_item_seq)), dim=1)
    return [
        {"item_seq": class_to_item_seq.get(idx, f"unknown_{idx}"), "score": round(float(score), 4)}
        for idx, score in zip(top_indices.squeeze(0).cpu().tolist(), top_probs.squeeze(0).cpu().tolist())
    ]

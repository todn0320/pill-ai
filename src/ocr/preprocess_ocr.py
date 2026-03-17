import cv2

def resize_if_needed(image, max_side=1280):
    h, w = image.shape[:2]
    if max(h, w) <= max_side:
        return image
    scale = max_side / max(h, w)
    return cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

def generate_ocr_variants(image_path: str):
    img = cv2.imread(image_path)
    if img is None:
        return []
    img = resize_if_needed(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    enlarged = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    h, w = img.shape[:2]
    crop = img[int(h*0.2):int(h*0.8), int(w*0.2):int(w*0.8)]
    return [
        ("original", img),
        ("gray", gray),
        ("threshold", thresh),
        ("enlarged_gray", enlarged),
        ("center_crop", crop),
    ]

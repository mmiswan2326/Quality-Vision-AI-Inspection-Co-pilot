from PIL import Image
import numpy as np
import cv2

def predict_visual_defect(uploaded_image):

    image = Image.open(uploaded_image).convert("RGB")
    arr = np.array(image)

    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

    edges = cv2.Canny(gray, 100, 200)

    edge_density = np.sum(edges > 0) / edges.size

    brightness = gray.mean()

    score = (
        edge_density * 0.7
        + (1 - brightness / 255) * 0.3
    )

    score = min(max(score, 0), 1)

    confidence = min(95, max(70, int(score * 100)))

    if score >= 0.75:
        label = "Critical Defect"
    elif score >= 0.50:
        label = "Major Defect"
    elif score >= 0.25:
        label = "Minor Defect"
    else:
        label = "No / Low Visible Defect"

    return {
        "defect_label": label,
        "visual_defect_score": round(score, 2),
        "confidence": confidence,
        "image": image,
    }
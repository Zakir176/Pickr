from fastapi import FastAPI, UploadFile, File
from typing import List
import cv2
import numpy as np
try:
    import backend.analysis as analysis
except ModuleNotFoundError:
    import analysis

app = FastAPI()

# --- Constants for Normalization ---
MAX_BLUR_THRESHOLD = 500.0
IDEAL_EXPOSURE = 127.5
IDEAL_CONTRAST = 60.0       # Standard deviation of ~60 is good contrast
IDEAL_COLORFULNESS = 40.0   # Hasler metric around 40 is vibrant

# --- Constants for Scoring ---
BLUR_WEIGHT = 0.4
EXPOSURE_WEIGHT = 0.3
CONTRAST_WEIGHT = 0.2
COLOR_WEIGHT = 0.1

# --- Constants for Recommendations ---
KEEP_THRESHOLD = 0.75
REVIEW_THRESHOLD = 0.50

def normalize_simple(value, max_val):
    return min(float(value) / max_val, 1.0)

def calculate_final_exposure_score(stats):
    """
    Combines mean brightness with clipping penalties.
    """
    mean_val = stats["mean_brightness"]
    dist_score = 1.0 - (abs(mean_val - IDEAL_EXPOSURE) / IDEAL_EXPOSURE)
    
    # Penalize if too much clipping
    clipping_penalty = max(stats["shadow_clip_ratio"], stats["highlight_clip_ratio"])
    
    # If clipping is > 20%, heavily penalize
    if clipping_penalty > 0.2:
        dist_score *= 0.5
        
    return max(dist_score, 0.0)

def get_recommendation(final_score: float) -> str:
    if final_score >= KEEP_THRESHOLD:
        return "Keep"
    elif final_score >= REVIEW_THRESHOLD:
        return "Review"
    else:
        return "Delete"

@app.post("/analyze")
async def analyze_images(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        try:
            contents = await file.read()
            nparr = np.frombuffer(contents, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                raise ValueError("Invalid image file")

            # --- 1. Grayscale & Faces ---
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = analysis.detect_faces(gray)

            # --- 2. Calculate Metrics ---
            blur_raw, used_faces = analysis.calculate_blur(gray, faces)
            exposure_stats = analysis.calculate_exposure_stats(gray)
            contrast_raw = analysis.calculate_contrast(gray)
            color_raw = analysis.calculate_colorfulness(img)
            
            # --- 3. Normalize ---
            
            # Blur: If faces were found, we are more lenient with threshold as we are checking a smaller sharp area
            # But actually, face variance is usually higher if sharp.
            norm_blur = normalize_simple(blur_raw, MAX_BLUR_THRESHOLD)
            
            # Exposure
            norm_exposure = calculate_final_exposure_score(exposure_stats)
            
            # Contrast
            norm_contrast = normalize_simple(contrast_raw, IDEAL_CONTRAST)
            
            # Color
            norm_color = normalize_simple(color_raw, IDEAL_COLORFULNESS)

            # --- 4. Final Score ---
            final_score = (
                (norm_blur * BLUR_WEIGHT) +
                (norm_exposure * EXPOSURE_WEIGHT) +
                (norm_contrast * CONTRAST_WEIGHT) +
                (norm_color * COLOR_WEIGHT)
            )

            # --- 5. Recommendation ---
            recommendation = get_recommendation(final_score)
            
            results.append({
                "filename": file.filename,
                "score_components": {
                    "blur": round(norm_blur, 2),
                    "exposure": round(norm_exposure, 2),
                    "contrast": round(norm_contrast, 2),
                    "color": round(norm_color, 2)
                },
                "metrics_raw": {
                    "blur_var": round(float(blur_raw), 2),
                    "faces_detected": int(len(faces)) if faces is not None else 0,
                    "mean_brightness": round(float(exposure_stats["mean_brightness"]), 2),
                    "shadow_clip": round(float(exposure_stats["shadow_clip_ratio"]), 3),
                    "highlight_clip": round(float(exposure_stats["highlight_clip_ratio"]), 3),
                    "contrast_std": round(float(contrast_raw), 2),
                    "color_metric": round(float(color_raw), 2)
                },
                "final_score": round(final_score, 2),
                "recommendation": recommendation
            })

        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })

    return {"analysis_results": results}

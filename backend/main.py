from fastapi import FastAPI, UploadFile, File
from typing import List
import cv2
import numpy as np

app = FastAPI()

# --- Constants for Normalization ---
MAX_BLUR_THRESHOLD = 500.0  # Laplacian variance threshold, above this is considered sharp
IDEAL_EXPOSURE = 127.5      # Ideal middle gray value (0-255)

# --- Constants for Scoring ---
BLUR_WEIGHT = 0.6
EXPOSURE_WEIGHT = 0.4

# --- Constants for Recommendations ---
KEEP_THRESHOLD = 0.8    # Above this score, recommend 'Keep'
REVIEW_THRESHOLD = 0.5  # Above this score, recommend 'Review'; otherwise 'Delete'

def normalize_blur(laplacian_var: float) -> float:
    """Normalizes the blur score. 1.0 is sharp, 0.0 is very blurry."""
    return min(laplacian_var / MAX_BLUR_THRESHOLD, 1.0)

def normalize_exposure(mean_pixel_value: float) -> float:
    """
    Normalizes the exposure. 1.0 is ideally exposed, 0.0 is black or white.
    The score is based on the distance from the ideal mid-gray value.
    """
    normalized_distance = abs(mean_pixel_value - IDEAL_EXPOSURE) / IDEAL_EXPOSURE
    return max(1.0 - normalized_distance, 0.0)

def get_recommendation(final_score: float) -> str:
    """Provides a Keep/Review/Delete recommendation based on the final score."""
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
            # Read file content into memory
            contents = await file.read()
            
            # Decode image from memory
            nparr = np.frombuffer(contents, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                raise ValueError("Invalid image file")

            # --- Calculations ---
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            exposure = float(np.mean(gray))

            # --- Normalization ---
            norm_blur = normalize_blur(laplacian_var)
            norm_exposure = normalize_exposure(exposure)

            # --- Final Score Calculation ---
            final_score = (norm_blur * BLUR_WEIGHT) + (norm_exposure * EXPOSURE_WEIGHT)

            # --- Recommendation ---
            recommendation = get_recommendation(final_score)
            
            results.append({
                "filename": file.filename,
                "blur_score_raw": round(laplacian_var, 2),
                "exposure_score_raw": round(exposure, 2),
                "normalized_blur_score": round(norm_blur, 2),
                "normalized_exposure_score": round(norm_exposure, 2),
                "final_score": round(final_score, 2),
                "recommendation": recommendation
            })

        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })

    return {"analysis_results": results}

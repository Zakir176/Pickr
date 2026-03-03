from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import cv2
import numpy as np
import io
import json
import asyncio
from concurrent.futures import ProcessPoolExecutor
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()  # Enable HEIC support in Pillow

try:
    import backend.analysis as analysis
except ModuleNotFoundError:
    import analysis

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a process pool for CPU-bound image analysis
executor = ProcessPoolExecutor()


@app.on_event("shutdown")
def shutdown_event():
    executor.shutdown()

# --- Constants for Normalization ---
MAX_BLUR_THRESHOLD = 500.0
IDEAL_EXPOSURE = 127.5
IDEAL_CONTRAST = 60.0
IDEAL_COLORFULNESS = 40.0

# --- Constants for Recommendations ---
KEEP_THRESHOLD = 0.75
REVIEW_THRESHOLD = 0.50

# --- Scoring Configuration ---
DEFAULT_SCORING_WEIGHTS = {"blur": 0.4, "exposure": 0.3, "contrast": 0.2, "color": 0.1}


def normalize_simple(value, max_val):
    return min(float(value) / max_val, 1.0)


def calculate_final_exposure_score(stats):
    mean_val = stats["mean_brightness"]
    dist_score = 1.0 - (abs(mean_val - IDEAL_EXPOSURE) / IDEAL_EXPOSURE)
    clipping_penalty = max(stats["shadow_clip_ratio"], stats["highlight_clip_ratio"])
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


def analyze_single_image(filename, contents, weights=None):
    """
    Perform CPU-bound analysis on a single image.
    This function is designed to run in a separate process.
    """
    if weights is None:
        weights = DEFAULT_SCORING_WEIGHTS

    try:
        # --- HEIC & Format Handling ---
        pil_img = Image.open(io.BytesIO(contents))
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")

        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        if img is None:
            raise ValueError(f"Could not decode image '{filename}'.")

        # --- 1. Grayscale & Faces ---
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = analysis.detect_faces(gray)

        # --- 2. Calculate Metrics ---
        blur_raw, used_faces = analysis.calculate_blur(gray, faces)
        exposure_stats = analysis.calculate_exposure_stats(gray)
        contrast_raw = analysis.calculate_contrast(gray)
        color_raw = analysis.calculate_colorfulness(img)
        phash = analysis.calculate_phash(img)

        # --- 3. Normalize ---
        norm_blur = normalize_simple(blur_raw, MAX_BLUR_THRESHOLD)
        norm_exposure = calculate_final_exposure_score(exposure_stats)
        norm_contrast = normalize_simple(contrast_raw, IDEAL_CONTRAST)
        norm_color = normalize_simple(color_raw, IDEAL_COLORFULNESS)

        # --- 4. Final Score ---
        final_score = (
            (norm_blur * weights.get("blur", 0.4))
            + (norm_exposure * weights.get("exposure", 0.3))
            + (norm_contrast * weights.get("contrast", 0.2))
            + (norm_color * weights.get("color", 0.1))
        )

        # --- 5. Recommendation ---
        recommendation = get_recommendation(final_score)

        # Get original image dimensions for face box scaling
        h, w = gray.shape

        return {
            "filename": filename,
            "phash": phash,
            "dimensions": {"width": w, "height": h},
            "faces": [
                {"x": int(x), "y": int(y), "w": int(w_f), "h": int(h_f)} 
                for (x, y, w_f, h_f) in faces
            ] if faces is not None else [],
            "score_components": {
                "blur": round(norm_blur, 2),
                "exposure": round(norm_exposure, 2),
                "contrast": round(norm_contrast, 2),
                "color": round(norm_color, 2),
            },
            "metrics_raw": {
                "blur_var": round(float(blur_raw), 2),
                "faces_detected": int(len(faces)) if faces is not None else 0,
                "mean_brightness": round(float(exposure_stats["mean_brightness"]), 2),
                "contrast_std": round(float(contrast_raw), 2),
                "color_metric": round(float(color_raw), 2),
            },
            "final_score": round(final_score, 2),
            "recommendation": recommendation,
        }

    except Exception as e:
        return {
            "filename": filename,
            "error": str(e),
            "phash": "0000000000000000",
            "final_score": 0.0,
            "recommendation": "Review",
        }


@app.post("/analyze")
async def analyze_images(
    files: List[UploadFile] = File(...),
    weights: Optional[str] = Form(None)
):
    loop = asyncio.get_event_loop()
    tasks = []

    # Parse weights if provided
    scoring_weights = DEFAULT_SCORING_WEIGHTS
    if weights:
        try:
            scoring_weights = json.loads(weights)
        except Exception:
            pass

    for file in files:
        contents = await file.read()
        # Offload CPU-bound task to process pool
        tasks.append(
            loop.run_in_executor(executor, analyze_single_image, file.filename, contents, scoring_weights)
        )

    # Wait for all analysis tasks to complete
    raw_results = await asyncio.gather(*tasks)

    # --- 6. Clustering ---
    grouped_results = analysis.cluster_results(raw_results)

    return {"analysis_results": grouped_results}


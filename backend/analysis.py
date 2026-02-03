import cv2
import numpy as np
import os

# Get path to Haar cascade file from OpenCV's data
face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(face_cascade_path)

def detect_faces(gray_img):
    """Detects faces in a grayscale image. Returns list of (x, y, w, h)."""
    faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return faces

def calculate_blur(gray_img, faces=None):
    """
    Calculates blur score.
    If faces are detected, focuses analysis on the face regions.
    Otherwise, uses global Laplacian variance.
    Returns: (raw_score, is_focused_on_face)
    """
    if faces is not None and len(faces) > 0:
        # If faces are present, calculate average variance of face regions
        variances = []
        for (x, y, w, h) in faces:
            # Extract face ROI
            roi = gray_img[y:y+h, x:x+w]
            var = cv2.Laplacian(roi, cv2.CV_64F).var()
            variances.append(var)
        
        # Take the maximum variance (sharpest face) as the score
        # We assume if at least one face is sharp, the photo is usable
        return max(variances), True
    else:
        # Global variance
        return cv2.Laplacian(gray_img, cv2.CV_64F).var(), False

def calculate_exposure_stats(gray_img):
    """
    Calculates advanced exposure metrics using histogram analysis.
    Returns dictionary with:
        - mean: Mean pixel value (0-255)
        - dynamic_range: Range between 1st and 99th percentile (0-255)
        - shadow_clip: % of pixels < 5
        - highlight_clip: % of pixels > 250
    """
    hist = cv2.calcHist([gray_img], [0], None, [256], [0, 256])
    total_pixels = gray_img.size
    
    # Shadow clipping (< 5)
    shadow_count = np.sum(hist[:5])
    shadow_clip_ratio = shadow_count / total_pixels
    
    # Highlight clipping (> 250)
    highlight_count = np.sum(hist[251:])
    highlight_clip_ratio = highlight_count / total_pixels
    
    # Dynamic Range (using percentiles)
    # This is a bit computationally expensive for very large images, so we can use a simpler approximation if needed
    # But for MVP, numpy percentiles on the flattened array is fine
    p1, p99 = np.percentile(gray_img, [1, 99])
    dynamic_range = p99 - p1
    
    return {
        "mean_brightness": np.mean(gray_img),
        "dynamic_range": dynamic_range,
        "shadow_clip_ratio": shadow_clip_ratio,
        "highlight_clip_ratio": highlight_clip_ratio
    }

def calculate_contrast(gray_img):
    """Calculates RMS contrast (Standard Deviation of pixel intensities)."""
    return float(np.std(gray_img))

def calculate_colorfulness(img_bgr):
    """
    Calculates Hasler & Süsstrunk colorfulness metric.
    rg = R - G
    yb = 0.5 * (R + G) - B
    std_root = sqrt(std(rg)^2 + std(yb)^2)
    mean_root = sqrt(mean(rg)^2 + mean(yb)^2)
    Metric = std_root + 0.3 * mean_root
    """
    B, G, R = cv2.split(img_bgr.astype("float"))
    rg = np.absolute(R - G)
    yb = np.absolute(0.5 * (R + G) - B)

    std_rg = np.std(rg)
    mean_rg = np.mean(rg)
    
    std_yb = np.std(yb)
    mean_yb = np.mean(yb)
    
    std_root = np.sqrt(std_rg**2 + std_yb**2)
    mean_root = np.sqrt(mean_rg**2 + mean_yb**2)
    
    return std_root + (0.3 * mean_root)

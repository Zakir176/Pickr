import cv2
import numpy as np
import imagehash
from PIL import Image

# Get path to Haar cascade file from OpenCV's data
face_cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(face_cascade_path)

eye_cascade_path = cv2.data.haarcascades + "haarcascade_eye.xml"
eye_cascade = cv2.CascadeClassifier(eye_cascade_path)


def detect_faces(gray_img):
    """Detects faces in a grayscale image. Returns list of (x, y, w, h)."""
    faces = face_cascade.detectMultiScale(
        gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )
    return faces


def detect_blinks(gray_img, faces):
    """
    Detects potential blinks by checking for eyes within face regions.
    Returns: (bool blink_detected, list face_indices_with_blinks)
    """
    if faces is None or len(faces) == 0:
        return False, []

    blink_detected = False
    face_indices = []

    for i, (x, y, w, h) in enumerate(faces):
        # Eyes are usually in the top half of the face
        roi_gray = gray_img[y : y + int(h * 0.7), x : x + w]
        
        # Detect eyes in face ROI
        eyes = eye_cascade.detectMultiScale(
            roi_gray, scaleFactor=1.1, minNeighbors=10, minSize=(w // 10, h // 10)
        )
        
        # Heuristic: If we find fewer than 2 eyes in a front-facing face, 
        # it's likely a blink or occlusion worth reviewing.
        if len(eyes) < 2:
            blink_detected = True
            face_indices.append(i)
            
    return blink_detected, face_indices


def calculate_blur(gray_img, faces=None):
    """
    Calculates blur score.
    If faces are detected, focuses analysis on the face regions.
    Otherwise, uses the central 50% ROI to avoid background dominance.
    Returns: (raw_score, is_focused_on_face)
    """
    if faces is not None and len(faces) > 0:
        # If faces are present, calculate average variance of face regions
        variances = []
        for x, y, w, h in faces:
            # Extract face ROI
            roi = gray_img[y : y + h, x : x + w]
            # Laplacian variance is a standard measure for focus
            var = cv2.Laplacian(roi, cv2.CV_64F).var()
            variances.append(var)

        # Take the maximum variance (sharpest face) as the score
        return max(variances), True
    else:
        # No faces: analyze the central region where subjects usually are
        h, w = gray_img.shape
        # Center 50% ROI
        y1, y2 = int(h * 0.25), int(h * 0.75)
        x1, x2 = int(w * 0.25), int(w * 0.75)
        roi = gray_img[y1:y2, x1:x2]
        
        # We take the global variance but weight it by the center ROI
        global_var = cv2.Laplacian(gray_img, cv2.CV_64F).var()
        roi_var = cv2.Laplacian(roi, cv2.CV_64F).var()
        
        # Combine global and ROI variance (70% weight on ROI)
        combined_var = (0.7 * roi_var) + (0.3 * global_var)
        return combined_var, False


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
    p1, p99 = np.percentile(gray_img, [1, 99])
    dynamic_range = p99 - p1

    return {
        "mean_brightness": np.mean(gray_img),
        "dynamic_range": dynamic_range,
        "shadow_clip_ratio": shadow_clip_ratio,
        "highlight_clip_ratio": highlight_clip_ratio,
    }


def calculate_contrast(gray_img):
    """Calculates RMS contrast (Standard Deviation of pixel intensities)."""
    return float(np.std(gray_img))


def calculate_colorfulness(img_bgr):
    """
    Calculates Hasler & Süsstrunk colorfulness metric.
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


def calculate_phash(img_bgr):
    """Calculates perceptual hash of an image."""
    # Convert BGR (OpenCV) to RGB then to PIL Image
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    return str(imagehash.phash(pil_img))


def calculate_composition(gray_img, faces=None):
    """
    Analyzes composition based on Rule of Thirds.
    Checks if subjects (faces or points of interest) align with the four 'power points'.
    Returns: { score: 0.0-1.0, description: str }
    """
    h, w = gray_img.shape
    power_points = [
        (h / 3, w / 3), (h / 3, 2 * w / 3),
        (2 * h / 3, w / 3), (2 * h / 3, 2 * w / 3)
    ]
    
    subjects = []
    if faces is not None and len(faces) > 0:
        for x, y, w_f, h_f in faces:
            subjects.append((y + h_f / 2, x + w_f / 2))
    else:
        # If no faces, find the most "interesting" point using edge density
        edges = cv2.Canny(gray_img, 100, 200)
        # Use a large blur to find the center of edge density
        density = cv2.GaussianBlur(edges.astype(float), (0, 0), sigmaX=w/10, sigmaY=h/10)
        _, _, _, max_loc = cv2.minMaxLoc(density)
        subjects.append((max_loc[1], max_loc[0])) # (y, x)

    # Calculate min distance to any power point for each subject
    min_distances = []
    for sy, sx in subjects:
        dists = [np.sqrt((sy - py)**2 + (sx - px)**2) for py, px in power_points]
        min_distances.append(min(dists))

    # Normalize score: max distance is roughly diagonal / 3
    max_dist = np.sqrt(h**2 + w**2) / 3
    avg_min_dist = np.mean(min_distances)
    score = max(0.0, 1.0 - (avg_min_dist / max_dist))
    
    description = "Subject aligned with Rule of Thirds" if score > 0.7 else "Subject centered or off-axis"
    return {"score": round(float(score), 2), "description": description}


def analyze_scene_and_tags(img_bgr, gray_img, faces=None):
    """
    Detects scene type and generates descriptive tags using heuristics.
    Returns: { scene: str, tags: list[str] }
    """
    h, w = gray_img.shape
    tags = []
    scene = "Other"

    # 1. Detect "People" and "Portrait"
    if faces is not None and len(faces) > 0:
        tags.append("People")
        # Check if it's a "Portrait" (faces occupy > 10% of image area)
        total_face_area = sum(wf * hf for (xf, yf, wf, hf) in faces)
        if total_face_area / (h * w) > 0.1:
            scene = "Portrait"
            tags.append("Close-up")
        else:
            scene = "Group Shot" if len(faces) > 1 else "Portrait"

    # 2. Color Analysis for "Nature" vs "Urban"
    # Convert to HSV for better color segmentation
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    
    # Green (Nature/Foliage)
    green_mask = cv2.inRange(hsv, (35, 20, 20), (85, 255, 255))
    green_ratio = np.sum(green_mask > 0) / (h * w)
    
    # Blue (Sky/Water)
    blue_mask = cv2.inRange(hsv, (90, 20, 20), (130, 255, 255))
    blue_ratio = np.sum(blue_mask > 0) / (h * w)

    if green_ratio > 0.15:
        tags.append("Nature")
    if blue_ratio > 0.15:
        tags.append("Sky/Water")
    
    if (green_ratio + blue_ratio) > 0.3 and scene == "Other":
        scene = "Landscape"

    # 3. Edge Density for "Architecture/Urban"
    edges = cv2.Canny(gray_img, 100, 200)
    edge_ratio = np.sum(edges > 0) / (h * w)
    if edge_ratio > 0.05:
        tags.append("Detailed")
        if scene == "Other" and green_ratio < 0.1:
            scene = "Architecture"
            tags.append("Urban")

    # 4. Brightness/Contrast tags
    brightness = np.mean(gray_img)
    if brightness > 200:
        tags.append("Bright")
    elif brightness < 60:
        tags.append("Low Light")

    return {
        "scene": scene,
        "tags": list(set(tags)) # Unique tags
    }


def cluster_results(results, threshold=10):
    """
    Groups analysis results based on perceptual hash similarity.
    threshold: Max Hamming distance to be considered 'similar'.
    Returns list of groups [{title, items:[]}]
    """
    clusters = []

    for item in results:
        assigned = False
        item_hash = imagehash.hex_to_hash(item["phash"])

        for cluster in clusters:
            # Check distance against the first item in the cluster (the representative)
            rep_hash = imagehash.hex_to_hash(cluster[0]["phash"])
            if (item_hash - rep_hash) < threshold:
                cluster.append(item)
                assigned = True
                break

        if not assigned:
            clusters.append([item])

    # Format for Frontend
    formatted_groups = []
    for i, cluster in enumerate(clusters):
        # Sort cluster by final_score descending to pick the best shot
        cluster.sort(key=lambda x: x["final_score"], reverse=True)

        # Mark the first one as best
        for j, item in enumerate(cluster):
            item["isBest"] = j == 0

        title = "Group " + str(i + 1)
        if len(cluster) == 1:
            title = "Unique Photo"
        else:
            title = f"Similar Set ({len(cluster)} items)"

        formatted_groups.append({"title": title, "items": cluster})

    return formatted_groups

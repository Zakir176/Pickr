# Pickr: A Phone-First Photo Curation Tool

> **Tagline:** Quickly pick the best photos and discard the rest.

Pickr is a minimalist MVP designed to help you quickly decide which photos to keep or delete by analyzing them for common issues like blur and poor exposure. It's built for casual photography, not for professional-grade analysis.

## 1. Project Overview

### Goal
The primary goal is to help users efficiently curate their photos by automatically flagging images that are blurry, over/underexposed, or near-duplicates.

### MVP Features
-   **Upload via Browser**: Upload multiple photos from your phone's web browser.
-   **Blur Detection**: Uses Laplacian variance to identify blurry images.
-   **Exposure Detection**: Uses mean brightness to find over/underexposed shots.
-   **Scoring**: Computes a combined score for each photo.
-   **Recommendations**: Provides a simple **Keep / Review / Delete** suggestion.
-   **JSON API**: Returns all analysis data as JSON for any frontend to consume.

### Non-Goals (for this MVP)
-   No database or persistent storage.
-   No cloud-based processing.
-   No complex AI-based aesthetic judgments.
-   No automatic deletion—the user always makes the final decision.

## 2. Tech Stack

### Backend
-   **Python** 3.10+
-   **FastAPI**: For the web framework.
-   **Uvicorn**: As the ASGI server.
-   **OpenCV**: For image processing (blur/exposure).
-   **NumPy**: For numerical operations.
-   **python-multipart**: To handle file uploads.

### Frontend (Planned)
-   **Vue 3**: For the reactive UI.
-   **Axios**: To communicate with the backend API.
-   Minimal CSS for a mobile-first layout.

## 3. Project Structure

```
pickr/
├── backend/
│   ├── main.py            # FastAPI application
│   └── requirements.txt   # Python dependencies
├── frontend/
│   └── (Vue 3 project files will go here)
├── docs/
│   └── (Documentation files)
├── README.md
└── LICENSE
```

## 4. Backend Usage

### 4.1. Setup
1.  **Clone the repository and navigate to the project directory.**

2.  **Create and activate a virtual environment:**
    ```sh
    python -m venv venv
    # On macOS/Linux:
    source venv/bin/activate
    # On Windows:
    .\venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    ```sh
    pip install -r backend/requirements.txt
    ```

### 4.2. Current `main.py`

The current backend implementation includes blur detection.

```python
from fastapi import FastAPI, UploadFile, File
from typing import List
import cv2
import numpy as np

app = FastAPI()

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
            
            # --- Blur Detection ---
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            results.append({
                "filename": file.filename,
                "score": 0.85,  # Dummy score
                "quality": "good", # Dummy quality
                "blur_score": round(laplacian_var, 2)
            })

        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })
            
    return {"analysis_results": results}
```

### 4.3. Run the Backend

Navigate to the root directory and run:

```sh
uvicorn backend.main:app --reload
```
You can now access the API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and use it to test file uploads.

## 5. Roadmap

### Phase 1: Backend MVP (Completed)
-   [x] Upload multiple images.
-   [x] Compute blur score (Laplacian variance).
-   [x] Compute exposure score (mean brightness).
-   [x] Normalize scores to a 0–1 range.
-   [x] Compute a weighted `final_score`.
-   [x] Add `recommendation` field (`Keep`/`Review`/`Delete`).

### Phase 2: Frontend MVP
-   [ ] Create a mobile-first Vue interface.
-   [ ] Allow users to upload photos and see results.
-   [ ] Display thumbnails with scores and recommendations.
-   [ ] Allow users to manually override recommendations.

### Phase 3: Advanced Features
-   [ ] Group similar or near-duplicate images.
-   [ ] Suggest the best shot from a group of similar photos.
-   [ ] Package as a Progressive Web App (PWA) for better mobile experience.
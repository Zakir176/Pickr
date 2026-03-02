import cv2
import numpy as np
from fastapi.testclient import TestClient
import os
import pytest

from backend.main import app

client = TestClient(app)
TEMP_DIR = "test_images_pytest"

@pytest.fixture(scope="session", autouse=True)
def setup_teardown():
    # Setup
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    
    yield
    
    # Teardown (optional, clean up test images)
    for f in os.listdir(TEMP_DIR):
        os.remove(os.path.join(TEMP_DIR, f))
    os.rmdir(TEMP_DIR)

def create_image(filename, method):
    img = np.zeros((500, 500, 3), dtype=np.uint8)
    
    if method == "solid_black":
        pass  # Already black
    elif method == "solid_white":
        img.fill(255)
    elif method == "solid_gray":
        img.fill(127)  # Ideal exposure
    elif method == "noise_sharp":
        # Random noise is very sharp (high laplacian variance)
        cv2.randn(img, (127, 127, 127), (50, 50, 50))
    elif method == "noise_blur":
        # Generate noise then blur it
        cv2.randn(img, (127, 127, 127), (50, 50, 50))
        img = cv2.GaussianBlur(img, (21, 21), 0)
        
    path = os.path.join(TEMP_DIR, filename)
    cv2.imwrite(path, img)
    return path

def test_analyze_images():
    files_to_test = [
        ("black.jpg", "solid_black"),
        ("gray.jpg", "solid_gray"),
        ("sharp.jpg", "noise_sharp"),
        ("blurry.jpg", "noise_blur"),
        ("dup1.jpg", "solid_gray"),
        ("dup2.jpg", "solid_gray"),
    ]
    
    files_payload = []
    file_handlers = []
    
    try:
        for fname, method in files_to_test:
            path = create_image(fname, method)
            f = open(path, 'rb')
            file_handlers.append(f)
            files_payload.append(('files', (fname, f, 'image/jpeg')))
            
        response = client.post("/analyze", files=files_payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "analysis_results" in data
        groups = data["analysis_results"]
        
        # Verify groups were created
        assert len(groups) > 0
        
        # Check flat items
        all_items = []
        for g in groups:
            all_items.extend(g["items"])
            
        assert len(all_items) == 6
        
        # Mapping for easier assertions
        results_by_name = {item["filename"]: item for item in all_items}
        
        # 1. Blur checks
        assert results_by_name["sharp.jpg"]["score_components"]["blur"] > results_by_name["blurry.jpg"]["score_components"]["blur"], "Sharp image should have higher blur score than blurry image"
        
        # 2. Exposure checks (Gray is ideal, Black is underexposed)
        # Note: score_components.exposure is normalized, higher is better
        assert results_by_name["gray.jpg"]["score_components"]["exposure"] > results_by_name["black.jpg"]["score_components"]["exposure"], "Gray image should have better exposure score than black image"
        
        # 3. Duplicate checks (dup1 and dup2 should likely be in the same group or have very close hashes)
        # Since gray.jpg is also solid_gray, all three might be in one group.
        # Let's verify they share the same phash.
        assert results_by_name["dup1.jpg"]["phash"] == results_by_name["dup2.jpg"]["phash"]
        assert results_by_name["dup1.jpg"]["phash"] == results_by_name["gray.jpg"]["phash"]

    finally:
        for f in file_handlers:
            f.close()

import cv2
import numpy as np
import requests
import os
import time
    
API_URL = "http://localhost:8002/analyze"
API_URL = "http://localhost:8000/analyze"
TEMP_DIR = "test_images"

def setup():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

def create_image(filename, method):
    img = np.zeros((500, 500, 3), dtype=np.uint8)
    
    if method == "solid_black":
        pass # Already black
    
    elif method == "solid_white":
        img.fill(255)
        
    elif method == "solid_gray":
        img.fill(127) # Ideal exposure
        
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

def test_backend():
    print("Generating test images...")
    files_to_test = [
        ("black.jpg", "solid_black", "Expect Low Exposure Score"),
        ("white.jpg", "solid_white", "Expect Low Exposure Score (Overexposed)"),
        ("gray.jpg", "solid_gray", "Expect High Exposure Score (Ideal)"),
        ("sharp.jpg", "noise_sharp", "Expect High Blur Score (Sharp)"),
        ("blurry.jpg", "noise_blur", "Expect Low Blur Score (Blurry)"),
    ]
    
    files_payload = []
    file_handlers = []
    
    try:
        for fname, method, desc in files_to_test:
            path = create_image(fname, method)
            f = open(path, 'rb')
            file_handlers.append(f)
            files_payload.append(('files', (fname, f, 'image/jpeg')))
            print(f"Created {fname}: {desc}")

        print("\nSending request to backend...")
        log_file = open("results.log", "w", encoding="utf-8")
        try:
            response = requests.post(API_URL, files=files_payload)
            if response.status_code == 200:
                results = response.json().get("analysis_results", [])
                print("\n--- Analysis Results ---")
                log_file.write("--- Analysis Results ---\n")
                for res in results:
                    metrics = res.get('metrics_raw', {})
                    scores = res.get('score_components', {})
                    
                    s = f"\nFile: {res['filename']}\n"
                    s += f"  Final Score: {res.get('final_score')}\n"
                    s += f"  Recommendation: {res.get('recommendation')}\n"
                    s += f"  Blur (Var): {metrics.get('blur_var')} (Score: {scores.get('blur')})\n"
                    s += f"  Faces: {metrics.get('faces_detected')}\n"
                    s += f"  Exposure (Mean): {metrics.get('mean_brightness')} (Score: {scores.get('exposure')})\n"
                    s += f"  Clipping: Shadow {metrics.get('shadow_clip')}, Highlight {metrics.get('highlight_clip')}\n"
                    s += f"  Contrast (Std): {metrics.get('contrast_std')} (Score: {scores.get('contrast')})\n"
                    s += f"  Color (Hasler): {metrics.get('color_metric')} (Score: {scores.get('color')})\n"
                    
                    print(s)
                    log_file.write(s)
            else:
                print(f"Error: Server returned {response.status_code}")
                # log_file.write(f"Error: Server returned {response.status_code}")
                print(response.text)
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to server. Is it running?")
        finally:
            log_file.close()

    finally:
        # Cleanup
        for f in file_handlers:
            f.close()
            
if __name__ == "__main__":
    setup()
    # Give server a moment if it just started
    time.sleep(2)
    test_backend()

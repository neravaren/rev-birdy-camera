import cv2
import requests
import time
import os
from ultralytics import YOLO

# Configuration
ESP32_CAMERA_URL = "http://10.2.1.143/capture"  # Change this to your ESP32 Camera URL
SAVE_DIR = "captured_birds"
BLUR_THRESHOLD = 100
CAPTURE_INTERVAL = 5  # Seconds

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Ensure save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

def capture_image():
    """Fetch image from ESP32 Camera."""
    try:
        response = requests.get(ESP32_CAMERA_URL, timeout=5)
        if response.status_code == 200:
            img_array = np.frombuffer(response.content, dtype=np.uint8)
            return cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        else:
            print("Failed to capture image.")
    except requests.RequestException as e:
        print(f"Error fetching image: {e}")
    return None

def is_blurred(image):
    """Check if the image is blurry using the Laplacian method."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance < BLUR_THRESHOLD

def contains_bird(image):
    """Check if the image contains a bird using YOLOv8."""
    results = model(image)
    for r in results:
        for box in r.boxes:
            if int(box.cls) == 16:  # COCO class ID for bird
                return True
    return False

def save_image(image):
    """Save image with timestamp."""
    filename = os.path.join(SAVE_DIR, f"bird_{int(time.time())}.jpg")
    cv2.imwrite(filename, image)
    print(f"Saved: {filename}")

def main():
    while True:
        image = capture_image()
        if image is not None:
            if not is_blurred(image) and contains_bird(image):
                save_image(image)
        time.sleep(CAPTURE_INTERVAL)

if __name__ == "__main__":
    main()

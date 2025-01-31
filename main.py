import cv2
import requests
import time
import os
import argparse
from datetime import datetime
from ultralytics import YOLO
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
ESP32_CAMERA_URL = os.getenv("ESP32_CAMERA_URL", "http://10.2.1.143/capture")
SAVE_DIR = os.getenv("SAVE_DIR", "captured_birds")
BLUR_THRESHOLD = int(os.getenv("BLUR_THRESHOLD", "100"))
CAPTURE_INTERVAL = int(os.getenv("CAPTURE_INTERVAL", "5"))
DISPLAY_WIDTH = int(os.getenv("DISPLAY_WIDTH", "800"))  # Width in pixels for display window

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
    results = model(image, verbose=False)
    for r in results:
        for box in r.boxes:
            if int(box.cls) == 16:  # COCO class ID for bird
                return True
    return False

def print_timed(message):
    """Print a message with timestamp prefix."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def resize_image(image, width):
    """Resize image maintaining aspect ratio."""
    height = int(image.shape[0] * (width / image.shape[1]))
    return cv2.resize(image, (width, height))

def save_image(image):
    """Save image with timestamp."""
    filename = os.path.join(SAVE_DIR, f"bird_{int(time.time())}.jpg")
    cv2.imwrite(filename, image)
    print(f"Saved: {filename}")

def main():
    parser = argparse.ArgumentParser(description='Bird detection from ESP32 camera')
    parser.add_argument('--checks', type=int, help='Number of checks to perform (default: infinite)', default=None)
    parser.add_argument('--display', action='store_true', help='Display captured images in window')
    args = parser.parse_args()

    if args.display:
        cv2.namedWindow('Bird Detection', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Bird Detection', DISPLAY_WIDTH, DISPLAY_WIDTH)  # Initial square window

    checks_performed = 0
    while args.checks is None or checks_performed < args.checks:
        print_timed("Capturing image...")
        image = capture_image()
        if image is not None:
            if args.display:
                display_image = resize_image(image.copy(), DISPLAY_WIDTH)
                cv2.imshow('Bird Detection', display_image)
                # Update window size to match the resized image aspect ratio
                cv2.resizeWindow('Bird Detection', DISPLAY_WIDTH, display_image.shape[0])
                cv2.waitKey(1)
            print_timed("Checking image quality...")
            if not is_blurred(image):
                print_timed("Image is clear, checking for birds...")
                if contains_bird(image):
                    print_timed("Bird detected! Saving image...")
                    save_image(image)
                else:
                    print_timed("No birds detected")
            else:
                print_timed("Image too blurry, skipping")
        checks_performed += 1
        is_last_check = args.checks is not None and checks_performed >= args.checks
        
        if not is_last_check:
            print_timed(f"Waiting {CAPTURE_INTERVAL} seconds...")
            time.sleep(CAPTURE_INTERVAL)

    if args.display:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

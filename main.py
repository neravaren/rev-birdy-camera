import cv2
import requests
import time
import os
import argparse
from datetime import datetime
import numpy as np
from dotenv import load_dotenv
from analysis import is_blurred, contains_bird

# Load environment variables
load_dotenv()

# Configuration
ESP32_CAMERA_URL = os.getenv("ESP32_CAMERA_URL", "http://10.2.1.143/capture")
SAVE_DIR = os.getenv("SAVE_DIR", "captured_birds")
BLUR_THRESHOLD = int(os.getenv("BLUR_THRESHOLD", "100"))
CAPTURE_INTERVAL = int(os.getenv("CAPTURE_INTERVAL", "5"))
DISPLAY_WIDTH = int(os.getenv("DISPLAY_WIDTH", "800"))  # Width in pixels for display window


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


def log(message, verbose_only=False, args=None):
    """Print a message with timestamp prefix if verbose conditions are met."""
    if not verbose_only or (args and args.verbose):
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
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()

    if args.display:
        cv2.namedWindow('Bird Detection', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Bird Detection', DISPLAY_WIDTH, DISPLAY_WIDTH)  # Initial square window

    checks_performed = 0
    while args.checks is None or checks_performed < args.checks:
        log("Capturing image...", verbose_only=True, args=args)
        image = capture_image()
        if image is not None:
            if args.display:
                display_image = resize_image(image.copy(), DISPLAY_WIDTH)
                cv2.imshow('Bird Detection', display_image)
                # Update window size to match the resized image aspect ratio
                cv2.resizeWindow('Bird Detection', DISPLAY_WIDTH, display_image.shape[0])
                cv2.waitKey(1)
            log("Checking image quality...", verbose_only=True, args=args)
            if not is_blurred(image, BLUR_THRESHOLD):
                log("Image is clear, checking for birds...", verbose_only=True, args=args)
                if contains_bird(image):
                    log("Bird detected! Saving image...")  # Always print detection
                    save_image(image)
                else:
                    log("No birds detected", verbose_only=True, args=args)
            else:
                log("Image too blurry, skipping", verbose_only=True, args=args)
        checks_performed += 1
        is_last_check = args.checks is not None and checks_performed >= args.checks

        if not is_last_check:
            log(f"Waiting {CAPTURE_INTERVAL} seconds...", verbose_only=True, args=args)
            time.sleep(CAPTURE_INTERVAL)

    if args.display:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

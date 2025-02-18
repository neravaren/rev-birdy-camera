import cv2
import requests
import time
import os
import argparse
from datetime import datetime
import numpy as np
from dotenv import load_dotenv
from analysis import analyze_blur, analyze_bird

# Load environment variables
load_dotenv()

# Configuration
ESP32_CAMERA_URL = os.getenv("ESP32_CAMERA_URL", "http://10.2.1.146/capture")
SAVE_DIR = os.getenv("SAVE_DIR", "storage")
SAVE_CAT_DIR = os.getenv("SAVE_CAT_DIR", "storage.cat")
BLUR_THRESHOLD = float(os.getenv("BLUR_THRESHOLD", "50"))
CAPTURE_INTERVAL = int(os.getenv("CAPTURE_INTERVAL", "5"))
BIRD_INTERVAL = int(os.getenv("BIRD_INTERVAL", "5"))
DISPLAY_WIDTH = int(os.getenv("DISPLAY_WIDTH", "800"))  # Width in pixels for display window
DO_SAVE_CAT = os.getenv("DO_SAVE_CAT", "True").lower() == "true"


# Ensure save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(SAVE_CAT_DIR, exist_ok=True)

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

def draw_detections(image, results):
    """Draw detection boxes and labels on the image."""
    annotated_image = image.copy()
    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Get box coordinates
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Get class and confidence
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            
            # Draw box
            color = (0, 255, 0) if cls == 14 else (0, 165, 255)  # Green for birds, orange for others
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)
            
            # Add label
            label = f"{r.names[cls]} {conf:.2f}"
            (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(annotated_image, (x1, y1-label_height-5), (x1+label_width, y1), color, -1)
            cv2.putText(annotated_image, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return annotated_image

def save_image(image, target_dir=SAVE_DIR, suffix=""):
    """Save image with timestamp in a structured directory format."""
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    time_str = now.strftime("%H%M%S")

    # Create directory structure
    dir_path = os.path.join(target_dir, year, month, day)
    os.makedirs(dir_path, exist_ok=True)

    filename = os.path.join(dir_path, f"{time_str}{suffix}.jpg")
    cv2.imwrite(filename, image)
    print(f"Saved: {filename}")

def main():
    parser = argparse.ArgumentParser(description='Bird detection from ESP32 camera')
    parser.add_argument('--checks', type=int, help='Number of checks to perform (default: infinite)', default=None)
    parser.add_argument('--display', action='store_true', help='Display captured images in window')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()

    print(f"Starting with BLUR_THRESHOLD={BLUR_THRESHOLD}, CAPTURE_INTERVAL={CAPTURE_INTERVAL}s")

    if args.display:
        cv2.namedWindow('Bird Detection', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Bird Detection', DISPLAY_WIDTH, DISPLAY_WIDTH)  # Initial square window

    checks_performed = 0
    while args.checks is None or checks_performed < args.checks:
        log("Capturing image...", verbose_only=True, args=args)
        image = capture_image()
        if image is None:
            continue

        # Check image quality
        log("Checking image quality...", verbose_only=True, args=args)
        blur_analysis = analyze_blur(image, BLUR_THRESHOLD)
        if blur_analysis["is_blurred"]:
            log(f"Image is blurry (variance: {blur_analysis['variance']:.2f})", verbose_only=True, args=args)
        else:
            log("Image is clear", verbose_only=True, args=args)

        # Analyze for birds
        log("Checking for birds...", verbose_only=True, args=args)
        bird_analysis = analyze_bird(image)

        # Prepare display image with detections
        display_image = image.copy()
        display_image_marked = draw_detections(display_image, bird_analysis["results"])

        # Display if requested
        if args.display:
            display_sized = resize_image(display_image_marked, DISPLAY_WIDTH)
            cv2.imshow('Bird Detection', display_sized)
            cv2.resizeWindow('Bird Detection', DISPLAY_WIDTH, display_sized.shape[0])
            cv2.waitKey(1)

        # Handle detection results
        if bird_analysis["contains_bird"]:
            log("Bird detected!", verbose_only=True, args=args)
            if not blur_analysis["is_blurred"]:
                log("Saving clear image with bird...")
                save_image(image)
                if DO_SAVE_CAT:
                    save_image(display_image_marked, target_dir=SAVE_CAT_DIR, suffix=".cat")
        else:
            log("No birds detected", verbose_only=True, args=args)
        checks_performed += 1
        is_last_check = args.checks is not None and checks_performed >= args.checks

        if not is_last_check:
            wait_time = BIRD_INTERVAL if bird_analysis["contains_bird"] else CAPTURE_INTERVAL
            log(f"Waiting {wait_time} seconds...", verbose_only=True, args=args)
            time.sleep(wait_time)

    if args.display:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

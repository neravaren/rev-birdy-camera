import cv2
import os
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

def get_variance(image):
    """Calculate the Laplacian variance of an image."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def is_blurred(image, threshold):
    """Check if the image is blurry using the Laplacian method."""
    variance = get_variance(image)
    return variance < threshold

def contains_bird(image):
    """Check if the image contains a bird using YOLOv8."""
    results = model(
        source=image,
        conf=0.2,
        iou=0.5,
        verbose=False,
    )
    for r in results:
        for box in r.boxes:
            if int(box.cls) == 14:  # COCO class ID for bird
                return True
    return False

if __name__ == "__main__":
    print("This module provides image analysis functions.")
    print("Run test.py to test the functionality.")

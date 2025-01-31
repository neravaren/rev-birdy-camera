import cv2
import os
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

def analyze_blur(image, threshold):
    """Analyze image blur and return detailed results.
    
    Returns:
        dict: Contains variance and is_blurred status
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return {
        "variance": variance,
        "is_blurred": variance < threshold
    }

def analyze_bird(image):
    """Analyze image for birds and return detailed results.
    
    Returns:
        dict: Contains YOLO results and contains_bird status
    """
    results = model(
        source=image,
        conf=0.2,
        iou=0.5,
        verbose=False,
    )
    
    contains_bird = False
    for r in results:
        for box in r.boxes:
            if int(box.cls) == 14:  # COCO class ID for bird
                contains_bird = True
                break
    
    return {
        "results": results,
        "contains_bird": contains_bird
    }

def get_variance(image):
    """Calculate the Laplacian variance of an image."""
    analysis = analyze_blur(image)
    return analysis["variance"]

def is_blurred(image, threshold):
    """Check if the image is blurry using the Laplacian method."""
    analysis = analyze_blur(image)
    return analysis["is_blurred"]

def contains_bird(image):
    """Check if the image contains a bird using YOLOv8."""
    analysis = analyze_bird(image)
    return analysis["contains_bird"]

if __name__ == "__main__":
    print("This module provides image analysis functions.")
    print("Run test.py to test the functionality.")

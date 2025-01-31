import cv2
import os
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

def is_blurred(image, threshold):
    """Check if the image is blurry using the Laplacian method."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance < threshold

def contains_bird(image):
    """Check if the image contains a bird using YOLOv8."""
    results = model(image, verbose=False)
    for r in results:
        for box in r.boxes:
            if int(box.cls) == 16:  # COCO class ID for bird
                return True
    return False

if __name__ == "__main__":
    # Test image analysis functions
    test_image_path = "test.jpg"
    if not os.path.exists(test_image_path):
        print(f"Error: Test image {test_image_path} not found!")
        exit(1)

    # Load and analyze test image
    image = cv2.imread(test_image_path)
    if image is None:
        print(f"Error: Could not load image {test_image_path}")
        exit(1)

    # Test blur detection
    blur_threshold = 100
    is_blur = is_blurred(image, blur_threshold)
    print(f"Image blur test (threshold={blur_threshold}):")
    print(f"  Is blurry: {is_blur}")

    # Test bird detection
    has_bird = contains_bird(image)
    print("\nBird detection test:")
    print(f"  Contains bird: {has_bird}")

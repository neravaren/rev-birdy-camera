import cv2
import os
from analysis import is_blurred, contains_bird

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

def test_single_image(image_path, blur_threshold=100):
    """Test analysis functions on a single image."""
    print(f"\nAnalyzing: {image_path}")
    print("-" * 50)
    
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image {image_path}")
        return False
    
    # Test blur detection
    is_blur = is_blurred(image, blur_threshold)
    print(f"Image blur test (threshold={blur_threshold}):")
    print(f"  Is blurry: {is_blur}")

    # Test bird detection
    has_bird = contains_bird(image)
    print("Bird detection test:")
    color = GREEN if has_bird else RED
    print(f"  Contains bird: {color}{has_bird}{RESET}")
    
    return True

def test_all_images():
    """Run tests on test.jpg or all images in test_images directory."""
    test_image_path = "test.jpg"
    test_images = []
    
    if os.path.exists(test_image_path):
        test_images.append(test_image_path)
    elif os.path.exists("test_images"):
        test_images.extend([
            os.path.join("test_images", f) 
            for f in os.listdir("test_images") 
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ])
    
    if not test_images:
        print("Error: No test images found! Please provide test.jpg or images in test_images folder")
        return False
    
    success = True
    for img_path in test_images:
        if not test_single_image(img_path):
            success = False
    
    return success

if __name__ == "__main__":
    test_all_images()

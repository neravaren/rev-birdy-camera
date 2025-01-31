from flask import Flask, render_template, send_from_directory, request
import os

app = Flask(__name__)
IMAGE_FOLDER = "captured_birds"  # Directory to store images

# Ensure the image folder exists
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

def get_image_files(page=1, per_page=12):
    """Get paginated list of image files from the image folder
    
    Args:
        page (int): Page number (1-based indexing)
        per_page (int): Number of images per page
        
    Returns:
        tuple: (list of image filenames for current page, total number of images)
    """
    # Get all images and sort by modification time (newest first)
    all_images = [(img, os.path.getmtime(os.path.join(IMAGE_FOLDER, img))) 
                 for img in os.listdir(IMAGE_FOLDER)
                 if img.endswith(('png', 'jpg', 'jpeg', 'gif', 'webp'))]
    all_images.sort(key=lambda x: x[1], reverse=True)
    all_images = [img[0] for img in all_images]  # Extract just the filenames
    
    total_images = len(all_images)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    return all_images[start_idx:end_idx], total_images

@app.route('/')
def gallery():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 25))
    
    images, total = get_image_files(page, per_page)
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('gallery.html', 
                         images=images,
                         current_page=page,
                         total_pages=total_pages)

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

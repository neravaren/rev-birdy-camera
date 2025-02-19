from flask import Flask, render_template, send_from_directory, request
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
IMAGE_FOLDER = "../storage"  # Directory to store images
IMAGE_CAT_FOLDER = "../storage.cat"
GALLERY_PORT = int(os.getenv("GALLERY_PORT", "5000"))
GALLERY_DEBUG = os.getenv("GALLERY_DEBUG", "True").lower() == "true"
IMAGES_PER_PAGE = 50  # Number of images to display per page

def get_image_files(year=None, month=None, day=None):
    """Get list of image files based on year, month, and day
    
    Args:
        year (str): Year to filter images
        month (str): Month to filter images
        day (str): Day to filter images
        
    Returns:
        tuple: (list of image filenames, list of years, list of months, list of days)
    """
    all_images = []
    years = []
    months = []
    days = []

    if year and month and day:
        all_images, months, days = get_images_by_date(year, month, day)
    elif year and month:
        all_images, months, days = get_images_by_month(year, month)
    elif year:
        all_images, months, years = get_images_by_year(year)
    else:
        all_images, years = get_all_images()

    return sorted(all_images, reverse=True), sorted(years), sorted(months), sorted(days)

def get_images_by_date(year, month, day):
    target_dir = os.path.join(IMAGE_FOLDER, year, month, day)
    return get_images_from_directory(target_dir), [], []

def get_images_by_month(year, month):
    target_dir = os.path.join(IMAGE_FOLDER, year, month)
    all_images = []
    days = []

    for root, dirs, _ in os.walk(target_dir):
        for dir in sorted(dirs):
            day_dir = os.path.join(target_dir, dir)
            days.append(os.path.basename(day_dir))
            all_images.extend(get_images_from_directory(day_dir))

    return all_images, [], sorted(days)

def get_images_by_year(year):
    target_dir = os.path.join(IMAGE_FOLDER, year)
    all_images = []
    months = []

    for month_dir in sorted(os.listdir(target_dir)):
        month_path = os.path.join(target_dir, month_dir)
        if os.path.isdir(month_path):
            months.append(month_dir)
            all_images.extend(get_images_from_directory(month_path))

    return all_images, sorted(months), []

def get_all_images():
    all_images = get_images_from_directory(IMAGE_FOLDER)
    years = sorted(os.listdir(IMAGE_FOLDER))
    return all_images, years

def get_images_from_directory(directory):
    return [os.path.relpath(os.path.join(root, file), IMAGE_FOLDER)
            for root, _, files in os.walk(directory)
            for file in files if file.endswith('.jpg')]

def get_notes(image_path):
    # Parse the image path to extract the date and time
    path_parts = image_path.split('/')
    if len(path_parts) == 4:  # Expecting <year>/<month>/<day>/<time>.jpg
        time_str = path_parts[-1].replace('.jpg', '')
        date_str = f"{path_parts[0]}-{path_parts[1]}-{path_parts[2]} {time_str}"
        # Convert to datetime object
        dt = datetime.strptime(date_str, "%Y-%m-%d %H%M%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return "No date available"

@app.route('/')
def gallery():
    now = datetime.now()
    select = request.args.get('select', None)
    year = request.args.get('year')
    month = request.args.get('month')
    day = request.args.get('day')
    page = int(request.args.get('page', 1))

    if not year and not month and not day and select is None:
        # Show today images by default
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")

    images, years, months, days = get_image_files(year, month, day)

    # Pagination logic
    total_images = len(images)
    total_pages = (total_images + IMAGES_PER_PAGE - 1) // IMAGES_PER_PAGE
    start_idx = (page - 1) * IMAGES_PER_PAGE
    end_idx = start_idx + IMAGES_PER_PAGE
    paginated_images = images[start_idx:end_idx]
    images_w_notes = [(x, get_notes(x)) for x in paginated_images]

    return render_template('gallery.html',
                         images=paginated_images,
                         images_w_notes=images_w_notes,
                         years=years,
                         months=months,
                         days=days,
                         current_year=year,
                         current_month=month,
                         current_day=day,
                         current_page=page,
                         total_pages=total_pages)

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/categories/<path:filename>')
def serve_image_cat(filename):
    return send_from_directory(IMAGE_CAT_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=GALLERY_PORT, debug=GALLERY_DEBUG)

from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)
IMAGE_FOLDER = "captured_birds"  # Directory to store images

# Ensure the image folder exists
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

@app.route('/')
def gallery():
    images = [img for img in os.listdir(IMAGE_FOLDER) if img.endswith(('png', 'jpg', 'jpeg', 'gif', 'webp'))]
    return render_template('gallery.html', images=images)

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)

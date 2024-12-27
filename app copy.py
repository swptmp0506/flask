import os
import json
from flask import Flask, request, render_template, send_from_directory

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'  # Folder to store uploaded images
DATA_FILE = 'furniture_inventory.json'  # JSON file to store inventory data
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed file types

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the uploads folder exists

# Ensure the JSON file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

# Helper functions
def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_data():
    """Load inventory data from the JSON file."""
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    """Save inventory data to the JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Routes
@app.route('/')
def home():
    """Render the upload form."""
    return render_template('index.html')

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    data = load_data()
    if item_id < 0 or item_id >= len(data):
        return "Invalid item ID.", 400

    # Remove the item
    removed_item = data.pop(item_id)

    # Save updated inventory
    save_data(data)

    return f"Item '{removed_item['name']}' deleted successfully!", 200


@app.route('/upload', methods=['POST'])
def upload():
    item_name = request.form.get('itemName')  # Get item name
    item_value = request.form.get('itemValue')  # Get item value
    photo = request.files.get('itemPhoto')  # Get uploaded file

    # Validate inputs
    if not item_name or not item_value or not photo:
        return "All fields are required.", 400

    # Save the photo to the uploads folder
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
    photo.save(photo_path)

    # Generate the full URL for the photo
    photo_url = f"{request.url_root}uploads/{photo.filename}"  # Full URL

    # Save metadata to JSON file
    data = load_data()
    data.append({'name': item_name, 'value': float(item_value), 'photo_path': photo_url})
    save_data(data)

    return f"Item '{item_name}' uploaded successfully!"

@app.route('/inventory')
def inventory():
    """Display the inventory with uploaded items."""
    data = load_data()
    return render_template('inventory.html', items=data)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

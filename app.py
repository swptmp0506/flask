import os
import json
from flask import Flask, request, render_template, redirect, url_for, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
DATA_FILE = 'furniture_inventory.json'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_new_id(data):
    # If no items, start from 1, else max id + 1
    if not data:
        return 1
    return max(item['id'] for item in data) + 1

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    item_name = request.form.get('itemName')
    item_value = request.form.get('itemValue')
    item_cost = request.form.get('itemCost')
    item_notes = request.form.get('itemNotes')
    photo = request.files.get('itemPhoto')

    if not item_name or not item_value or not item_cost or not photo:
        return "All fields (except notes) are required.", 400

    if not allowed_file(photo.filename):
        return "Invalid file type.", 400

    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
    photo.save(photo_path)
    photo_url = f"{request.url_root}uploads/{photo.filename}"

    data = load_data()
    new_id = get_new_id(data)
    data.append({
        'id': new_id,
        'name': item_name,
        'value': float(item_value),
        'cost': float(item_cost),
        'notes': item_notes or "",
        'photo_path': photo_url,
        'archived': False
    })
    save_data(data)

    return redirect(url_for('inventory'))

@app.route('/inventory')
def inventory():
    data = load_data()
    active_items = [item for item in data if not item.get('archived', False)]
    return render_template('inventory.html', items=active_items)

@app.route('/inventory/read-only')
def read_only_inventory():
    data = load_data()
    active_items = [item for item in data if not item.get('archived', False)]
    return render_template('inventory_read_only.html', items=active_items)

@app.route('/archived')
def archived_items():
    data = load_data()
    archived_items = [item for item in data if item.get('archived', False)]
    return render_template('archived.html', items=archived_items)

def find_item_by_id(data, item_id):
    for item in data:
        if item['id'] == item_id:
            return item
    return None

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    data = load_data()
    item = find_item_by_id(data, item_id)
    if not item:
        return "Invalid item ID.", 400

    data.remove(item)
    save_data(data)
    return redirect(url_for('inventory'))

@app.route('/archive/<int:item_id>', methods=['POST'])
def archive_item(item_id):
    data = load_data()
    item = find_item_by_id(data, item_id)
    if not item:
        return "Invalid item ID.", 400

    item['archived'] = True
    save_data(data)
    return redirect(url_for('inventory'))

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    data = load_data()
    item = find_item_by_id(data, item_id)

    if not item:
        return "Invalid item ID.", 400

    if request.method == 'POST':
        item['name'] = request.form.get('itemName')
        item['value'] = float(request.form.get('itemValue'))
        item['cost'] = float(request.form.get('itemCost'))
        item['notes'] = request.form.get('itemNotes') or ""
        save_data(data)
        return redirect(url_for('inventory'))

    return render_template('edit.html', item=item, item_id=item_id)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

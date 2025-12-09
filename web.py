from flask import Flask, render_template, request, redirect
import yaml
import os
from werkzeug.utils import secure_filename
import glob

app = Flask(__name__)

CONFIG_PATH = 'config.yaml'
FLAG_PATH = '.refresh_dashboard.flag'  # IPC flag

# Folder to save user-uploaded images (working directory)
UPLOAD_FOLDER = 'assets/User_Images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Helper functions ---
def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

def save_config(cfg):
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(cfg, f)
    # Touch the flag file
    with open(FLAG_PATH, 'w') as flag:
        flag.write('trigger')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    config = load_config()
    
    if request.method == 'POST':
        # --- Handle image upload ---
        if 'upload_image' in request.form and 'user_image' in request.files:
            file = request.files['user_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(save_path)
                app.logger.debug(f"Saved image to: {save_path}, exists: {os.path.exists(save_path)}")

                # --- Update config without overwriting other keys ---
                image_config = config.setdefault('image', {})
                image_config['path'] = save_path

        # --- Handle dashboard selection ---
        if 'dashboard' in request.form:
            config['current_dashboard'] = request.form['dashboard']

        # --- Handle cycling settings ---
        cycle_config = config.setdefault('cycle', {})
        cycle_config['enabled'] = 'cycle_enabled' in request.form
        
        try:
            interval = int(request.form.get('cycle_interval', 5))
            cycle_config['interval_minutes'] = max(1, interval)
        except (ValueError, TypeError):
            cycle_config['interval_minutes'] = 5

        dashboards_config = cycle_config.setdefault('dashboards', {})
        for dashboard in ['clock', 'youtube', 'weather', 'stocks', 'text', 'image']:
            dashboards_config[dashboard] = f'enable_{dashboard}' in request.form

        save_config(config)
        return redirect('/')

    # List all images in assets/User_Images
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    images_list = [os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(f)) 
                for f in glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*'))]

    cycle_config = config.get('cycle', {})
    return render_template('index.html', 
                           current=config.get('current_dashboard', 'clock'),
                           cycle_enabled=cycle_config.get('enabled', False),
                           cycle_interval=cycle_config.get('interval_minutes', 5),
                           dashboard_enables=cycle_config.get('dashboards', {}),
                           images_list=images_list)

    # --- Handle image deletion ---
    if 'delete_image' in request.form:
        img_to_delete = request.form['delete_image']
        if os.path.exists(img_to_delete):
            os.remove(img_to_delete)
            app.logger.debug(f"Deleted image: {img_to_delete}")
        return redirect('/')  # reload page after deletion


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == 'POST':
        new_config = request.form['config']
        with open(CONFIG_PATH, 'w') as f:
            f.write(new_config)
        # Touch the flag file
        with open(FLAG_PATH, 'w') as flag:
            flag.write('trigger')
        return redirect('/')
    
    return render_template('edit.html', config=open(CONFIG_PATH).read())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

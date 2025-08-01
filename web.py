from flask import Flask, render_template, request, redirect
import yaml
import os

app = Flask(__name__)
CONFIG_PATH = 'config.yaml'
FLAG_PATH = '.refresh_dashboard.flag'  # IPC flag

def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

def save_config(cfg):
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(cfg, f)
    # Touch the flag file
    with open(FLAG_PATH, 'w') as flag:
        flag.write('trigger')

@app.route('/', methods=['GET', 'POST'])
def index():
    config = load_config()
    if request.method == 'POST':
        config['current_dashboard'] = request.form['dashboard']
        save_config(config)
        return redirect('/')
    return render_template('index.html', current=config.get('current_dashboard', 'clock'))

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == 'POST':
        new_config = request.form['config']
        with open(CONFIG_PATH, 'w') as f:
            f.write(new_config)
        # Also set the flag
        with open(FLAG_PATH, 'w') as flag:
            flag.write('trigger')
        return redirect('/')
    return render_template('edit.html', config=open(CONFIG_PATH).read())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

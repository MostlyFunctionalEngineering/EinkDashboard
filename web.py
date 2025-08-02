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
        # Handle dashboard selection
        if 'dashboard' in request.form:
            config['current_dashboard'] = request.form['dashboard']
        
        # Handle cycling settings
        if 'cycle_enabled' in request.form:
            cycle_config = config.setdefault('cycle', {})
            cycle_config['enabled'] = request.form.get('cycle_enabled') == 'on'
            
            # Update cycle interval
            try:
                interval = int(request.form.get('cycle_interval', 5))
                cycle_config['interval_minutes'] = max(1, interval)  # Minimum 1 minute
            except (ValueError, TypeError):
                cycle_config['interval_minutes'] = 5
            
            # Update dashboard enables
            dashboards_config = cycle_config.setdefault('dashboards', {})
            for dashboard in ['clock', 'youtube', 'weather', 'stocks']:
                dashboards_config[dashboard] = request.form.get(f'enable_{dashboard}') == 'on'
        
        save_config(config)
        return redirect('/')
    
    # Get cycle configuration for template
    cycle_config = config.get('cycle', {})
    return render_template('index.html', 
                         current=config.get('current_dashboard', 'clock'),
                         cycle_enabled=cycle_config.get('enabled', False),
                         cycle_interval=cycle_config.get('interval_minutes', 5),
                         dashboard_enables=cycle_config.get('dashboards', {}))

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

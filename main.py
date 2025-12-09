import os
import time
import yaml
import logging
import sys
import threading
from datetime import datetime

from display import show_dashboard
import lib.epd2in13b_V4 as epd2in13b_V4
import web  # assumes web.py defines Flask app as `app`

CONFIG_PATH = 'config.yaml'
FLAG_PATH = '.refresh_dashboard.flag'

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def setup_logging(config):
    level_str = config.get('logging', {}).get('level', 'INFO').upper()
    level = getattr(logging, level_str, logging.INFO)
    logging.basicConfig(level=level, format='%(asctime)s [%(levelname)s] %(message)s')

def check_and_clear_flag():
    if os.path.exists(FLAG_PATH):
        os.remove(FLAG_PATH)
        logging.debug("Refresh flag detected and cleared")
        return True
    return False

def start_web_gui():
    web.app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

def get_refresh_interval(dashboard_name, config):
    if dashboard_name == 'clock':
        return None
    return config.get(dashboard_name, {}).get('refresh_interval_seconds', 60)

def get_enabled_dashboards(config):
    """Get list of dashboards enabled for cycling"""
    cycle_config = config.get('cycle', {})
    enabled_dashboards = cycle_config.get('dashboards', {})
    return [name for name, enabled in enabled_dashboards.items() if enabled]

def get_next_dashboard(current_dashboard, enabled_dashboards):
    """Get the next dashboard in the cycle"""
    if not enabled_dashboards:
        return current_dashboard
    
    try:
        current_index = enabled_dashboards.index(current_dashboard)
        next_index = (current_index + 1) % len(enabled_dashboards)
        return enabled_dashboards[next_index]
    except ValueError:
        # Current dashboard not in enabled list, return first enabled
        return enabled_dashboards[0] if enabled_dashboards else current_dashboard

def main():
    config = load_config()
    setup_logging(config)

    epd = epd2in13b_V4.EPD()
    epd.init_fast()

    gui_thread = threading.Thread(target=start_web_gui, daemon=True)
    gui_thread.start()

    last_dashboard = None
    last_minute = None
    last_rendered = 0
    last_cycle_time = time.time()

    try:
        while True:
            config = load_config()
            current = config.get('current_dashboard', 'clock')
            
            # Check for cycling
            cycle_config = config.get('cycle', {})
            cycle_enabled = cycle_config.get('enabled', False)
            cycle_interval_minutes = cycle_config.get('interval_minutes', 5)
            flip_screen = config.get('flip_screen', False)
            
            now = time.time()
            force_refresh = check_and_clear_flag()
            
            # Handle automatic cycling
            if cycle_enabled and (now - last_cycle_time >= cycle_interval_minutes * 60):
                enabled_dashboards = get_enabled_dashboards(config)
                if enabled_dashboards:
                    next_dashboard = get_next_dashboard(current, enabled_dashboards)
                    if next_dashboard != current:
                        config['current_dashboard'] = next_dashboard
                        # Save the updated config
                        with open(CONFIG_PATH, 'w') as f:
                            yaml.dump(config, f)
                        current = next_dashboard
                        logging.info(f"Cycled to dashboard: {current}")
                last_cycle_time = now

            logging.debug(f"Selected dashboard: {current}")

            should_render = False

            if current == 'clock':
                this_minute = datetime.now().strftime('%Y-%m-%d %H:%M')
                if force_refresh or this_minute != last_minute:
                    should_render = True
                    last_minute = this_minute

            else:
                interval = get_refresh_interval(current, config)
                if current != last_dashboard:
                    should_render = True
                elif force_refresh or (now - last_rendered >= interval):
                    should_render = True

            if should_render:
                try:
                    show_dashboard(current, epd, config, flip_screen=flip_screen)
                    logging.info(f"Rendered dashboard: {current}")
                    last_rendered = now
                    last_dashboard = current
                except Exception as e:
                    logging.exception(f"Failed to render dashboard '{current}': {e}")

            # Wait short time to keep loop responsive
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("Interrupted by user. Cleaning up.")
        epd2in13b_V4.epdconfig.module_exit(cleanup=True)
        sys.exit(0)

if __name__ == '__main__':
    main()

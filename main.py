import os
import time
import yaml
import logging
import sys
import threading

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

def sleep_aligned(seconds):
    now = time.time()
    next_time = ((now // seconds) + 1) * seconds
    time.sleep(max(0, next_time - now))

def sleep_for_dashboard(dashboard_name, interval):
    start = time.time()
    deadline = start + interval

    if dashboard_name == 'clock':
        logging.debug(f"[{dashboard_name}] Aligned interruptible sleep for {interval} seconds")
        while time.time() < deadline:
            time.sleep(1)
            if os.path.exists(FLAG_PATH):
                logging.debug(f"[{dashboard_name}] Refresh flag detected during aligned sleep — breaking early")
                break
        logging.debug(f"[{dashboard_name}] Aligned sleep complete")
        return

    logging.debug(f"[{dashboard_name}] Sleep for {interval} seconds")
    time.sleep(interval)


def get_refresh_interval(dashboard_name, config):
    return config.get(dashboard_name, {}).get('refresh_interval_seconds', 60)

def start_web_gui():
    web.app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

def check_and_clear_flag():
    if os.path.exists(FLAG_PATH):
        os.remove(FLAG_PATH)
        logging.debug("Refresh flag detected and cleared")
        return True
    return False

def main():
    config = load_config()
    setup_logging(config)

    epd = epd2in13b_V4.EPD()
    epd.init()

    gui_thread = threading.Thread(target=start_web_gui, daemon=True)
    gui_thread.start()

    last_dashboard = None

    try:
        while True:
            logging.debug(f"Starting dashboard loop at {time.strftime('%H:%M:%S')}")

            config = load_config()
            current = config.get('current_dashboard', 'clock')
            logging.debug(f"Selected dashboard: {current}")

            force_refresh = check_and_clear_flag()

            if current != last_dashboard or force_refresh:
                try:
                    show_dashboard(current, epd, config)
                    logging.info(f"Rendered dashboard: {current}")
                    last_dashboard = current
                except Exception as e:
                    logging.exception(f"Failed to render dashboard '{current}': {e}")

            interval = get_refresh_interval(current, config)
            logging.debug(f"Dashboard '{current}' refresh interval: {interval} seconds")
            sleep_for_dashboard(current, interval)

    except KeyboardInterrupt:
        logging.info("Interrupted by user. Cleaning up.")
        epd2in13b_V4.epdconfig.module_exit(cleanup=True)
        sys.exit(0)

if __name__ == '__main__':
    main()

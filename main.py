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

def sleep_for_dashboard(dashboard_name, interval, last_mtime_ref):
    start = time.time()
    if dashboard_name == 'clock':
        logging.debug(f"[{dashboard_name}] Aligned sleep starting for {interval} seconds")
        sleep_aligned(interval)
        logging.debug(f"[{dashboard_name}] Aligned sleep complete")
        return

    logging.debug(f"[{dashboard_name}] Interruptible sleep starting for up to {interval} seconds")
    deadline = start + interval

    while time.time() < deadline:
        time.sleep(1)
        try:
            current_mtime = os.path.getmtime(CONFIG_PATH)
            if current_mtime != last_mtime_ref[0]:
                logging.debug("Detected config change during sleep — breaking early")
                break
        except FileNotFoundError:
            logging.warning("Config file disappeared during sleep — breaking")
            break

    slept = round(time.time() - start, 2)
    logging.debug(f"[{dashboard_name}] Slept for {slept} seconds")

def get_refresh_interval(dashboard_name, config):
    return config.get(dashboard_name, {}).get('refresh_interval_seconds', 60)

def start_web_gui():
    web.app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

def main():
    config = load_config()
    setup_logging(config)

    epd = epd2in13b_V4.EPD()
    epd.init()

    gui_thread = threading.Thread(target=start_web_gui, daemon=True)
    gui_thread.start()

    last_mtime = os.path.getmtime(CONFIG_PATH)
    last_mtime_ref = [last_mtime]  # mutable reference
    last_dashboard = None

    try:
        while True:
            logging.debug(f"Starting dashboard loop at {time.strftime('%H:%M:%S')}")
            mtime = os.path.getmtime(CONFIG_PATH)
            config_changed = mtime != last_mtime
            if config_changed:
                config = load_config()
                logging.debug("Config file changed, reloading")

            current = config.get('current_dashboard', 'clock')
            logging.debug(f"Selected dashboard: {current}")

            if current != last_dashboard or config_changed:
                try:
                    show_dashboard(current, epd, config)
                    logging.info(f"Rendered dashboard: {current}")
                    last_dashboard = current
                except Exception as e:
                    logging.exception(f"Failed to render dashboard '{current}': {e}")

            interval = get_refresh_interval(current, config)
            logging.debug(f"Dashboard '{current}' refresh interval: {interval} seconds")
            logging.debug(f"Sleeping for {interval} seconds")
            sleep_for_dashboard(current, interval, last_mtime_ref)

            # Re-check mtime after sleeping to detect mid-sleep config edits
            new_mtime = os.path.getmtime(CONFIG_PATH)
            config_changed = new_mtime != last_mtime
            if config_changed:
                config = load_config()
                logging.debug("Config file changed during sleep, reloading")

            last_mtime = new_mtime
            last_mtime_ref[0] = new_mtime



    except KeyboardInterrupt:
        logging.info("Interrupted by user. Cleaning up.")
        epd2in13b_V4.epdconfig.module_exit(cleanup=True)
        sys.exit(0)

if __name__ == '__main__':
    main()

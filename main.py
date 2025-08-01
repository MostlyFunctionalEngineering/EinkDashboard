import time
import yaml
import logging
import sys
from display import show_dashboard
import lib.epd2in13b_V4 as epd2in13b_V4

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

def get_refresh_interval(dashboard_name, config):
    return config.get(dashboard_name, {}).get('refresh_interval_seconds', 60)

def sleep_for_dashboard(dashboard_name, interval):
    if dashboard_name == 'clock':
        sleep_aligned(interval)
    else:
        time.sleep(interval)

def main():
    epd = epd2in13b_V4.EPD()
    epd.init()    

    try:
        while True:
            config = load_config()
            current = config.get('current_dashboard', 'clock')
            setup_logging(config)
            logging.debug(f"Selected dashboard: {current}")
            try:
                show_dashboard(current, epd, config)
                logging.info(f"Rendered dashboard: {current}")
            except Exception as e:
                logging.exception(f"Failed to render dashboard '{current}': {e}")
            interval = get_refresh_interval(current, config)
            logging.debug(f"Sleeping for {interval} seconds")
            sleep_for_dashboard(current, interval)

    except KeyboardInterrupt:
        logging.info("Interrupted by user. Cleaning up.")
        epd2in13b_V4.epdconfig.module_exit(cleanup=True)
        sys.exit(0)

if __name__ == '__main__':
    main()

import time, yaml
from display import show_dashboard
import lib.epd2in13b_V4 as epd2in13b_V4

CONFIG_PATH = 'config.yaml'

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def sleep_aligned(seconds):
    now = time.time()
    next_time = ((now // seconds) + 1) * seconds
    time.sleep(max(0, next_time - now))

def get_refresh_interval(dashboard_name, config):
    """Get refresh interval from config for a given dashboard."""
    return config.get(dashboard_name, {}).get('refresh_interval_seconds', 60)

def sleep_for_dashboard(dashboard_name, interval):
    """Sleep aligned to the interval for 'clock', otherwise sleep raw."""
    if dashboard_name == 'clock':
        sleep_aligned(interval)
    else:
        time.sleep(interval)

def main():
    epd = epd2in13b_V4.EPD()
    epd.init()

    while True:
        config = load_config()
        current = config.get('current_dashboard', 'clock')
        try:
            show_dashboard(current, epd, config)
        except Exception as e:
            print(f"Error: {e}")
        interval = get_refresh_interval(current, config)
        sleep_for_dashboard(current, interval)

if __name__ == '__main__':
    main()

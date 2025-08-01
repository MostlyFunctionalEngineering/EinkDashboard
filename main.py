import time, yaml
from display import show_dashboard
import lib.epd2in13b_V4 as epd2in13b_V4

CONFIG_PATH = 'config.yaml'

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

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
        time.sleep(config.get('refresh_interval_seconds', 60))

if __name__ == '__main__':
    main()

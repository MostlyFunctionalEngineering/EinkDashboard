#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os, sys, time, yaml, csv, logging
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import requests
from dotenv import load_dotenv
import lib.epd2in13b_V4 as epd2in13b_V4

epd = None

# Paths
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, 'config.yaml')
DATA_PATH = os.path.join(SCRIPT_DIR, 'data', 'subscribers.csv')
ASSETS_DIR = os.path.join(SCRIPT_DIR, 'assets')

# Load config
load_dotenv()
with open(CONFIG_PATH, 'r') as f:
    config = yaml.safe_load(f)

# Logging config
log_level = config.get('log_level', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# API credentials
API_KEY = os.getenv("YOUTUBE_API_KEY") or config['api_key']
CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID") or config['channel_id']
REFRESH_MINUTES = config.get('refresh_interval_minutes', 1)

# Asset config
ASSETS_CONFIG = config.get('assets', {})
FONT_PATH = os.path.join(ASSETS_DIR, ASSETS_CONFIG.get('font', 'Fonts/thirteen-pixel-fonts/default.ttf'))
LOGO_PATH = os.path.join(ASSETS_DIR, ASSETS_CONFIG.get('logo', 'YouTube_Logo_68x48.png'))
BG_PATH_RAW = ASSETS_CONFIG.get('background', '')
BG_PATH = os.path.join(ASSETS_DIR, BG_PATH_RAW) if BG_PATH_RAW else None

# Warn on missing files
for label, path in [('font', FONT_PATH), ('logo', LOGO_PATH), ('background', BG_PATH)]:
    if path and not os.path.isfile(path):
        logging.warning(f"{label.capitalize()} file not found: {path}")

# Safety check
if not API_KEY or not CHANNEL_ID:
    logging.error("API key or Channel ID not set")
    sys.exit(1)

def fetch_subscriber_count():
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={CHANNEL_ID}&key={API_KEY}"
    try:
        logging.debug(f"Requesting subscriber count from YouTube API: {url}")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        count = int(data['items'][0]['statistics']['subscriberCount'])
        logging.info(f"Fetched subscriber count: {count}")
        return count
    except Exception as e:
        logging.error(f"API Error: {e}")
        return None

def record_to_csv(count):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), count])
    logging.debug(f"Appended subscriber count to CSV: {count}")

def read_historical_data():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, 'r') as f:
        reader = csv.reader(f)
        data = [(datetime.fromisoformat(row[0]), int(row[1])) for row in reader]
    logging.debug(f"Loaded {len(data)} historical records")
    return data

def get_changes(data):
    now = datetime.now()
    def delta_filter(delta): 
        target = now - delta
        closest = min(data, key=lambda x: abs(x[0] - target), default=(now, data[-1][1]))
        return closest[1]

    latest = data[-1][1]
    daily = latest - delta_filter(timedelta(days=1))
    weekly = latest - delta_filter(timedelta(weeks=1))
    monthly = latest - delta_filter(timedelta(days=30))
    return latest, daily, weekly, monthly

def draw_dashboard(epd):
    logging.debug("Initializing EPD display")
    epd.init()
    epd.Clear()

    # Create blank images
    black_img = Image.new('1', (epd.height, epd.width), 255)
    red_img = Image.new('1', (epd.height, epd.width), 255)
    draw_black = ImageDraw.Draw(black_img)
    draw_red = ImageDraw.Draw(red_img)

    # Center the YouTube logo
    try:
        logo = Image.open(LOGO_PATH)
        logo_width, logo_height = logo.size

        x_center = (epd.height - logo_width) // 2
        y_center = (epd.width - logo_height) // 2

        red_img.paste(logo, (x_center, y_center))
        logging.debug("Logo pasted to red layer at center")
    except Exception as e:
        logging.warning(f"Logo load failed: {e}")

    epd.display(epd.getbuffer(black_img), epd.getbuffer(red_img))
    epd.sleep()

"""
def draw_dashboard(epd, count, daily, weekly, monthly):
    logging.debug("Initializing EPD display")
    epd.init()
    epd.Clear()

    black_img = Image.new('1', (epd.height, epd.width), 255)
    red_img = Image.new('1', (epd.height, epd.width), 255)
    draw_black = ImageDraw.Draw(black_img)
    draw_red = ImageDraw.Draw(red_img)

    if BG_PATH and os.path.isfile(BG_PATH):
        try:
            logging.debug(f"Loading background image from {BG_PATH}")
            bg = Image.open(BG_PATH).resize((epd.height, epd.width))
            black_img.paste(bg, (0, 0))
        except Exception as e:
            logging.warning(f"Background not loaded: {e}")

    try:
        font_small = ImageFont.truetype(FONT_PATH, 14)
        font_large = ImageFont.truetype(FONT_PATH, 20)
    except OSError:
        logging.warning(f"Failed to load font at {FONT_PATH}, using default")
        font_small = font_large = ImageFont.load_default()

    try:
        logo = Image.open(LOGO_PATH)
        red_img.paste(logo, (5, 5))
    except Exception as e:
        logging.warning(f"Logo not loaded: {e}")

    logging.debug("Drawing text on dashboard")
    draw_black.text((60, 5), f"{count} subs", font=font_large, fill=0)
    draw_black.text((5, 40), f"Daily:   {daily:+}", font=font_small, fill=0)
    draw_black.text((5, 60), f"Weekly:  {weekly:+}", font=font_small, fill=0)
    draw_black.text((5, 80), f"Monthly: {monthly:+}", font=font_small, fill=0)

    logging.debug("Pushing image to EPD")
    epd.display(epd.getbuffer(black_img), epd.getbuffer(red_img))
    epd.sleep()
"""

def main():
    global epd
    logging.info("Starting logo test loop")
    epd = epd2in13b_V4.EPD()

    while True:
        draw_dashboard(epd)
        time.sleep(5)
    
    """
    logging.info("Starting dashboard loop")
    epd = epd2in13b_V4.EPD()
    while True:
        count = fetch_subscriber_count()
        if count is not None:
            record_to_csv(count)
            history = read_historical_data()
            if len(history) >= 1:
                count, daily, weekly, monthly = get_changes(history)
                draw_dashboard(epd, count, daily, weekly, monthly)
        else:
            logging.warning("No subscriber data fetched; skipping dashboard update")
        time.sleep(REFRESH_MINUTES * 60)
    """

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Interrupted — clearing screen and cleaning up")
        if epd:
            try:
                epd.init()
                epd.Clear()
            except Exception as e:
                logging.warning(f"Failed to clear display during exit: {e}")
        epd2in13b_V4.epdconfig.module_exit(cleanup=True)
        sys.exit()

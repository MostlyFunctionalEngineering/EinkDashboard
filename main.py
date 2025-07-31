#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os, sys, time, yaml, csv, logging
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import requests
import lib.epd2in13b_V4 as epd2in13b_V4

# Setup
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, 'config.yaml')
DATA_PATH = os.path.join(SCRIPT_DIR, 'data', 'subscribers.csv')
ASSETS_PATH = os.path.join(SCRIPT_DIR, 'assets')
LOGO_PATH = os.path.join(ASSETS_PATH, 'youtube_logo.bmp')
FONT_PATH = os.path.join(SCRIPT_DIR, 'pic', 'Font.ttc')

logging.basicConfig(level=logging.INFO)

# Load config
with open(CONFIG_PATH, 'r') as f:
    config = yaml.safe_load(f)
API_KEY = config['api_key']
CHANNEL_ID = config['channel_id']
REFRESH_MINUTES = config.get('refresh_interval_minutes', 60)

def fetch_subscriber_count():
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={CHANNEL_ID}&key={API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        return int(data['items'][0]['statistics']['subscriberCount'])
    except Exception as e:
        logging.error("API Error: " + str(e))
        return None

def record_to_csv(count):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), count])

def read_historical_data():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, 'r') as f:
        reader = csv.reader(f)
        return [(datetime.fromisoformat(row[0]), int(row[1])) for row in reader]

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

def draw_dashboard(epd, count, daily, weekly, monthly):
    # Init
    epd.init()
    epd.Clear()

    # Create Images
    black_img = Image.new('1', (epd.height, epd.width), 255)
    red_img = Image.new('1', (epd.height, epd.width), 255)
    draw_black = ImageDraw.Draw(black_img)
    draw_red = ImageDraw.Draw(red_img)

    # Fonts
    font_small = ImageFont.truetype(FONT_PATH, 14)
    font_large = ImageFont.truetype(FONT_PATH, 20)

    # Draw YouTube logo
    logo = Image.open(LOGO_PATH)
    red_img.paste(logo, (5, 5))

    # Draw counts
    draw_black.text((60, 5), f"{count} subs", font=font_large, fill=0)
    draw_black.text((5, 40), f"Daily:   {daily:+}", font=font_small, fill=0)
    draw_black.text((5, 60), f"Weekly:  {weekly:+}", font=font_small, fill=0)
    draw_black.text((5, 80), f"Monthly: {monthly:+}", font=font_small, fill=0)

    # Display
    epd.display(epd.getbuffer(black_img), epd.getbuffer(red_img))
    epd.sleep()

def main():
    epd = epd2in13b_V4.EPD()
    while True:
        count = fetch_subscriber_count()
        if count is not None:
            record_to_csv(count)
            history = read_historical_data()
            if len(history) >= 1:
                count, daily, weekly, monthly = get_changes(history)
                draw_dashboard(epd, count, daily, weekly, monthly)
        time.sleep(REFRESH_MINUTES * 60)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Interrupted")
        epd2in13b_V4.epdconfig.module_exit(cleanup=True)
        sys.exit()
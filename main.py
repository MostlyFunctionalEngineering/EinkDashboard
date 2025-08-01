#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os, sys, time, logging
from PIL import Image
import lib.epd2in13b_V4 as epd2in13b_V4

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Paths
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, 'assets')
LOGO_PATH = os.path.join(ASSETS_DIR, 'YouTube_Logo_68x48.png')  # Adjust as needed

try:
    logging.info("Initializing display")
    epd = epd2in13b_V4.EPD()
    epd.init()
    epd.Clear()
    time.sleep(1)

    logging.info("Entering refresh loop")
    while True:
        # Prepare frame buffers
        black_img = Image.new('1', (epd.height, epd.width), 255)  # White background
        red_img = Image.new('1', (epd.height, epd.width), 255)

        # Load and center logo
        try:
            logo = Image.open(LOGO_PATH)
            logo_w, logo_h = logo.size
            x = (epd.height - logo_w) // 2
            y = (epd.width - logo_h) // 2
            red_img.paste(logo, (x, y))
            logging.debug("Logo pasted at center")
        except Exception as e:
            logging.warning(f"Logo failed to load: {e}")

        epd.display(epd.getbuffer(black_img), epd.getbuffer(red_img))
        time.sleep(5)

except KeyboardInterrupt:
    logging.info("Ctrl+C received — clearing and exiting")
    try:
        epd.init()
        epd.Clear()
    except Exception as e:
        logging.warning(f"Could not clear screen: {e}")
    epd.sleep()
    epd2in13b_V4.epdconfig.module_exit(cleanup=True)
    sys.exit()

except Exception as e:
    logging.error(f"Unhandled error: {e}")
    epd2in13b_V4.epdconfig.module_exit(cleanup=True)
    sys.exit(1)

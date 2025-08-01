#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os, sys, time, logging, traceback
from PIL import Image, ImageDraw, ImageFont
import lib.epd2in13b_V4 as epd2in13b_V4  # Use your vendored driver

# Logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Directories
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
PIC_DIR = os.path.join(SCRIPT_DIR, 'assets')  # Replace 'pic' with your own structure

try:
    logging.info("epd2in13b_V4 Demo")

    epd = epd2in13b_V4.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()
    time.sleep(1)

    # Load fonts
    font_path = os.path.join(PIC_DIR, 'Fonts/thirteen-pixel-fonts/ThirteenPixelFontsRegular-wjR3.ttf')  # You must have this font locally
    font20 = ImageFont.truetype(font_path, 20)
    font18 = ImageFont.truetype(font_path, 18)

    # Horizontal drawing
    logging.info("1. Drawing on the Horizontal image...")
    HBlackimage = Image.new('1', (epd.height, epd.width), 255)
    HRYimage = Image.new('1', (epd.height, epd.width), 255)
    drawblack = ImageDraw.Draw(HBlackimage)
    drawry = ImageDraw.Draw(HRYimage)

    drawblack.text((10, 0), 'hello world', font=font20, fill=0)
    drawblack.text((10, 20), '2.13inch e-Paper b V4', font=font20, fill=0)
    drawblack.text((120, 0), u'微雪电子', font=font20, fill=0)
    drawblack.line((20, 50, 70, 100), fill=0)
    drawblack.line((70, 50, 20, 100), fill=0)
    drawblack.rectangle((20, 50, 70, 100), outline=0)
    drawry.line((165, 50, 165, 100), fill=0)
    drawry.line((140, 75, 190, 75), fill=0)
    drawry.arc((140, 50, 190, 100), 0, 360, fill=0)
    drawry.rectangle((80, 50, 130, 100), fill=0)
    drawry.chord((85, 55, 125, 95), 0, 360, fill=1)

    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
    time.sleep(2)

    # Vertical drawing
    logging.info("2. Drawing on the Vertical image...")
    LBlackimage = Image.new('1', (epd.width, epd.height), 255)
    LRYimage = Image.new('1', (epd.width, epd.height), 255)
    drawblack = ImageDraw.Draw(LBlackimage)
    drawry = ImageDraw.Draw(LRYimage)

    drawblack.text((2, 0), 'hello world', font=font18, fill=0)
    drawblack.text((2, 20), '2.13 epd b V4', font=font18, fill=0)
    drawblack.text((20, 50), u'微雪电子', font=font18, fill=0)
    drawblack.line((10, 90, 60, 140), fill=0)
    drawblack.line((60, 90, 10, 140), fill=0)
    drawblack.rectangle((10, 90, 60, 140), outline=0)
    drawry.rectangle((10, 150, 60, 200), fill=0)
    drawry.arc((15, 95, 55, 135), 0, 360, fill=0)
    drawry.chord((15, 155, 55, 195), 0, 360, fill=1)

    epd.display(epd.getbuffer(LBlackimage), epd.getbuffer(LRYimage))
    time.sleep(2)

    # Read BMP full frame
    logging.info("3. Display full-frame BMP")
    bmp_path = os.path.join(PIC_DIR, '464x46_Frame.png')  # Supply this image
    Blackimage = Image.open(bmp_path)
    RYimage = Image.open(bmp_path)
    epd.display(epd.getbuffer(Blackimage), epd.getbuffer(RYimage))
    time.sleep(2)

    # BMP in corner
    logging.info("4. Display windowed BMP")
    blackimage1 = Image.new('1', (epd.height, epd.width), 255)
    redimage1 = Image.new('1', (epd.height, epd.width), 255)
    sub_bmp_path = os.path.join(PIC_DIR, '250x122_Geometric_Pattern.png')  # Must exist
    newimage = Image.open(sub_bmp_path)
    blackimage1.paste(newimage, (0, 0))
    epd.display(epd.getbuffer(blackimage1), epd.getbuffer(redimage1))

    logging.info("Clearing...")
    epd.init()
    epd.Clear()

    logging.info("Sleeping...")
    epd.sleep()

except IOError as e:
    logging.error(f"I/O error: {e}")

except KeyboardInterrupt:
    logging.info("Interrupted — cleaning up")
    epd2in13b_V4.epdconfig.module_exit(cleanup=True)
    sys.exit()

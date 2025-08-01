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

def load_image_safe(path, target_size=(122, 250)):
    img = Image.open(path).convert('1')

    # If dimensions are flipped, auto-rotate
    if img.size == (target_size[1], target_size[0]):
        logging.info(f"Rotating image {path} from {img.size} to {target_size}")
        img = img.rotate(90, expand=True)

    # If still not the correct size, resize
    if img.size != target_size:
        logging.warning(f"Resizing image {path} from {img.size} to {target_size}")
        img = img.resize(target_size)

    return img


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

    drawblack.text((10, 0), 'Mostly', font=font20, fill=0)
    drawblack.text((10, 20), 'Functional', font=font20, fill=0)
    drawblack.text((120, 0), 'Engineering', font=font20, fill=0)
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

    drawblack.text((2, 0), 'Mostly', font=font18, fill=0)
    drawblack.text((2, 20), 'Functional', font=font18, fill=0)
    drawblack.text((20, 50), 'Engineering', font=font18, fill=0)
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
    bmp_path = os.path.join(PIC_DIR, '')
    img = load_image_safe(os.path.join(PIC_DIR, '250x122_Geometric_Pattern.png'))
    epd.display(epd.getbuffer(img), epd.getbuffer(img))
    time.sleep(2)

    # BMP in corner
    logging.info("4. Display windowed BMP")
    blackimage1 = Image.new('1', (epd.height, epd.width), 255)
    redimage1 = Image.new('1', (epd.height, epd.width), 255)
    corner_img = load_image_safe(os.path.join(PIC_DIR, '46x46_Frame.png'))
    # Make sure it fits (optionally scale smaller)
    if corner_img.size[0] > epd.height or corner_img.size[1] > epd.width:
        logging.warning("Corner image too large, scaling down to fit")
        corner_img.thumbnail((epd.height, epd.width))

    black = Image.new('1', (epd.height, epd.width), 255)
    black.paste(corner_img, (0, 0))  # You could center it too if needed
    epd.display(epd.getbuffer(black), epd.getbuffer(Image.new('1', (epd.height, epd.width), 255)))

    logging.info("Clearing...")
    #epd.init()
    epd.Clear()

    logging.info("Sleeping...")
    epd.sleep()

except IOError as e:
    logging.error(f"I/O error: {e}")

except KeyboardInterrupt:
    logging.info("Interrupted — cleaning up")
    epd2in13b_V4.epdconfig.module_exit(cleanup=True)
    sys.exit()

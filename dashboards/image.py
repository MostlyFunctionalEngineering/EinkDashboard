from PIL import Image, ImageOps
import os
import logging

logger = logging.getLogger(__name__)

def render(epd, config, flip_screen=False):
    logger.debug("Rendering image dashboard")

    try:
        height, width = epd.height, epd.width
        cfg = config.get('image', {})
        img_path = cfg.get('path')

        if not img_path or not os.path.exists(img_path):
            logger.error(f"No valid image path: {img_path}")
            return

        # Load and convert
        img = Image.open(img_path).convert('L')
        img = img.resize((height, width))  # match display buffer

        # Optional invert
        invert = cfg.get('invert_colors', False)
        if invert:
            img = ImageOps.invert(img)

        # Canvas
        black_img = Image.new('1', (height, width), 255)
        black_img.paste(img)

        if flip_screen:
            black_img = black_img.rotate(180)

        epd.display_fast(epd.getbuffer(black_img))
        logger.info(f"Image displayed: {img_path}")

    except Exception as e:
        logger.exception(f"Image dashboard failed: {e}")
